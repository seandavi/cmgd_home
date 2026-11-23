"""Build subject_observations.tsv for haran_nh_ad, kd_epilepsy_a, kd_epilepsy_b, ferreiro_preclinical_ad.

Usage: python3 -I build.py <group_dir> <specimens.tsv>

Reads raw/ sources (and work/ TSVs dumped from R serialized files by
dump_rds_sampledata.R / the Ferreiro `meta` export) and writes
<group_dir>/subject_observations.tsv. Values are copied verbatim.
"""
import csv, collections, hashlib, re, site, sys
import xml.etree.ElementTree as ET
sys.path.append(site.getusersitepackages())  # -I drops user site; openpyxl lives there
import openpyxl

G, SPECIMENS = sys.argv[1], sys.argv[2]
COLS = ["study_key", "subject", "source_subject_id", "biosample", "visit", "days_from_baseline",
        "age_days", "field", "value", "unit", "source_url", "source_file", "source_sha256",
        "source_location", "license"]
YEAR = 365.25
out = []


def sha(p):
    return hashlib.sha256(open(f"{G}/{p}", "rb").read()).hexdigest()


def emit(**kw):
    out.append({c: "" if kw.get(c) is None else str(kw.get(c)) for c in COLS})


def years_to_days(v):
    try:
        return str(round(float(v) * YEAR))
    except (TypeError, ValueError):
        return ""


spec = [r for r in csv.DictReader(open(SPECIMENS), delimiter="\t")]
by_study = collections.defaultdict(list)
for r in spec:
    by_study[r["study_key"]].append(r)

# ---------------------------------------------------------------- haran_nh_ad
HARAN_RDS = ("raw/gitlab_2020_cdad_nh_paper/2020_cdad_nh_paper-master-d21978422c3289a3ad45eafbe15ffdd533586a19/"
             "phy_mtph_prev_0.10_C_DIFFICILE_renormalized_20200401.rds")
HARAN_URL = ("https://gitlab.com/vanni-bucci/2020_cdad_nh_paper/-/raw/d21978422c3289a3ad45eafbe15ffdd533586a19/"
             "phy_mtph_prev_0.10_C_DIFFICILE_renormalized_20200401.rds")
HARAN_LIC = "unknown (no license file in GitLab repo)"
HARAN_SKIP = {"row_name", "ID.Match", "Sample.ID", "Version.2", "Version.3", "study_id", "total_reads",
              "Drop", "Only.one.sample", "remove.from.analysis"}
h_sha = sha(HARAN_RDS)
# our specimen_name -> source Sample.ID: strip "JPH" prefix and trailing V/V2 resequencing suffix
ours = {re.sub(r"V\d*$", "", re.sub(r"^JPH", "", r["specimen_name"].upper())): r for r in by_study["haran_nh_ad"]}
rows = list(csv.DictReader(open(f"{G}/work/haran/phy_mtph_sampledata.tsv"), delimiter="\t"))
by_subj = collections.defaultdict(list)
for r in rows:
    by_subj[r["study_id"].strip()].append(r)
for sid, rs in by_subj.items():
    matched = [ours[r["Sample.ID"].upper()] for r in rs if r["Sample.ID"].upper() in ours]
    our_subjects = sorted({m["subject"] for m in matched}) or [""]
    for f in rs[0]:
        if f in HARAN_SKIP:
            continue
        vals = {r[f] for r in rs}
        unit = "years" if f == "age" else ""
        if len(vals) == 1:  # subject-level constant
            v = vals.pop()
            if v == "":
                continue
            for s in our_subjects:
                emit(study_key="haran_nh_ad", subject=s, source_subject_id=sid, field=f, value=v, unit=unit,
                     age_days=years_to_days(v) if f == "age" else "", source_url=HARAN_URL,
                     source_file=HARAN_RDS, source_sha256=h_sha, license=HARAN_LIC,
                     source_location=f"sample_data (constant across {len(rs)} samples of study_id); column {f}")
        else:  # varies within subject: one row per sample
            for r in rs:
                if r[f] == "":
                    continue
                m = ours.get(r["Sample.ID"].upper())
                emit(study_key="haran_nh_ad", subject=m["subject"] if m else "", source_subject_id=sid,
                     biosample=m["biosample"] if m else "", field=f, value=r[f], unit=unit,
                     age_days=years_to_days(r[f]) if f == "age" else "", source_url=HARAN_URL,
                     source_file=HARAN_RDS, source_sha256=h_sha, license=HARAN_LIC,
                     source_location=f"sample_data row {r['row_name']} (Sample.ID {r['Sample.ID']}); column {f}")


# ------------------------------------------------------- JATS table helper (kd)
def jats_table(xml_path, label):
    root = ET.parse(f"{G}/{xml_path}").getroot()
    txt = lambda e: " ".join("".join(e.itertext()).split())
    for tw in root.iter("table-wrap"):
        lab = tw.find("label")
        if lab is not None and txt(lab) == label:
            return [[txt(c) for c in tr if c.tag in ("td", "th")] for tr in tw.iter("tr")]
    raise SystemExit(f"{label} not found in {xml_path}")


def emit_patient_table(study, xml_path, url, label, header, visit_of, age_field):
    rows = jats_table(xml_path, label)
    h = sha(xml_path)
    data = [r for r in rows if r and re.fullmatch(r"\d+", r[0])]
    for r in data:
        pid = f"Pat no {r[0]}"
        for f, v in zip(header[1:], r[1:]):
            if v == "":
                continue
            emit(study_key=study, source_subject_id=pid, visit=visit_of(f), field=f, value=v,
                 unit="years" if "(yr" in f or "(years)" in f else ("mmol/L" if "β-OHB" in f or "Blood ketones" in f else ""),
                 age_days=years_to_days(v) if f == age_field else "",
                 source_url=url, source_file=xml_path, source_sha256=h, license="CC-BY-4.0",
                 source_location=f"{label}; column '{f}'; row {pid}")


# kd_epilepsy_a: Lindefeldt 2019 Table 1 (Pat. no. 1-12; not keyed to ENA ids)
L_XML = "raw/epmc_PMC6344533/fullTextXML.xml"
L_HDR = ["Pat. no.", "Age at KD start (years)", "Sex (M/F)", "Age at seizure start (years)", "Type of seizures",
         "Etiology", "Concomitant AEDs", "Previous AEDs (no.)", "Comorbidity", "Gastrostomy (Y/N)",
         "Efficacy at 3 months: Seizures", "Efficacy at 3 months: Behavior", "KD at 3 months: Ratio",
         "KD at 3 months: Blood ketones"]
emit_patient_table("kd_epilepsy_a", L_XML, "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC6344533/fullTextXML",
                   "Table 1", L_HDR, lambda f: "3 months on KD" if "3 months" in f else ("KD start" if "KD start" in f else ""),
                   "Age at KD start (years)")

# kd_epilepsy_b: Dahlin 2024 Table 1 (Pat no 1-14, ordered by % seizure reduction; not keyed to ENA ids)
D_XML = "raw/epmc_PMC11570732/fullTextXML.xml"
D_HDR = ["Pat no", "Sex", "Age at KD start (yr)", "Age at seizure onset (yr)", "Epilepsytype", "Seizure type(s)",
         "Etiology", "ASMs prior to KD (no)", "ASMs during KD", "Comorbidity", "KD at 3 months: Ratio",
         "KD at 3 months: β-OHB (mmol/L)", "Outcome: Respons", "Outcome: % seizure reduction"]
emit_patient_table("kd_epilepsy_b", D_XML, "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11570732/fullTextXML",
                   "Table 1", D_HDR,
                   lambda f: "3 months on KD" if f.startswith(("KD at 3", "Outcome")) else ("KD start" if "KD start" in f else ""),
                   "Age at KD start (yr)")

# Dahlin 2024 Supplementary Table S1 (mmc1.xlsx, OrigScale sheet): per serum sample header rows keyed
# by CLIENT SAMPLE ID (PA.04 / PB.04) and SUBJECT OR ANIMAL ID (4) - same PA/PB.NN scheme as the ENA titles.
M_XLSX = "raw/epmc_PMC11570732/mmc1.xlsx"
M_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11570732/supplementaryFiles (mmc1.xlsx)"
m_sha = sha(M_XLSX)
ws = openpyxl.load_workbook(f"{G}/{M_XLSX}", read_only=True, data_only=True)["OrigScale"]
hdr = {}
for row in ws.iter_rows(values_only=True):
    if row[0] is not None:
        break  # metabolite rows start
    if row[12] is not None:
        hdr[row[12]] = list(row[13:])
kd_subj = {}  # "P04" -> (study_key, subject)
for st in ("kd_epilepsy_a", "kd_epilepsy_b"):
    for r in by_study[st]:
        if r["subject"].startswith("P"):
            kd_subj[r["subject"]] = st
PER_SAMPLE = ["AGE", "GROUP ID2", "GROUP ID3", "GROUP ID4"]
PER_SUBJECT = ["GROUP NAME 1", "GROUP NAME 2"]
seen = set()
for j, samp in enumerate(hdr["CLIENT SAMPLE ID"]):
    if samp is None:
        continue
    num = hdr["SUBJECT OR ANIMAL ID"][j]
    our = f"P{int(num):02d}"
    st = kd_subj.get(our, "kd_epilepsy_b")
    subj = our if our in kd_subj else ""
    col = openpyxl.utils.get_column_letter(14 + j)
    common = dict(study_key=st, subject=subj, source_subject_id=str(num), source_url=M_URL, source_file=M_XLSX,
                  source_sha256=m_sha, license="CC-BY-4.0")
    for f in PER_SAMPLE:
        v = hdr[f][j]
        emit(**common, visit=hdr["SAMPLE DESCRIPTION"][j], field=f, value=v,
             unit="years" if f == "AGE" else "", age_days=years_to_days(v) if f == "AGE" else "",
             source_location=f"OrigScale; header row '{f}'; column {col} (CLIENT SAMPLE ID {samp}, serum)")
    for f in PER_SUBJECT:
        v = hdr[f][j]
        if (num, f, v) in seen:
            continue
        seen.add((num, f, v))
        emit(**common, field=f, value=v,
             source_location=f"OrigScale; header row '{f}'; column {col} (CLIENT SAMPLE ID {samp}, serum)")

# ----------------------------------------------------- ferreiro_preclinical_ad
F_RDATA = "raw/zenodo_14991167/230118_preclinicalAD_Ferreiro_etal_DATA_v2.RData"
F_URL = "https://zenodo.org/api/records/14991167/files/230118_preclinicalAD_Ferreiro_etal_DATA_v2.RData/content"
F_LIC = "MIT (LICENSE.txt in github.com/dantaslab/preclinAD_GutMicrobiomes v1.0.0; Zenodo record lists other-open)"
F_SKIP = {"Participant", "Reads", "Richness", "Shannon", "Tax.PCoA1", "Tax.PCoA2", "FBratio",
          "Fnl.Richness", "Fnl.Shannon", "Fnl.PCoA1", "Fnl.PCoA2"}  # microbiome-derived, not clinical
f_sha = sha(F_RDATA)
f_ours = {r["subject"] for r in by_study["ferreiro_preclinical_ad"]}
for r in csv.DictReader(open(f"{G}/work/ferreiro/meta.tsv"), delimiter="\t"):
    pid = r["Participant"]
    for f, v in r.items():
        if f in F_SKIP or v == "":
            continue
        emit(study_key="ferreiro_preclinical_ad", subject=pid if pid in f_ours else "", source_subject_id=pid,
             field=f, value=v, unit="years" if f == "Age" else ("days" if f.startswith(("INT_", "Days.", "Interval_Days")) else ""),
             age_days=years_to_days(v) if f == "Age" else "", source_url=F_URL, source_file=F_RDATA,
             source_sha256=f_sha, license=F_LIC, source_location=f"R object `meta`; column {f}")

with open(f"{G}/subject_observations.tsv", "w", newline="") as fh:
    w = csv.DictWriter(fh, COLS, delimiter="\t", lineterminator="\n")
    w.writeheader()
    w.writerows(out)
print(len(out), "rows")
