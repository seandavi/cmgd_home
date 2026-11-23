"""Build subject_observations.tsv: one row per (subject, timepoint, field) value.

Usage: python -I scripts/longitudinal_neuro/build_observations.py data/longitudinal-neuro [extra.tsv ...]
- Outcome attributes that live in BioSample (GAINS) come from biosample_attributes.tsv.gz.
- Extra tables (same columns, from supplements/deposits) are appended.
Rows whose license allows redistribution go to <dir>/subject_observations.tsv.gz (committed);
the rest go to <dir>/local/subject_observations.tsv.gz (gitignored), so this public repo
never republishes data under NC/ND/unknown terms.
"""
import csv
import gzip
import sys
from collections import defaultdict
from pathlib import Path

COLS = ["study_key", "subject", "source_subject_id", "biosample", "visit", "days_from_baseline",
        "age_days", "field", "value", "unit", "source_url", "source_file", "source_sha256",
        "source_location", "license"]
# Exact first token, so CC-BY-NC-ND-4.0 never passes as CC-BY.
OPEN = {"CC0", "CC0-1.0", "CC-BY-4.0", "CC-BY-3.0", "MIT", "INSDC"}


def is_open(lic: str) -> bool:
    return (lic.split() or [""])[0] in OPEN


assert is_open("MIT (LICENSE.txt in repo)") and not is_open("CC-BY-NC-ND-4.0") and not is_open("unknown")

# Per-specimen outcome attributes that a study deposits in BioSample.
BIOSAMPLE_FIELDS = {"gains": ["cohort_subset", "age", "male", "polypharm5", "ADAS.COG.13",
                              "Memory_sum_Z", "EF_sum_Z"]}


def from_biosample(d: Path) -> list[dict]:
    attrs = defaultdict(dict)
    for r in csv.DictReader(gzip.open(d / "biosample_attributes.tsv.gz", "rt"), delimiter="\t"):
        attrs[r["biosample"]][r["attribute"]] = r["value"]
    out = []
    for s in csv.DictReader(open(d / "specimens.tsv"), delimiter="\t"):
        for field in BIOSAMPLE_FIELDS.get(s["study_key"], []):
            v = attrs[s["biosample"]].get(field, "")
            if v and v.lower() not in ("not applicable", "missing", "na"):
                out.append(dict(study_key=s["study_key"], subject=s["subject"],
                                source_subject_id=s["subject"], biosample=s["biosample"],
                                visit=s["visit"], days_from_baseline=s["days_from_baseline"],
                                age_days="", field=field, value=v, unit="",
                                source_url=f"https://www.ncbi.nlm.nih.gov/biosample/{s['biosample']}",
                                source_file="biosample_attributes.tsv.gz", source_sha256="",
                                source_location=f"BioSample attribute {field}", license="INSDC"))
    return out


def main(d: Path, extras: list[Path]) -> None:
    rows = from_biosample(d)
    for p in extras:
        rows += [{c: r.get(c, "") for c in COLS} for r in csv.DictReader(open(p), delimiter="\t")]
    keep = [r for r in rows if is_open(r["license"])]
    local = [r for r in rows if not is_open(r["license"])]
    for path, data in ((d / "subject_observations.tsv.gz", keep), (d / "local/subject_observations.tsv.gz", local)):
        path.parent.mkdir(exist_ok=True)
        with gzip.open(path, "wt", newline="") as f:
            w = csv.DictWriter(f, fieldnames=COLS, delimiter="\t", lineterminator="\n")
            w.writeheader()
            w.writerows(data)
    print(f"public: {len(keep)} rows; local only: {len(local)} rows", file=sys.stderr)


if __name__ == "__main__":
    main(Path(sys.argv[1]), [Path(p) for p in sys.argv[2:]])
