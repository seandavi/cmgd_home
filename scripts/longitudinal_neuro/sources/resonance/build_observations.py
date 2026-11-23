"""Build resonance/subject_observations.tsv from the OSF (ybs32) timepoints and brain tables.

Usage: python3 -I build_observations.py <timepoints_metadata.csv> <brain_normalized.csv> <specimens.tsv> <out.tsv>
"""
import csv
import hashlib
import sys
from collections import defaultdict

TP_URL = "https://osf.io/download/pva98/"
BRAIN_URL = "https://osf.io/download/yatwr/"
TP_FILE = "raw/osf_ybs32/extracted/timepoints_metadata.csv"
BRAIN_FILE = "raw/osf_ybs32/extracted/brain_normalized.csv"
LICENSE = "CC-BY-4.0"  # OSF node ybs32 license
SUBJECT_FIELDS = ["sex", "race", "education"]  # constant per subject in source (checked below)
VISIT_FIELDS = ["ageMonths", "cogScore"]
SAMPLE_FIELDS = ["date", "sample", "sample_base", "read_depth",
                 "filter_00to120", "filter_00to06", "filter_18to120"]
COLS = ["study_key", "subject", "source_subject_id", "biosample", "visit", "days_from_baseline",
        "age_days", "field", "value", "unit", "source_url", "source_file", "source_sha256",
        "source_location", "license"]


def sha256(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def main(tp_path, brain_path, spec_path, out_path):
    spec = [r for r in csv.DictReader(open(spec_path), delimiter="\t") if r["study_key"] == "resonance"]
    our_subjects = {r["subject"] for r in spec if r["subject"]}
    biosample_by_name = {r["specimen_name"]: r["biosample"] for r in spec}
    tp = list(csv.DictReader(open(tp_path)))
    brain = list(csv.DictReader(open(brain_path)))
    tp_sha, brain_sha = sha256(tp_path), sha256(brain_path)

    def subject_for(src):
        s = "C" + str(int(src))  # source rows are all children (derive.jl isKid filter)
        return s if s in our_subjects else ""

    def row(src, visit, age, field, value, unit, url, file, sha, loc, biosample=""):
        return dict(study_key="resonance", subject=subject_for(src), source_subject_id=src,
                    biosample=biosample, visit=visit, days_from_baseline="", age_days=age,
                    field=field, value=value, unit=unit, source_url=url, source_file=file,
                    source_sha256=sha, source_location=loc, license=LICENSE)

    out, seen = [], set()

    def add(r):
        key = (r["source_subject_id"], r["visit"], r["biosample"], r["field"], r["value"], r["source_file"])
        if key not in seen:
            seen.add(key)
            out.append(r)

    per_subject = defaultdict(set)
    for t in tp:
        for f in SUBJECT_FIELDS:
            per_subject[(t["subject"], f)].add(t[f])
    assert all(len(v) == 1 for v in per_subject.values()), "subject-level field varies within subject"

    loc = "timepoints.tar.gz > timepoints_metadata.csv, column "
    for t in tp:
        src, visit = t["subject"], t["timepoint"]
        age = f"{float(t['ageMonths']) * 30.4375:.1f}" if t["ageMonths"] else ""
        for f in SUBJECT_FIELDS:
            if t[f]:
                add(row(src, "", "", f, t[f], "", TP_URL, TP_FILE, tp_sha, loc + f))
        for f in VISIT_FIELDS:
            if t[f]:
                add(row(src, visit, age, f, t[f], "months" if f == "ageMonths" else "",
                        TP_URL, TP_FILE, tp_sha, loc + f))
        bs = biosample_by_name.get(t["sample_base"], "")
        for f in SAMPLE_FIELDS:
            if t[f]:
                add(row(src, visit, age, f, t[f], "", TP_URL, TP_FILE, tp_sha, loc + f, bs))

    loc = "brain.tar.gz > brain_normalized.csv, column "
    for b in brain:
        for f, v in b.items():
            if f in ("subject", "timepoint") or v == "":
                continue
            add(row(b["subject"], b["timepoint"], "", f, v, "", BRAIN_URL, BRAIN_FILE, brain_sha, loc + f))

    with open(out_path, "w", newline="") as fh:
        w = csv.DictWriter(fh, COLS, delimiter="\t", lineterminator="\n")
        w.writeheader()
        w.writerows(out)
    print("rows", len(out))


if __name__ == "__main__":
    main(*sys.argv[1:5])
