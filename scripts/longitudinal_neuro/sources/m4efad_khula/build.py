"""Build subject_observations.tsv for m4efad + khula.

usage: python -I build.py <group_dir> <specimens.tsv>
"""
import csv, hashlib, sys, collections
from pathlib import Path
import openpyxl

G = Path(sys.argv[1])
SPEC = sys.argv[2]
RAW = G / "raw"
COLS = ["study_key", "subject", "source_subject_id", "biosample", "visit", "days_from_baseline",
        "age_days", "field", "value", "unit", "source_url", "source_file", "source_sha256",
        "source_location", "license"]


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def tsv(p):
    with open(p, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f, delimiter="\t"))


spec = [r for r in tsv(SPEC) if r["study_key"] in ("m4efad", "khula")]
by_bs = {r["biosample"]: r for r in spec}
m4_subjects = {r["subject"] for r in spec if r["study_key"] == "m4efad"}
m4_by_name = {r["specimen_name"]: r for r in spec if r["study_key"] == "m4efad"}
out = []


def emit(**kw):
    row = {c: "" for c in COLS}
    row.update({k: ("" if v is None else str(v)) for k, v in kw.items()})
    out.append(row)


# ---- m4efad: figshare per-subject tables -------------------------------------------------
FIG_FILES = {  # file id, visit, units per column
    "meta.tsv": ("51155876", "", {}),
    "anthro.tsv": ("51155849", "enrolment", {"Weight": "kg", "MUAC": "cm", "HC": "cm", "WLZ_WHZ": "z-score"}),
    "bayley.tsv": ("51155852", "enrolment", {}),
    "wolkes.tsv": ("51155843", "enrolment", {}),
    "psd.tsv": ("51155846", "enrolment", None),  # None: every column is log10 PSD
}
for name, (fid, visit, units) in FIG_FILES.items():
    p = RAW / "figshare_m4efad" / name
    h = sha(p)
    for r in tsv(p):
        sid = r["ID"]
        for field, value in r.items():
            if field == "ID" or value == "":
                continue
            emit(study_key="m4efad", subject=sid if sid in m4_subjects else "", source_subject_id=sid,
                 visit=visit, field=field, value=value,
                 unit="log10(uV^2/Hz)" if units is None else units.get(field, ""),
                 source_url=f"https://ndownloader.figshare.com/files/{fid}",
                 source_file=str(p.relative_to(G)), source_sha256=h,
                 source_location=f"{name}:{field}", license="CC-BY-4.0")

# ---- khula paper source data (MOESM5): per-sample age for Khula and M4EFaD -----------------
X = RAW / "europepmc_khula" / "41467_2025_56072_MOESM5_ESM.xlsx"
XH = sha(X)
XURL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11733223/supplementaryFiles"
XLIC = "CC-BY-NC-ND-4.0 (article license)"
wb = openpyxl.load_workbook(X, read_only=True, data_only=True)


def sheet(name):
    rows = list(wb[name].iter_rows(values_only=True))
    hi = next(i for i, r in enumerate(rows) if r and "sample" in r)
    h = rows[hi]
    return [dict(zip(h, r)) for r in rows[hi + 1:] if r and r[0] is not None]


fig2a = {(r["datasource"], r["sample"]): r for r in sheet("Figure2A")}
fig1b = sheet("Figure1B")

# Khula: SEQ library name -> BioSample (ENA filereport), BioSample -> our subject (specimens.tsv)
ena = tsv(RAW / "ena_khula" / "filereport.tsv")
seq2bs = {r["library_name"]: r["sample_accession"] for r in ena}
assert len(seq2bs) == len(ena), "duplicate library_name in ENA khula"

khula_rows = [r for r in fig1b if r["datasource"] == "1kDLEAP-KHULA"]
# source subject id -> our subject, only from samples whose BioSample already has a subject
k2ours = collections.defaultdict(set)
for r in khula_rows:
    bs = seq2bs.get(r["sample"])
    if bs and by_bs.get(bs, {}).get("subject"):
        k2ours[r["subject_id"]].add(by_bs[bs]["subject"])
# Ambiguous links stay unmapped: a source id landing on >1 of our subjects, or one of our
# subjects reached from >1 source id.
ours2k = collections.defaultdict(set)
for k, v in k2ours.items():
    for o in v:
        ours2k[o].add(k)
conflicts = {k for k, v in k2ours.items() if len(v) > 1}
conflicts |= set().union(*(v for v in ours2k.values() if len(v) > 1))
print("khula id conflicts:", {k: sorted(k2ours[k]) for k in sorted(conflicts)}, file=sys.stderr)
for k in conflicts:
    del k2ours[k]

stats = collections.Counter()
for r in khula_rows:
    f2 = fig2a.get(("1kDLEAP-KHULA", r["sample"]))
    if f2:
        assert abs(f2["ageMonths"] - r["ageMonths"]) < 1e-9 and f2["subject_id"] == r["subject_id"]
    bs = seq2bs.get(r["sample"], "")
    sp = by_bs.get(bs)
    subj = next(iter(k2ours[r["subject_id"]])) if r["subject_id"] in k2ours else ""
    assert not (subj and sp and sp["subject"]) or subj == sp["subject"]
    if r["subject_id"] in conflicts:
        stats["conflict_unmapped"] += 1
    if subj and not (sp and sp["subject"]):
        subj = next(iter(k2ours[r["subject_id"]]))
        stats["subject_from_sibling_sample"] += 1
    visit = f2["visit"] if f2 else ""
    if sp and visit and sp["visit"] and sp["visit"] != visit:
        stats["visit_mismatch"] += 1
    stats["bs_found" if sp else "bs_missing"] += 1
    emit(study_key="khula", subject=subj, source_subject_id=r["subject_id"], biosample=bs,
         visit=visit, age_days=round(r["ageMonths"] * 30.4375, 1), field="ageMonths",
         value=repr(r["ageMonths"]), unit="months", source_url=XURL,
         source_file=str(X.relative_to(G)), source_sha256=XH,
         source_location="Figure1B:ageMonths (sample=%s; visit from Figure2A)" % r["sample"],
         license=XLIC)

# M4EFaD rows in the same sheet: sample = our specimen_name (C###), subject_id = m4efad-<LCC id>
for r in (r for r in fig1b if r["datasource"] == "1kDLEAP-M4EFAD"):
    f2 = fig2a.get(("1kDLEAP-M4EFAD", r["sample"]))
    sp = m4_by_name.get(r["sample"])
    sid = r["subject_id"]
    lcc = sid.removeprefix("m4efad-")
    ok = sp is not None and sp["subject"] == lcc
    stats["m4_ok" if ok else "m4_unmatched"] += 1
    # the source divided days by 30.5 (MicrobiomeAgeModel2024 notebook), so invert with 30.5
    days = r["ageMonths"] * 30.5
    assert abs(days - round(days)) < 1e-6, (r, days)
    emit(study_key="m4efad", subject=lcc if ok else "", source_subject_id=sid,
         biosample=sp["biosample"] if ok else "", visit=f2["visit"] if f2 else "",
         age_days=round(days), field="ageMonths", value=repr(r["ageMonths"]), unit="months",
         source_url=XURL, source_file=str(X.relative_to(G)), source_sha256=XH,
         source_location="Figure1B:ageMonths (sample=%s; visit from Figure2A)" % r["sample"],
         license=XLIC)

with open(G / "subject_observations.tsv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, COLS, delimiter="\t", lineterminator="\n")
    w.writeheader()
    w.writerows(out)
print(len(out), "rows;", dict(stats), file=sys.stderr)
