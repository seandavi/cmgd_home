"""Fetch every BioSample in readsets.tsv from NCBI and write all attributes, long format.

Usage: python -I scripts/longitudinal_neuro/fetch_biosamples.py data/longitudinal-neuro
Writes <dir>/biosample_attributes.tsv.gz: study_key, biosample, attribute, harmonized_name, value.
Title, description and sample-name ids are included as `_title`, `_description`, `_id:<db>`
because several studies encode subject and visit there instead of in attributes.
"""
import csv
import gzip
import json
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

EFETCH = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"


def efetch(accs: list[str]) -> ET.Element:
    data = urllib.parse.urlencode({"db": "biosample", "id": ",".join(accs), "retmode": "xml"}).encode()
    for attempt in range(6):
        try:
            with urllib.request.urlopen(EFETCH, data=data, timeout=180) as r:
                return ET.fromstring(r.read())
        except (OSError, ET.ParseError):
            time.sleep(5 * (attempt + 1))
    raise SystemExit(f"efetch failed at {accs[0]}")


def rows(bs: ET.Element):
    acc = bs.get("accession")
    yield acc, "_title", "", (bs.findtext("Description/Title") or "").strip()
    yield acc, "_description", "", " ".join((bs.findtext("Description/Comment/Paragraph") or "").split())
    for i in bs.findall("Ids/Id"):
        if i.get("db") != "BioSample":
            yield acc, f"_id:{i.get('db') or i.get('db_label') or 'other'}", "", (i.text or "").strip()
    for a in bs.findall("Attributes/Attribute"):
        yield acc, a.get("attribute_name"), a.get("harmonized_name") or "", (a.text or "").strip()


def ebi_rows(acc: str):
    """EBI BioSamples fallback for SAMEA accessions NCBI doesn't return."""
    for attempt in range(5):
        try:
            with urllib.request.urlopen(f"https://www.ebi.ac.uk/biosamples/samples/{acc}", timeout=60) as r:
                d = json.load(r)
            break
        except OSError:
            time.sleep(3 * (attempt + 1))
    else:
        raise SystemExit(f"EBI BioSamples failed at {acc}")
    yield acc, "_title", "", d.get("name") or ""
    for k, vs in (d.get("characteristics") or {}).items():
        for v in vs:
            yield acc, k, "", str(v.get("text", "")).strip()


def main(out: Path) -> None:
    study = {r["biosample"]: r["study_key"] for r in csv.DictReader(open(out / "readsets.tsv"), delimiter="\t")}
    accs = sorted(study)
    seen = set()
    with gzip.open(out / "biosample_attributes.tsv.gz", "wt", newline="") as f:
        w = csv.writer(f, delimiter="\t", lineterminator="\n")
        w.writerow(["study_key", "biosample", "attribute", "harmonized_name", "value"])
        for i in range(0, len(accs), 200):
            for bs in efetch(accs[i:i + 200]).iter("BioSample"):
                if bs.get("accession") not in study:
                    continue  # efetch returns unrelated records when it can't resolve an accession
                for acc, *rest in rows(bs):
                    if rest[2]:
                        w.writerow([study.get(acc, ""), acc, *rest])
                seen.add(bs.get("accession"))
            time.sleep(0.4)  # NCBI: 3 requests/s without an API key
            print(f"{min(i + 200, len(accs))}/{len(accs)}", file=sys.stderr)
        missing = sorted(set(accs) - seen)
        print(f"NCBI missed {len(missing)}; trying EBI BioSamples", file=sys.stderr)
        for acc in missing:
            for acc_, *rest in ebi_rows(acc):
                if rest[2]:
                    w.writerow([study[acc], acc_, *rest])
            time.sleep(0.1)


if __name__ == "__main__":
    main(Path(sys.argv[1]))
