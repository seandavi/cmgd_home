"""Fetch WGS runs per BioProject from ENA and compute one readset per BioSample.

Usage: python -I scripts/longitudinal_neuro/fetch_runs.py data/longitudinal-neuro
Reads <dir>/studies.tsv; writes <dir>/runs.tsv and <dir>/readsets.tsv.
Readset ids come from ../nextflow_telemetry (ADR-0007), checked against its golden vectors.
"""
import csv
import importlib.util
import io
import sys
import time
import urllib.parse
import urllib.request
from collections import defaultdict
from pathlib import Path

HOME = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location(
    "readset", HOME.parent / "nextflow_telemetry/src/nextflow_telemetry/readset.py")
readset = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(readset)
assert readset.readset_id(["insdc.sra:SRR000001"]) == "RS.29BkNp8wxCWwuhVe3luQxYtv97BwdwjF"
assert readset.readset_id(["insdc.sra:SRR1", "insdc.sra:ERR2", "insdc.sra:DRR3"]) == "RS.uFRI93utvCk3llTO2fQPqARuz-e6Lj_-"

FIELDS = ("run_accession,experiment_accession,sample_accession,secondary_sample_accession,"
          "study_accession,secondary_study_accession,library_strategy,library_source,"
          "library_layout,instrument_model,read_count,base_count,sample_alias,sample_title,"
          "run_alias,first_public")


def ena_runs(project: str) -> list[dict]:
    q = urllib.parse.urlencode({"accession": project, "result": "read_run",
                                "fields": FIELDS, "format": "tsv", "limit": 0})
    for attempt in range(5):
        try:
            with urllib.request.urlopen(f"https://www.ebi.ac.uk/ena/portal/api/filereport?{q}", timeout=120) as r:
                return list(csv.DictReader(io.StringIO(r.read().decode()), delimiter="\t"))
        except OSError:
            time.sleep(5 * (attempt + 1))
    raise SystemExit(f"ENA failed for {project}")


def main(out: Path) -> None:
    studies = list(csv.DictReader(open(out / "studies.tsv"), delimiter="\t"))
    runs, readsets = [], []
    for s in studies:
        rows = [r for r in ena_runs(s["bioproject"]) if r["library_strategy"] == "WGS"]
        by_sample = defaultdict(list)
        for r in rows:
            r = {"study_key": s["study_key"], "bioproject": s["bioproject"], **r}
            runs.append(r)
            by_sample[r["sample_accession"]].append(r["run_accession"])
        # ponytail: one readset = all WGS runs of a BioSample; curated run subsets would override this
        for biosample, rs in sorted(by_sample.items()):
            readsets.append({"study_key": s["study_key"], "biosample": biosample,
                             "readset_id": readset.readset_id("insdc.sra:" + x for x in rs),
                             "n_runs": len(rs), "runs": ";".join(sorted(set(rs)))})
        print(f"{s['study_key']}: {len(rows)} WGS runs, {len(by_sample)} biosamples", file=sys.stderr)
    for name, data in (("runs.tsv", runs), ("readsets.tsv", readsets)):
        with open(out / name, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(data[0]), delimiter="\t", lineterminator="\n")
            w.writeheader()
            w.writerows(data)


if __name__ == "__main__":
    main(Path(sys.argv[1]))
