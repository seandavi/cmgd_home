# fmtpd_ms: per-subject metadata notes

Raw files, with their sha256, are listed in `raw_sha256.txt`. Scripts are in `scripts/`. All Python ran with `-I` (openpyxl came in through `uv run --with openpyxl`).

## fmt_pd_finland (Scheperjans 2024, JAMA Neurol 81:925, PMID 39073834, PMC11287445)

**Result: no per-subject clinical data is public. This study has 0 rows in `subject_observations.tsv`.**

What I found:
- Europe PMC calls the article "not open access" [verified]. Its supplementaryFiles endpoint returns an error bean and fullTextXML returns HTTP 500 [verified]. I kept both responses under `raw/epmc_*PMC11287445/` as evidence.
- The PMC article page (`raw/pmc_PMC11287445/article.html`) lists 4 supplements [verified]:
  - s001: trial protocol (PDF)
  - s002: eMethods/eResults (PDF)
  - s003: eTables 5–12 (xlsx). These are outcome lists and model, alpha-diversity, differential-abundance and sensitivity tables.
  - s004: data sharing statement (PDF)
- I could not download any of the four. PMC serves a JavaScript proof-of-work page instead of the file, Europe PMC `/bin/` returns 403, and jamanetwork.com returns 403 with a Cloudflare challenge [verified]. I did not try to get around these blocks. Judging by the eTable titles, s003 holds group-level models, not per-subject data [unverified]. The PMC page shows no Creative Commons license string, so the license is "unknown / publisher copyright" [verified that no CC string is present].
- The ClinicalTrials.gov record is NCT04854291 (`raw/ctgov_NCT04854291/NCT04854291.json`) [verified]. hasResults=false. Its IPD statement says de-identified clinical data and metadata are shared "upon reasonable request and execution of a data transfer agreement", and that only protocol and analytic code will be shared [verified]. **Clinical data is on request, under a DTA.** The registered outcomes include MDS-UPDRS I–IV, TUG, NMSS, BDI-II, BAI, RBDSQ, **MoCA**, IBS-SSS and PDQ-39, measured at 6 and 12 months [verified].
- ENA PRJEB68317 (`raw/ena_PRJEB68317/PRJEB68317.xml`) describes "45 Parkinson's patients with 15 placebo and 15+15 fecal transplantations from two donors" [verified]. The paper says 14 participants got one donor and 16 got the other [verified, PMC text]. These two accounts disagree. The BioSample records have no clinical fields, only title, description ("gut microbiome") and collection date "2021" [verified in biosample_attributes.tsv.gz].
- Europe PMC searches for PRJEB68317 and NCT04854291, and Zenodo/GitHub searches, turned up no deposit with per-subject data [verified, searches run 2026-11-23].
- Group-level data only: Table 1 (median age 65 placebo vs 66 FMT; 9M/6F placebo, 16M/14F FMT) and the outcome model tables. These are not per-subject and are not in the TSV.

Id structure in specimens.tsv (all inference, not confirmed by the source):
- The X1.* (28), X2.* (9) and X3.* (11) subjects add up to **48**, which equals the 48 randomized patients in the paper [verified counts]. The prefix is probably a site or randomization stratum, but that is [unverified]. The paper names Helsinki, Lahti, Tampere and Turku as sites.
- HY (30), TY (12) and TA (8) are 50 screening-only samples (`_DYS_SC_` = dysbiosis-test screening sample). They may stand for HUS (Helsinki), TYKS (Turku) and TAYS (Tampere) [unverified guess]. No public key links screening ids to X ids.
- HM and PA are the two stool donors, consistent with "two donors" [verified count; the names are unverified].
- The visit codes V1/V1_ab and V3–V5 likely correspond to baseline and the 1/3/6/12-month visits. PRO1–4 are possibly additional home-collected samples, but no source available to me defines PRO or V [unverified]. The protocol (s001) probably defines both but was blocked.
- Arm (FMT/placebo) per subject: **not public**.

Next step: request the per-sample clinical table (arm, visit dates, MDS-UPDRS, MoCA) from the corresponding author under a DTA, as NCT04854291 describes. The s001 protocol and s004 data sharing statement can also be fetched by hand in a browser.

## ms_onset_turin (Maglione 2026, eBioMedicine 132:106470, PMID 42700718, PMC13688122)

**Result: 2,263 rows from Supplementary Table S1 (`mmc2.xlsx`, sheet "Foglio1", 124 subjects plus NEG and POS rows, 18 columns per row).**

Sources:
- The Europe PMC supplement zip (`raw/epmc_PMC13688122/supp.zip`) was extracted to `x/` [verified].
- The full-text XML (`raw/epmc_fulltext_PMC13688122/fulltext.xml`) gives the article license as **CC BY-NC-ND 4.0** [verified]. I assumed the supplements carry the same license [unverified]. Under NC-ND we can redistribute the file unmodified for non-commercial use. A derived long table may count as an adaptation, so check before publishing it.
- Columns: id, category, naive, sex, age, bmi, sequencing_batch, sample_collection_date, gc_treatment, lesion_burden, spinal_cord_lesion, subtentorial_lesions, gadolinium_contrast, clinical_presentation, WORSENING, EDSS_DIAGNOSI, EDSS_PROGRESSIONE, Event, EventTime [verified].
- No column for DMT or therapy after onset. The only treatment field is `gc_treatment` (glucocorticoid exposure at onset, positive/negative) [verified]. No MRI lesion counts are given, only the binary flags plus WORSENING.

Mapping: our `subject` matches the source `id` exactly for all **89/89** of our subjects (HD01–HD18, MS01–MS69, NEG, POS) [verified]. HD19–HD55 have blank `subject`. They are 37 PREDICT1 healthy donors (USA) from external data, not in PRJNA1245671 [verified, Methods text and sequencing_batch 6].

**Why there are 89 runs but the paper reports 108 participants** [verified from Methods and S1]:
- The 89 runs are 69 pwMS recruited, 18 local HD, and the NEG and POS sequencing controls.
- The paper's analysis set of 108 is 53 MS + 55 HD:
  - 53 MS = 69 recruited − 11 non-naive (naive="no": MS03, MS12, MS18, MS44, MS46, MS53, MS56, MS60, MS61, MS62, MS69) − 5 with recent antibiotic use.
  - 55 HD = 18 local + 37 PREDICT1.
- S1 does not say which 5 MS subjects took antibiotics [verified absent].
- Our specimens.tsv labels all 69 MS as "MS onset patient", including the 11 that were not treatment-naive. That disagrees with the paper's cohort definition.

How I read the timepoints (labels are mine, because the table doesn't label them):
- `onset`: EDSS_DIAGNOSI and the baseline MRI and clinical flags. Baseline MRI was done within 6 months of T0 [verified, Methods].
- `12mo_followup`: EDSS_PROGRESSIONE, WORSENING, Event and EventTime. I take EDSS_PROGRESSIONE to be EDSS at the 12-month follow-up, matching "EDSS progression" in Table 1 [unverified interpretation].
- `stool_sample`: sequencing_batch and sample_collection_date, with `biosample` filled. For HD and controls, all fields use this label.
- EventTime has no stated unit. Its values (52.14 = 365/7) suggest weeks to event or censoring [unverified], so `unit` is left blank.
- Age is in years. age_days = years × 365.25 and is applied to the onset and stool-sample rows.
- Values are verbatim: "NA" is kept, and decimal commas such as "1,5" and BMI "21,8" are left as written.
- The MS non-NA counts match the paper's Table 1 N: 47 for EDSS at diagnosis and 41 for EDSS progression [verified].

Contradictions with our data:
- 13 sample_collection_date values in S1 differ from the BioSample collection_date: HD03–HD14 are off by 2–6 days, and HD18 is 2024-01-24 in S1 vs 2024-01-23 in BioSample. The build script lists them. I could not tell which source is right.
- The paper's group-level tables (Table 1, Supplementary Table S2 in mmc3.docx) are summaries and are not in the TSV.
- The other supplements are per-sample microbiome or model outputs, not clinical data, and are not in the TSV: mmc4 (read mapping), mmc5 (abundances), mmc6 (alpha diversity), mmc7–9 (MaAsLin3), mmc8 (HUMAnN).
