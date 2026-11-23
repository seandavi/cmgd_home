"""Build elabe/subject_observations.tsv from Lee 2026 Table S1 and Warner 2023 Supp Data 2.

usage: python3 -I build.py <elabe_dir> <runs.tsv> <specimens.tsv>
Join key: SRA run accession in the supplement -> runs.tsv sample_accession -> specimens.tsv biosample.
"""
import sys, site, csv, hashlib, collections, re
sys.path.append(site.getusersitepackages())
import openpyxl
from openpyxl.utils import get_column_letter

base, runs_tsv, specs_tsv = sys.argv[1:4]
MISSING = {None, "", "-", " "}
MONTH = 30.4375

runs = {r["run_accession"]: r for r in csv.DictReader(open(runs_tsv), delimiter="\t") if r["study_key"] == "elabe"}
specs = {r["biosample"]: r for r in csv.DictReader(open(specs_tsv), delimiter="\t") if r["study_key"] == "elabe"}
subject_by_dyad_role = {(r["family_id"], r["role"]): r["subject"] for r in specs.values() if r["role"] and r["subject"]}

COLS = ["study_key", "subject", "source_subject_id", "biosample", "visit", "days_from_baseline", "age_days",
        "field", "value", "unit", "source_url", "source_file", "source_sha256", "source_location", "license"]
out = []


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def fmt(v):
    return str(v).strip() if not isinstance(v, str) else v


def emit(src, **kw):
    row = dict.fromkeys(COLS, "")
    row.update(study_key="elabe", **src)
    row.update({k: ("" if v is None else str(v)) for k, v in kw.items()})
    out.append(row)


def collapse(samples, emit_fn):
    """samples: list of (subject_key, biosample, value). Emit one row per subject if the value is
    constant within the subject, else one row per sample (biosample filled)."""
    by = collections.defaultdict(list)
    for k, b, v in samples:
        by[k].append((b, v))
    n_incons = 0
    for k, lst in by.items():
        vals = {v for _, v in lst}
        if len(vals) == 1:
            emit_fn(k, "", lst[0][1])
        else:
            n_incons += 1
            for b, v in lst:
                emit_fn(k, b, v)
    return n_incons


# ---------------- Lee 2026 eBioMedicine, Supplementary Table S1 ----------------
lee_file = "raw/epmc_PMC13718489/mmc2.xlsx"
lee_src = dict(source_url="https://www.ebi.ac.uk/europepmc/webservices/rest/PMC13718489/supplementaryFiles (mmc2.xlsx in zip)",
               source_file=lee_file, source_sha256=sha(f"{base}/{lee_file}"), license="CC-BY-NC-ND-4.0")
ws = openpyxl.load_workbook(f"{base}/{lee_file}", read_only=True)["Supp Table 1"]
allrows = list(ws.iter_rows(values_only=True, max_col=53))
names = allrows[3]
sub = [None] * len(names)
for start, end in [(7, 10), (11, 14), (26, 29), (30, 38), (39, 47), (48, 51)]:
    assert allrows[2][start], start
    for j in range(start, end + 1):
        sub[j] = allrows[2][start]
assert names[1] == "Sample ID" and names[2].startswith("SRA accessions") and names[5] == "Assigned time points"
data = [r for r in allrows[5:] if r[1]]
assert len(data) == 905

UNITS = {"Actual timepoint (months)": "months", "Gestational age (weeks)": "weeks", "Birth weight (g)": "g",
         "Maternal age at birth": "years"}
SUB_UNITS = {"Bayley-III composite score": "composite score", "Infant–Toddler Social and Emotional Assessment (ITSEA) T-score": "T-score",
             "Preschool Age Psychiatric Assessment (PAPA)": "symptom count"}
SAMPLE_COLS = [1, 4, 5, 25, 26, 27, 28, 29]
SUBJECT_COLS = list(range(7, 22)) + [23, 24] + list(range(30, 52))


def field_of(j):
    return f"{sub[j]} | {names[j]}" if sub[j] else names[j]


def loc(j):
    return f"Supp Table 1, column {get_column_letter(j + 1)} ({' > '.join(x for x in (allrows[1][j], sub[j], names[j]) if x) if j else names[j]})"


def visit_of(name):
    m = re.search(r"(\d+) MOL$", name)
    if m:
        return f"{m.group(1)} MOL", round(int(m.group(1)) * MONTH, 2)
    m = re.match(r"(Prenatal|Y\d) SD$", name) or re.match(r"INR at (\S+ trimester)$", name)
    return (m.group(1), "") if m else ("", "")


lee_bs = []
for r in data:
    b = runs[r[2]]["sample_accession"]  # KeyError here = run missing from runs.tsv
    lee_bs.append((r, b, specs[b]))

# dyads holding more than one child in S1 (two distinct children share a BioSample dyad id),
# detected on fixed child/mother identity columns: sex, GA, birth weight, prenatal SD, race, maternal age
IDENTITY_COLS = [24, 21, 23, 7, 16, 17]
profiles = collections.defaultdict(set)
for r, b, s in lee_bs:
    profiles[s["family_id"]].add(tuple(r[j] for j in IDENTITY_COLS))
collision = {f for f, p in profiles.items() if len(p) > 1}
lee_subject = {}
for r, b, s in lee_bs:
    if s["family_id"] not in collision and s["subject"]:
        lee_subject.setdefault(s["family_id"], set()).add(s["subject"])
assert all(len(v) == 1 for v in lee_subject.values())

for r, b, s in lee_bs:
    visit = r[5]
    age = round(r[4] * MONTH, 1)
    for j in SAMPLE_COLS:
        if r[j] in MISSING:
            continue
        emit(lee_src, subject=s["subject"], source_subject_id=f"{s['family_id']}|Child", biosample=b, visit=visit,
             age_days=age, field=field_of(j), value=fmt(r[j]), unit=UNITS.get(names[j], ""), source_location=loc(j))

lee_incons = 0
for j in SUBJECT_COLS:
    vis, age = visit_of(names[j])

    def emit_subj(fam, b, v, j=j, vis=vis, age=age):
        subj = specs[b]["subject"] if b else next(iter(lee_subject.get(fam, {""})))
        emit(lee_src, subject=subj, source_subject_id=f"{fam}|Child", biosample=b, visit=vis, age_days=age,
             field=field_of(j), value=fmt(v), unit=UNITS.get(names[j], SUB_UNITS.get(sub[j], "")), source_location=loc(j))

    samples = []
    for r, b, s in lee_bs:
        if r[j] in MISSING:
            continue
        # collision dyads: key by biosample so values never merge across the two children
        key = s["family_id"]
        samples.append((key if key not in collision else f"{key}#{b}", b, r[j]))
    by_key = collections.defaultdict(list)
    for k, b, v in samples:
        by_key[k].append((b, v))
    for k, lst in by_key.items():
        fam = k.split("#")[0]
        if "#" in k:
            emit_subj(fam, lst[0][0], lst[0][1])
        elif len({v for _, v in lst}) == 1:
            emit_subj(fam, "", lst[0][1])
        else:
            lee_incons += 1
            for b, v in lst:
                emit_subj(fam, b, v)
n_lee = len(out)

# ---------------- Warner 2023 Nat Commun, Supplementary Data 2 ----------------
w_file = "raw/epmc_PMC10509221/41467_2023_41421_MOESM5_ESM.xlsx"
w_src = dict(source_url="https://www.ebi.ac.uk/europepmc/webservices/rest/PMC10509221/supplementaryFiles (41467_2023_41421_MOESM5_ESM.xlsx in zip)",
             source_file=w_file, source_sha256=sha(f"{base}/{w_file}"), license="CC-BY-4.0")
ws = openpyxl.load_workbook(f"{base}/{w_file}", read_only=True)["Supp Table 2 all data"]
wrows = list(ws.iter_rows(values_only=True, max_col=13))
wn = wrows[5]
assert wn[1] == "Sample ID" and wn[2] == "Mother / Child" and wn[5] == "Dyad ID" and wrows[6][7] == "WMS accession"
wdata = [r for r in wrows[8:] if r[1]]
WSUB = {8: "Antibiotic exposure", 9: "Antibiotic exposure", 10: "Maternal metadata used in analysis",
        11: "Maternal metadata used in analysis", 12: "Maternal metadata used in analysis"}
for j, g in WSUB.items():
    assert wrows[4][8 if j < 10 else 10] == g


def wfield(j):
    return f"{WSUB[j]} | {wn[j]}" if j in WSUB else wn[j]


def wloc(j):
    return f"Supp Table 2 all data, column {get_column_letter(j + 1)} ({' > '.join(x for x in (WSUB.get(j), wn[j]) if x)})"


def age_days_of(v):
    m = re.fullmatch(r"([\d.]+) years", str(v))
    return round(float(m.group(1)) * 365.25, 1) if m else ""  # ponytail: child "weeks" ages left blank (see notes.md)


w_samples = collections.defaultdict(list)
w_mapped_bs = 0
for r in wdata:
    sid = f"{r[5]}|{r[2]}"
    subj = subject_by_dyad_role.get((str(r[5]), r[2].lower()), "")
    b = runs[r[7]]["sample_accession"] if r[7] in runs else ""
    if b:
        w_mapped_bs += 1
        assert specs[b]["subject"] == subj, (r[1], b)
        for j in (1, 4, 8, 9):
            if r[j] in MISSING:
                continue
            emit(w_src, subject=subj, source_subject_id=sid, biosample=b, age_days=age_days_of(r[4]) if j == 4 else "",
                 field=wfield(j), value=fmt(r[j]), source_location=wloc(j))
    if subj:
        for j in (3, 10, 11, 12):
            if r[j] not in MISSING:
                w_samples[j].append((sid, b, r[j]))

w_incons = 0
for j, samples in w_samples.items():
    def emit_w(sid, b, v, j=j):
        emit(w_src, subject=subject_by_dyad_role[(sid.split("|")[0], sid.split("|")[1].lower())], source_subject_id=sid,
             biosample=b, field=wfield(j), value=fmt(v), source_location=wloc(j))
    w_incons += collapse(samples, emit_w)

with open(f"{base}/subject_observations.tsv", "w", newline="", encoding="utf-8") as fh:
    wr = csv.DictWriter(fh, COLS, delimiter="\t", lineterminator="\n")
    wr.writeheader()
    wr.writerows(out)

# ---- report ----
lee = out[:n_lee]
print("lee rows", n_lee, "inconsistent subject-level fields", lee_incons, "collision dyads", sorted(collision, key=int))
print("lee subject-keys", len({(r["source_subject_id"], r["biosample"]) for r in lee if not r["biosample"]} ),
      "lee mapped subjects", len({r["subject"] for r in lee if r["subject"]}))
print("lee biosamples mapped", len({b for _, b, _ in lee_bs}), "with specimens subject", sum(1 for _, _, s in lee_bs if s["subject"]))
wo = out[n_lee:]
print("warner rows", len(wo), "S2 rows", len(wdata), "mapped to our biosample", w_mapped_bs, "inconsistent", w_incons,
      "subjects mapped", len({r["subject"] for r in wo if r["subject"]}))
print("fields:", collections.Counter(r["field"] for r in out).most_common())
