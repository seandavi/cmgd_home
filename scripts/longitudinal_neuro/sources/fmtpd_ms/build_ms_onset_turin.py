"""Convert Maglione 2026 Supplementary Table S1 (mmc2.xlsx) to long subject_observations rows.

usage: python -I build_ms_onset_turin.py <mmc2.xlsx> <specimens.tsv> <biosample_attributes.tsv.gz> <out.tsv>
"""
import csv, datetime, gzip, hashlib, sys
import openpyxl

xlsx, specimens, attrs, out = sys.argv[1:5]
STUDY = "ms_onset_turin"
URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC13688122/supplementaryFiles (mmc2.xlsx in zip)"
SRC = "raw/epmc_PMC13688122/x/mmc2.xlsx"
LICENSE = "CC-BY-NC-ND-4.0"
SHA = hashlib.sha256(open(xlsx, "rb").read()).hexdigest()

# ponytail: timepoint per column is our reading of the Methods (onset vs 12-month follow-up); see notes.md
ONSET = {"naive", "age", "bmi", "gc_treatment", "lesion_burden", "spinal_cord_lesion",
         "subtentorial_lesions", "gadolinium_contrast", "clinical_presentation", "EDSS_DIAGNOSI"}
FOLLOWUP = {"EDSS_PROGRESSIONE", "WORSENING", "Event", "EventTime"}
SAMPLE_LEVEL = {"sequencing_batch", "sample_collection_date"}
CONSTANT = {"category", "sex"}

ours = {}  # subject -> biosample (one specimen per subject in this study)
with open(specimens) as f:
    for r in csv.DictReader(f, delimiter="\t"):
        if r["study_key"] == STUDY:
            assert r["subject"] not in ours, r["subject"]
            ours[r["subject"]] = r["biosample"]

ncbi_date = {}
with gzip.open(attrs, "rt") as f:
    for line in f:
        s, b, a, _, v = line.rstrip("\n").split("\t")
        if s == STUDY and a == "collection_date":
            ncbi_date[b] = v

ws = openpyxl.load_workbook(xlsx, read_only=True).worksheets[0]
rows = list(ws.iter_rows(values_only=True))
header = rows[0]
assert header[0] == "id" and len(header) == 19, header


def fmt(v):
    if isinstance(v, datetime.datetime):
        return v.date().isoformat()
    return str(v)


cols = ["study_key", "subject", "source_subject_id", "biosample", "visit", "days_from_baseline",
        "age_days", "field", "value", "unit", "source_url", "source_file", "source_sha256",
        "source_location", "license"]
seen, mismatched = set(), []
with open(out, "w", newline="") as f:
    w = csv.writer(f, delimiter="\t", lineterminator="\n")
    w.writerow(cols)
    for r in rows[1:]:
        sid = r[0]
        if sid is None:
            continue
        rec = dict(zip(header, r))
        subj = sid if sid in ours else ""
        seen.add(subj)
        age = rec["age"]
        for j, field in enumerate(header[1:], start=1):
            v = r[j]
            if v is None:  # empty cell (only in NEG row); "NA" strings are kept verbatim
                continue
            if field in ONSET:
                # healthy donors and NEG/POS controls have no disease onset; their only timepoint is the stool sample
                visit = "onset" if rec["category"] == "MS" else "stool_sample"
            elif field in FOLLOWUP:
                visit = "12mo_followup"
            elif field in SAMPLE_LEVEL:
                visit = "stool_sample"
            else:
                assert field in CONSTANT, field
                visit = ""
            age_days = ""
            if visit in ("onset", "stool_sample") and isinstance(age, (int, float)):
                age_days = str(round(age * 365.25))
            unit = {"age": "years", "bmi": "kg/m2"}.get(field, "")
            bios = ours.get(subj, "") if field in SAMPLE_LEVEL else ""
            w.writerow([STUDY, subj, sid, bios, visit, "", age_days, field, fmt(v), unit, URL, SRC,
                        SHA, f"Foglio1!{openpyxl.utils.get_column_letter(j + 1)} ({field})", LICENSE])
        if subj and isinstance(rec["sample_collection_date"], datetime.datetime):
            nd = ncbi_date.get(ours[subj], "")
            if nd != rec["sample_collection_date"].date().isoformat():
                mismatched.append((sid, fmt(rec["sample_collection_date"]), nd))

missing = sorted(set(ours) - seen)
print("mapped subjects:", len(seen - {""}), "of ours", len(ours), "missing:", missing)
print("collection_date mismatches (S1 vs BioSample):", len(mismatched))
for m in mismatched:
    print("  ", *m)
