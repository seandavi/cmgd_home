"""Cross-checks for asu_mtt/subject_observations.tsv. usage: python3 -I check.py <asu_mtt dir> <specimens.tsv>"""
import site, sys
sys.path.append(site.getusersitepackages())
import csv, json, re, collections
from pathlib import Path
import openpyxl

d, specimens = Path(sys.argv[1]), sys.argv[2]
obs = list(csv.DictReader(open(d / "subject_observations.tsv"), delimiter="\t"))
val = {(r["source_subject_id"], r["visit"], r["field"]): r["value"] for r in obs}
code_of = {r["subject"]: r["source_subject_id"] for r in obs if r["subject"]}

# 1. CARS / ABC printed in the caporaso-lab notebook (keyed by "<subject>.ST00n") vs Kang supplement (keyed by B1nn)
nb = json.load(open(d / "raw/github_autism-fmt1/metadata-processing.ipynb"))
text = "".join("".join(o.get("text", "")) for c in nb["cells"] for o in c.get("outputs", []))
st_visit = {"ST001": "baseline", "ST003": "10wk", "ST004": "18wk"}
n_ok = n_bad = 0
for m in re.finditer(r"^(\d+)\.(ST00[134]),([^,]+),[^,]+,([^,]+),", text, re.M):
    subj, st, cars, abc = m.groups()
    v = st_visit[st]
    if subj not in code_of or cars.lower() in ("na", "nan"):
        continue  # even numbers are mothers; na = not assessed
    mine = (val.get((code_of[subj], v, "CARS | " + {"baseline": "Baseline", "10wk": "week 10", "18wk": "week 18"}[v])),
            val.get((code_of[subj], v, "Aberrant Behavior Checklist (ABC) | Total | " + {"baseline": "initial", "10wk": "week 10", "18wk": "week 18"}[v])))
    ok = None not in mine and float(mine[0]) == float(cars) and float(mine[1]) == float(abc)
    n_ok += ok; n_bad += not ok
    if not ok:
        print("MISMATCH notebook", subj, st, cars, abc, mine)
print(f"notebook CARS/ABC vs supplement: {n_ok} match, {n_bad} mismatch")

# 2. sex: Qiita vs Kang supplement
q = list(csv.DictReader(open(d / "raw/qiita_10532/x/templates/10532_20230206-075033.txt"), delimiter="\t"))
qsex = collections.defaultdict(set)
for r in q:
    if r["sex"] in ("male", "female"):
        qsex[r["host_subject_id"]].add(r["sex"][0].upper())
for code, s in sorted(qsex.items()):
    k = val.get((code, "", "gender"))
    if {k} != s:
        print(f"sex: {code} supplement={k} qiita={sorted(s)}")

# 3. 2-year stools: Qiita ST005 vs specimens.tsv 2yr
q2 = {r["description"].split(".")[0] for r in q if r["description"].endswith(".ST005")}
s2 = {r["subject"] for r in csv.DictReader(open(specimens), delimiter="\t") if r["study_key"] == "asu_mtt" and r["visit"] == "2yr"}
print("2yr stool subjects: qiita-only", sorted(q2 - s2, key=int), "specimens-only", sorted(s2 - q2, key=int))

# 4. Kang 2017 MOESM2 vs Kang 2019 MOESM3, same sheet "general data", compare by header triple + code
def table(p):
    g = list(openpyxl.load_workbook(p, data_only=True)["general data"].iter_rows(values_only=True))
    hdr, h0, h1 = [], "", ""
    for j in range(len(g[2])):
        a, b, c = g[0][j], g[1][j], g[2][j]
        if a: h0, h1 = a, ""
        if b: h1 = b
        hdr.append((h0, h1, c))
    seen = collections.Counter()
    out = {}
    for j, h in enumerate(hdr):
        seen[h] += 1
        for r in g[3:]:
            if r[0]:
                out[(r[0], h, seen[h])] = r[j]
    return out
a = table(d / "raw/epmc_PMC5264285/x/40168_2016_225_MOESM2_ESM.xlsx")
b = table(d / "raw/epmc_PMC6456593/x/41598_2019_42183_MOESM3_ESM.xlsx")
diff = [(k, a[k], b[k]) for k in a if k in b and a[k] != b[k] and k[1][2] is not None]
print(f"2017 vs 2019 general data: {sum(k in b for k in a)} shared cells, {len(diff)} differ")
for x in diff[:15]:
    print("  ", x)
