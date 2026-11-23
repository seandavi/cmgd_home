# asu_mtt: ASU microbiota transfer therapy (NCT02504554), PRJNA782533

## What I found

- **Per-subject clinical table [verified].** Kang 2019 *Sci Rep* 9:5821 (PMC6456593), Supplementary file `41598_2019_42183_MOESM3_ESM.xlsx`. It has three sheets: `general data`, `medical history` and `Diet info`. `general data` has one row per child (codes B101–B181). Columns cover age, gender, weight/height/BMI, ASD or control, oral/rectal route, donor ids, PGI-R, CARS, muscle strength, ABC (5 subscales + total), SRS (5 subscales + total), Vineland (VABS-II subdomain age-equivalent scores + average), GSRS (5 subscales + average), the daily stool log, GSRS at screening, and ADI-R. The time points are baseline, week 2 (GSRS only), week 10, week 18 (week 17 for the stool log) and 2 years. All of it went into `subject_observations.tsv`.
- **Kang 2017 *Microbiome* 5:10 (PMC5264285), `40168_2016_225_MOESM2_ESM.xlsx` [verified].** Same layout but stops at week 18. I compared it cell by cell with the 2019 file: 5,814 shared cells, and only one differs (B119 `rectal or oral group`: `R` in 2017, `3` in 2019). The 2019 file is a superset, so I did not ingest the 2017 file again. Its MOESM5 is a taxonomy table, not clinical data.
- **Nirmalkar 2022 *IJMS* (PMC9654974) [verified].** The supplement is a single PDF of figures and tables with no subject ids. The paper says the clinical data are in Kang et al.
- **ClinicalTrials.gov NCT02504554 [verified].** Results are posted, but they are group-level only (Combined/Oral/Rectal arm means for GSRS, PGI-R, CARS, SRS, VABS, the stool record and the Short Sensory Profile, baseline → week 10/18). There is no IPD sharing statement. Not ingested. File: `raw/ctgov_NCT02504554/NCT02504554.json`.
- **Not ingested:** Kang 2019 `MOESM2_ESM.xlsx` (Supplementary Table S1, medication changes after MTT, wide free-text layout); Kang 2017/2019 PDF supplements (figures, Table 1 summaries); the moms' block of `Diet info` (even codes B102…, mothers are not our subjects).

## Subject id mapping [verified]

- **Key: Qiita study 10532 sample information** (`raw/qiita_10532/…/10532_20230206-075033.txt`, public download). Each row carries both `description` = `<n>.ST00k` / `<n>.SW0kk` (the same form as our BioSample `source_material_id`) and `host_subject_id` = `B1nn`. All 38 prefixes map one-to-one: 1→B101, 3→B103, …, 81→B181. One row disagrees (`21.SW009` has `host_subject_id` B127, while the other 15 rows for prefix 21 say B121), so I used the majority.
- **Independent check:** CARS and ABC-total values that the caporaso-lab/autism-fmt1 notebook prints per `<n>.ST001/ST003/ST004` match the supplement's B1nn baseline, week 10 and week 18 values in 57 of 57 cases (`scripts/check.py`).
- **Result:** 38 of 38 of our subjects mapped (18 ASD, 20 TD). B125 appears only in `Diet info` and `medical history`, has no Qiita or specimen rows, and is left unmapped. B125 and B129 (our 25 and 29) are the ASD codes missing from `general data`, consistent with 18 completers.
- **Donors:** the supplement's `BBT_Donor_ID` and `Maintenance_BBT_donor_ID` values (BBT2014-00029/35/36/37/38, MD-2014-00002/00003) exactly match the donors' `source_material_id` [verified]. They are stored as per-child subject constants. The donors themselves have no clinical rows.

## Conventions in the table

- `visit` is normalized from the source sub-header (baseline, 2wk, 10wk, 17wk, 18wk, 2yr, follow-up, screening). The verbatim sub-header is the last part of `field`, and `source_location` gives sheet!column.
- `field` joins the three header rows with ` | ` (e.g. `Aberrant Behavior Checklist (ABC) | Total | week 10`), with leading and trailing whitespace stripped.
- I dropped derived columns (Diff, % change, "vs initial/baseline", the "change in GSRS" blocks and `Responder?`).
- `age`, weight, height, BMI and `Diet info` are tagged `baseline` [inference: one value per child, at enrollment]. `age_days` = years × 365.25 and is filled on baseline rows only.
- Daily Stool Log "Follow Up" is kept as `follow-up`; it is probably the 2-year follow-up [unverified].
- `medical history` columns `6-12`, `12-24`, … are antibiotic courses by age band (months) next to `antibiotics 0-6`. The headers are kept verbatim.
- PGI-R values are improvement ratings as the source gives them.
- `biosample` and `days_from_baseline` are blank because the source gives neither.

## Contradictions and caveats

- **Sex:** Qiita has both `female` and `male` for B113. The Kang supplement says `M`. The table uses the supplement.
- **2-year stools:** Qiita ST005 subjects = specimens.tsv `2yr` subjects (17 and 31 are missing from both) [verified]. Clinical 2-year scores do exist for 17 and 31.
- **ST numbering in Qiita:** ST001 = week 0, ST002 = week 3/18 (mixed), ST003 = week 10, ST004 = week 18, ST005 = 2-year [verified from the Qiita `week` column]. Our specimens hold only ST001/ST003/ST005.
- **TD children:** TD rows have only demographics, muscle strength, GSRS-screening, medical history and diet. There are no CARS/ABC/SRS/VABS scores: those cells are empty [verified]. They were probably not assessed for TD [inference].

## Sources and licenses

| file | URL | sha256 | license |
|---|---|---|---|
| raw/epmc_PMC6456593/supp.zip (→ x/41598_2019_42183_MOESM3_ESM.xlsx, used) | https://www.ebi.ac.uk/europepmc/webservices/rest/PMC6456593/supplementaryFiles | faa09523…; xlsx ffefa0b9c70c1516a26a325b08e10ca05f4df18e782b43ed697aefd16f9dc637 | CC-BY-4.0 (article license [verified]; it applies to the supplement unless stated otherwise [unverified]) |
| raw/epmc_PMC5264285/supp.zip (→ x/40168_2016_225_MOESM2_ESM.xlsx, checked only) | https://www.ebi.ac.uk/europepmc/webservices/rest/PMC5264285/supplementaryFiles | 73de5ad8…; xlsx 9763ec72aca4dc16b77db99143108a4eb220fb04f6e5d5d5f0ca8b169be074c4 | CC-BY-4.0 article + CC0 waiver for data [verified] |
| raw/epmc_PMC9654974/supp.zip | https://www.ebi.ac.uk/europepmc/webservices/rest/PMC9654974/supplementaryFiles | ac49c6372f8b843e215c426407d6e4c3e4f45e2fdc27c139e63a1564fd74a0a0 | CC-BY-4.0 [verified] |
| raw/qiita_10532/sample_information.zip (mapping key) | https://qiita.ucsd.edu/public_download/?data=sample_information&study_id=10532 | 15b95aabc91358bfe25610977ab6853da9fd91cb60a987f3632925b64cc24b02 | unknown (no license stated) |
| raw/github_autism-fmt1/metadata-processing.ipynb (check only) | https://raw.githubusercontent.com/caporaso-lab/autism-fmt1/master/16S/metadata-processing.ipynb | d3664116c04b3c4ed04fa9bbc0b5c8f07d588a32215f197d32e756e16b9e423d | unknown (repo has no license) |
| raw/ctgov_NCT02504554/NCT02504554.json | https://clinicaltrials.gov/api/v2/studies/NCT02504554 | 1902bec92969bf641b3352ad1ab099bd3464ad0eff65d1a9cd9cfd871b32ba50 | unknown (ClinicalTrials.gov, U.S. government data) |
| raw/epmc_xml_PMC*/fullText.xml | https://www.ebi.ac.uk/europepmc/webservices/rest/<PMCID>/fullTextXML | see `sha256sum raw/epmc_xml_*/fullText.xml` | as the articles above |

Rebuild with `python3 -I scripts/build.py . <specimens.tsv>` and re-check with `python3 -I scripts/check.py . <specimens.tsv>`.
