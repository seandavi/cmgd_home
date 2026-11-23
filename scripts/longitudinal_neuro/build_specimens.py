"""Derive one row per specimen (BioSample) with subject, role and time, from biosample_attributes.

Usage: python -I scripts/longitudinal_neuro/build_specimens.py data/longitudinal-neuro
Writes <dir>/specimens.tsv. One rule per study below; `basis` says how sure each rule is:
  stated   - the value is its own BioSample attribute
  parsed   - parsed from a sample name, title or description whose pattern is unambiguous
  inferred - our reading of a code (e.g. C/P = child/parent); confirm against the paper
subject_key = <study_key>:<subject>, never global. Blank means the source doesn't say.
"""
import csv
import gzip
import re
import sys
from collections import defaultdict
from pathlib import Path

COLS = ["study_key", "biosample", "readset_id", "specimen_name", "specimen_type", "role",
        "family_id", "subject", "subject_key", "group", "visit", "days_from_baseline",
        "age_days", "collection_date", "basis"]


def m(pat, s):
    x = re.search(pat, s or "")
    return x.groups() if x else None


def gains(a):
    return dict(specimen_type="stool" if a["_id:Sample name"].endswith(("STL", "STLV2")) else "",
                subject=a["study_id"], group=a.get("cohort_subset", ""), visit=a.get("UnifiedNumber", ""),
                days_from_baseline=a.get("DaySample", ""), basis="stated")


def elabe(a):
    # Two deposits: Warner 2023 (role + "Dyad id"), Lee 2026 ("dyad_id" + expt_no, no role).
    # Lee's 836 specimens are all children: 836 + Warner's 69 child samples = Lee S1's 905.
    # Dyads 19, 30 and 166 hold two different children in S1, so they get no subject.
    # Ages come from Lee 2026 Supplementary Table S1, not BioSample.
    if "dyad_id" in a:
        fam = a["dyad_id"]
        return dict(specimen_type="stool", role="child", family_id=fam,
                    subject="" if fam in {"19", "30", "166"} else f"{fam}C", basis="inferred")
    role = a.get("Mother/Child status", "").lower()
    fam = a.get("Dyad id", "")
    return dict(specimen_type="stool", role=role, family_id=fam,
                subject=f"{fam}{role[:1].upper()}" if role else "", basis="stated")


def resonance(a):
    # subject_id is shared by a child (C...) and mother (M...): it is a family id. FG... = role unknown.
    name = a["_id:Sample name"]
    pre = re.match(r"[A-Z]+", name).group()
    role = {"C": "child", "M": "mother"}.get(pre, "")
    fam = a.get("subject_id", "")
    # FG-named BioSamples carry host_age off by up to ~10 years vs the OSF source; drop it.
    age = "" if pre == "FG" else a.get("host_age", "").replace(" days", "")
    return dict(specimen_type="stool", role=role, family_id=fam,
                subject=f"{pre}{fam}" if role else "", visit=a.get("timepoint", ""),
                age_days=age, basis="stated")


def asu_mtt(a):
    g = a.get("_description", "")
    subj, spec = m(r"^(\d+)\.(ST\d+)$", a.get("source_material_id", "")) or ("", "")
    visit = {"Autism_baseline": "baseline", "MTT_10wk": "10wk", "MTT_2yr": "2yr"}.get(g, "")
    role = "donor" if "Donor" in g else "child"
    return dict(specimen_type="stool", role=role, subject=subj,
                group={"TD": "TD"}.get(g, "ASD" if visit else g), visit=visit or spec, basis="parsed")


def haran_nh_ad(a):
    # Two title formats with different subject numbering (CH1019 vs CH1-178); kept as given.
    t = a["_title"]
    subj = m(r"^subject_(.+?)_(?:sample|specimen)_", t)
    day = m(r"_day_(\d+)$", t)
    return dict(specimen_type="stool", subject=subj[0] if subj else "",
                visit=a.get("specimen_number", "") or (m(r"_specimen_(\d+)_", t) or [""])[0],
                days_from_baseline=day[0] if day else "", basis="parsed")


def m4efad(a):
    return dict(specimen_type="stool", role="child", subject=a.get("host_subject_id", ""),
                age_days="", visit="12mo", basis="stated")


def nhbcs(a):
    # Sample names (nhbcs_<22 digits>) don't reveal subject or timepoint without the cohort key.
    return dict(specimen_type=a.get("env_medium", ""), basis="stated")


def fmt_pd_finland(a):
    t = a["_title"]
    if t.startswith("DONOR_"):
        return dict(specimen_type="stool", role="donor", subject=t.split("_")[1], basis="parsed")
    if x := m(r"^(X\d\.\d+)_DNA_((?:PRO|V)\d+)(_ab)?_", t):
        return dict(specimen_type="stool", role="patient", subject=x[0], visit=x[1] + (x[2] or ""),
                    basis="parsed")
    if x := m(r"^PD\.FMT_([A-Z]+\d+)_DYS_SC_", t):  # dysbiosis screening; id scheme differs from X#.#
        return dict(specimen_type="stool", role="patient", subject=x[0], visit="screening", basis="parsed")
    return dict(basis="parsed")


def kd(children_only):
    # P = patient (child), C = control parent: Lindefeldt 2019 has 12 patients and 11 parents,
    # matching PA/PB 12 and CA/CB 11; Dahlin 2024 supplements list PA.04 etc. as children.
    def rule(a):
        x = m(r"^([CP])([AB])\.(\d+)$", a["_title"])
        if not x:  # MO / NC: mock community and negative control
            return dict(specimen_type="control", basis="parsed")
        role = "child" if (x[0] == "P" or children_only) else "parent"
        return dict(specimen_type="stool", role=role, subject=f"{x[0]}{x[2]}",
                    visit={"A": "baseline", "B": "3mo_kd"}[x[1]], collection_date=a.get("collection date", ""),
                    basis="parsed")
    return rule


def ms_onset_turin(a):
    n = a["_id:Sample name"]
    return dict(specimen_type="stool", role="patient" if n.startswith("MS") else "healthy donor",
                subject=n, group=n[:2], visit="onset" if n.startswith("MS") else "", basis="parsed")


def khula(a):
    x = m(r"subject (\S+), timepoint (\d+)mo", a["_title"])
    return dict(specimen_type="stool", role="child", subject=x[0] if x else "",
                visit=f"{x[1]}mo" if x else "", basis="parsed")


def ferreiro(a):
    return dict(specimen_type="stool", subject=a["_id:Sample name"], basis="inferred")


RULES = {"gains": gains, "elabe": elabe, "resonance": resonance, "asu_mtt": asu_mtt,
         "haran_nh_ad": haran_nh_ad, "m4efad": m4efad, "nhbcs": nhbcs, "fmt_pd_finland": fmt_pd_finland,
         "kd_epilepsy_a": kd(False), "kd_epilepsy_b": kd(True), "ms_onset_turin": ms_onset_turin,
         "khula": khula, "ferreiro_preclinical_ad": ferreiro}


def main(d: Path) -> None:
    attrs = defaultdict(dict)
    for r in csv.DictReader(gzip.open(d / "biosample_attributes.tsv.gz", "rt"), delimiter="\t"):
        attrs[r["biosample"]].setdefault(r["attribute"], r["value"])
    out = []
    for rs in csv.DictReader(open(d / "readsets.tsv"), delimiter="\t"):
        a = attrs[rs["biosample"]]
        row = dict.fromkeys(COLS, "")
        row.update(study_key=rs["study_key"], biosample=rs["biosample"], readset_id=rs["readset_id"],
                   specimen_name=a.get("_id:Sample name") or a.get("_title", ""),
                   collection_date=a.get("collection_date", ""))
        row.update({k: v for k, v in RULES[rs["study_key"]](a).items() if v != "" or k == "basis"})
        if row["subject"]:
            row["subject_key"] = f"{row['study_key']}:{row['subject']}"
        out.append(row)
    with open(d / "specimens.tsv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLS, delimiter="\t", lineterminator="\n")
        w.writeheader()
        w.writerows(out)


if __name__ == "__main__":
    main(Path(sys.argv[1]))
