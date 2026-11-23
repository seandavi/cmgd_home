"""Build asu_mtt/subject_observations.tsv from the Kang 2019 Sci Rep supplement (MOESM3).

Subject mapping key: Qiita study 10532 sample information, where `description`
("<subject>.ST00n") and `host_subject_id` ("B1nn") sit on the same row.

usage: python3 -I build.py <asu_mtt dir> <specimens.tsv>
"""
import site, sys
sys.path.append(site.getusersitepackages())
import collections, csv, hashlib, re
from pathlib import Path
import openpyxl
from openpyxl.utils import get_column_letter

out_dir, specimens_tsv = Path(sys.argv[1]), sys.argv[2]
raw = out_dir / "raw"
XLSX = "raw/epmc_PMC6456593/x/41598_2019_42183_MOESM3_ESM.xlsx"
XLSX_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC6456593/supplementaryFiles (zip member 41598_2019_42183_MOESM3_ESM.xlsx)"
QIITA = raw / "qiita_10532/x/templates/10532_20230206-075033.txt"
LICENSE = "CC-BY-4.0"
STUDY = "asu_mtt"


def sha256(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


# --- id mapping: Qiita description prefix -> host_subject_id (majority vote, discordant rows reported)
pairs = collections.defaultdict(collections.Counter)
for r in csv.DictReader(open(QIITA), delimiter="\t"):
    m = re.match(r"^(\d+)\.S[TW]\d+$", r["description"])
    if m:
        pairs[m.group(1)][r["host_subject_id"]] += 1
code_to_subject = {}
for num, c in pairs.items():
    code, n = c.most_common(1)[0]
    if len(c) > 1:
        print(f"WARN qiita: description prefix {num} -> {dict(c)}; using {code}", file=sys.stderr)
    assert code not in code_to_subject, code
    code_to_subject[code] = num
ours = {r["subject"] for r in csv.DictReader(open(specimens_tsv), delimiter="\t") if r["study_key"] == STUDY and r["subject"]}

# --- visit label from the source sub-headers
DERIVED = re.compile(r"(?i)^(diff|% change|.*\bvs\b.*|responder\?)")
VISIT_BY_LABEL = {
    "baseline": "baseline", "initial": "baseline", "initial pgi-r": "baseline",
    "initial muscle strength": "baseline",
    "week 10": "10wk", "end of treatment pgi-r (improvement)": "10wk",
    "week 18": "18wk", "end of observation pgi-r": "18wk",
    "week 17": "17wk",
    "2-year": "2yr", "year 2": "2yr", "2-year follow up": "2yr",
    "follow up": "follow-up",
}
VISIT_BY_GROUP = {
    "GSRS - baseline": "baseline", "GSRS - week 2": "2wk", "GSRS - week 10": "10wk",
    "GSRS - week 18": "18wk", "GSRS - 2-year": "2yr",
    "GSRS-screening": "screening", "ADI-R current age": "screening",
    "ADI-R - diagnostic (age 3-4)": "",  # retrospective, about age 3-4
}
BASELINE_COLS = {"age", "weight (pounds)", "height (inches)", "BMI"}
UNITS = {"age": "years", "weight (pounds)": "pounds", "height (inches)": "inches"}

wb = openpyxl.load_workbook(out_dir / XLSX, data_only=True)
xlsx_sha = sha256(out_dir / XLSX)
rows_out = []
unmapped = set()


def emit(code, visit, field, value, unit, loc, age_years):
    subject = code_to_subject.get(code, "")
    if subject and subject not in ours:
        subject = ""
    if not subject:
        unmapped.add(code)
    age_days = f"{age_years * 365.25:.0f}" if visit == "baseline" and age_years is not None else ""
    rows_out.append([STUDY, subject, code, "", visit, "", age_days, field, str(value), unit,
                     XLSX_URL, XLSX, xlsx_sha, loc, LICENSE])


# general data: 3 header rows (group / subgroup / column), data from row 4
ws = wb["general data"]
grid = list(ws.iter_rows(values_only=True))
h0 = h1 = ""
cols = []
for j in range(ws.max_column):
    a, b, c = (grid[i][j] for i in range(3))
    if j >= 224:  # ponytail: row-0 group "Daily Stool Log" ends at col 223; later blocks have no row-0 group
        h0 = ""
    elif a:
        h0, h1 = a.strip(), ""
    if b:
        h1 = b.strip()
    if j == 0 or c is None or DERIVED.match(str(c).strip()) or h1.startswith("change in GSRS"):
        continue
    c = str(c)
    field = " | ".join(x for x in (h0, h1, c.strip()) if x)
    if j <= 12:
        visit = "baseline" if c in BASELINE_COLS else ""
    elif h1 in VISIT_BY_GROUP:
        visit = VISIT_BY_GROUP[h1]
    else:
        visit = VISIT_BY_LABEL[c.strip().lower()]
    cols.append((j, field, visit, UNITS.get(c, "")))

age_by_code = {}
for r in grid[3:]:
    if r[0]:
        age_by_code[r[0]] = r[1]
        for j, field, visit, unit in cols:
            v = r[j]
            if v is None or (isinstance(v, str) and not v.strip()):
                continue
            emit(r[0], visit, field, v, unit, f"general data!{get_column_letter(j + 1)}", age_by_code[r[0]])

# medical history: subject-level history, one header row
ws = wb["medical history"]
grid = list(ws.iter_rows(values_only=True))
for r in grid[1:]:
    if r[0]:
        for j in range(1, len(r)):
            if r[j] is not None and grid[0][j] is not None:
                emit(r[0], "", str(grid[0][j]).strip(), r[j], "", f"medical history!{get_column_letter(j + 1)}", None)

# diet info: kids block only (cols A-F); moms (B1nn even codes) are not our subjects
ws = wb["Diet info"]
grid = list(ws.iter_rows(values_only=True))
for r in grid[2:]:
    if r[0]:
        for j in range(1, 6):
            if r[j] is not None:
                emit(r[0], "baseline", grid[1][j], r[j], "", f"Diet info!{get_column_letter(j + 1)}", age_by_code.get(r[0]))

header = ["study_key", "subject", "source_subject_id", "biosample", "visit", "days_from_baseline", "age_days",
          "field", "value", "unit", "source_url", "source_file", "source_sha256", "source_location", "license"]
with open(out_dir / "subject_observations.tsv", "w", newline="") as f:
    w = csv.writer(f, delimiter="\t", lineterminator="\n")
    w.writerow(header)
    w.writerows(rows_out)

mapped = {r[2] for r in rows_out if r[1]}
print(f"rows={len(rows_out)} codes_mapped={len(mapped)} unmapped={sorted(unmapped)} "
      f"fields={len({r[7] for r in rows_out})} our_subjects_without_data={sorted(ours - set(code_to_subject[c] for c in mapped), key=int)}")
assert unmapped <= {"B125"} and len(mapped) == 38, unmapped  # B125: in diet/medical sheets only, absent from Qiita and specimens
