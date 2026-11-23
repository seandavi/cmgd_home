# haran_kd_ferreiro: per-subject metadata notes

Output: `subject_observations.tsv` (29,492 rows). Build: `python3 -I scripts/build.py <group_dir> <specimens.tsv>`.
R serialized files were read with `scripts/dump_rds_sampledata.R` and `load()` in Rscript (data only; no downloaded R code was sourced or run).
Every source file, with URL, sha256 and license, is listed in `raw/SOURCES.tsv`.
Values are verbatim. Where `age_days` is filled, it is the source value in years × 365.25, rounded; the original stays in `value`.

## haran_nh_ad (Haran 2019 mBio, PMC6509190; PRJNA529586)

- **The mBio paper has no per-subject data.** [verified] Supplements st001/st002 are species-literature tables, sf001/sf002 are figures and s0001 is references. The paper's data statement says data are available "upon written request to John P. Haran". Table 1 is group-level only.
- **Per-sample clinical metadata is on GitLab.** [verified] It comes from the follow-up paper on the same cohort, Haran/Bucci 2021 *Gut Microbes* (PMC8007149, C. difficile in nursing homes). That paper cites PRJNA529586 and says "Processed data, metadata and code … available at https://gitlab.com/vanni-bucci/2020_cdad_nh_paper". The phyloseq object `phy_mtph_prev_0.10_C_DIFFICILE_renormalized_20200401.rds` (commit d2197842) has `sample_data` with 494 samples, 167 residents (`study_id`, e.g. `CH1-017`) and 127 columns. Those columns include `age`, `male`, `abx6mo` (antibiotics in the prior 6 months), `Dementia`, `Alzheimers`, `Dementia.Other`, `Parkinsons`, `clinical_frailty_scale`, `malnutrition_indicator_sco`, the medication classes, the Charlson items and `C.diff.SPos`. I dropped id and processing columns (`row_name`, `ID.Match`, `Sample.ID`, `Version.2/3`, `study_id`, `total_reads`, `Drop`, `Only.one.sample`, `remove.from.analysis`). That leaves 118 fields.
- **Layout.** A field that is constant across all of a resident's samples is written once per subject with blank `biosample`. A field that varies is written per sample, with `biosample` set. 14 fields vary in at least one resident: `C.diff.SPos`, `Dementia`, `Alzheimers`, `Dementia.Other`, `abx6mo`, `hopsn`, `hosp1yr`, `polypharm5`, `time`, `Floor`, `Site.ID`, `age_cat`, `C.diff.one` and `Ord.C.diff`.
- **No codebook.** [verified absent] The repo has no data dictionary. `male`, `Dementia` and similar columns are 0/1 with an undocumented coding, and the meaning of `time` is undocumented: it does not match our `days_from_baseline`. The unit of `age` is assumed to be years (the paper's Table 1 reports age in years).
- **Data quality: dementia status is a spreadsheet error for many residents.** [verified] `Dementia`, `Alzheimers` and `Dementia.Other` hold the literal value `#REF!` in about 175 of 494 samples. About 52 residents have only `#REF!`, so their dementia status is not available in this file. The values were kept verbatim.
- **No repeated cognitive scores.** [verified] There is no MMSE, BIMS or CPS. There is no license file in the GitLab repo, so the license is "unknown". Treat the data as not redistributable until the authors confirm.
- **Mapping.** [verified, exact id] I stripped the `JPH` prefix and the `V`/`V2` resequencing suffix from our `specimen_name`, which gives the source `Sample.ID` (e.g. `JPHFB291V2` → `FB291`, `DC001` → `DC001`).
  - 483 of our 490 specimens match. For every match, the source `study_id` agrees with our `subject` once hyphens and spaces are removed.
  - 175 of our 178 `subject` values are mapped.
  - Unmatched specimens (not in the source table): DC041, DC072, FB030, FB060, FB070, FB157 and FB183. Their subjects CH1083, CH1123 and CH128 get no rows.
  - 11 source samples from 11 residents are not among our specimens: CH1-130, -152, -169, -171, -180, -185, -192, -196, `CH1 BL-01`, `CH1 BL-03` and `CH1BL-10`. Their subject-level rows have a blank `subject`.
  - The source `study_id` `CH1-178 ` has a trailing space. I trimmed it in `source_subject_id`.
- **Contradictions with specimens.tsv.** [verified]
  - 19 residents are split across two of our `subject` spellings: CH1-011/CH1011, CH1-101/CH1101, CH1-129…CH1-146 (various), CH1-166/CH1166, CH1-167/CH1167 and CH3-011/CH3011. They come from inconsistent BioSample titles. For these, subject-level rows are emitted once for each of our spellings.
  - `CH128` (FB157) looks like a typo for a CH1-xxx id [unverified].
  - Our `visit` is the specimen number, not a timepoint.

## kd_epilepsy_a (Lindefeldt 2019 npj Biofilms Microbiomes 5:5, PMID 30701077, PMC6344533; PRJEB28847)

- **Found.** [verified] Table 1 (CC-BY-4.0) lists 12 patients ("Pat. no." 1–12): age at KD start, sex, epilepsy and etiology details, AEDs, comorbidity, gastrostomy, seizure and behavior efficacy at 3 months (Resp/Nonresp, where responder means >50% seizure reduction), diet ratio and blood ketones. These rows are in the table with `source_subject_id` "Pat no N" and a **blank `subject`**, because the paper never links Pat. no. to the ENA ids.
- **Supplements have no clinical data.** [verified] S1 and S2 are MetaPhlAn2 and SUPER-FOCUS tables with CA/CB/PA/PB column ids. There is no clinical column.
- **Role labels in specimens.tsv are inverted.** [verified]
  - The paper says "Twelve patients starting KD and 11 healthy parents". ENA has 12 `PA/PB` ids (03, 04, 05, 06, 08, 10, 11, 18, 19, 22, 23, 28) and 11 `CA/CB` ids, and the figure legends use "Pat" and "Ctr".
  - Dahlin 2022 (PMC9126955) Supp Table 1 (mmc7) lists PA03…PA28 alongside the extended cohort's PA ids as patients. Dahlin 2024 mmc1 gives PA.04, PA.05 and so on as epileptic children with responder status.
  - So in PRJEB28847, **P = patient (child) and C = control (parent)**. Our `specimens.tsv` has `role=child` for C01…C23 and `role=parent` for P03…P28, which is backwards. This needs fixing upstream.
- **Mapped data from Dahlin 2024 mmc1** ("OrigScale" sheet header rows, serum samples). [verified exact id string] `CLIENT SAMPLE ID` PA.NN/PB.NN together with `SUBJECT OR ANIMAL ID` NN follows the same scheme as the ENA titles. The ids PA.04, 05, 06, 08, 10, 18, 22 and 23 are kd_a subjects, giving **8 kd_a subjects mapped** (P04, P05, P06, P08, P10, P18, P22, P23).
  - Fields: `AGE` per timepoint, and `GROUP ID2/3/4` per sample, with visit "before diet"/"after diet".
  - Subject-level `GROUP NAME 1`: R_ep/NR_ep, i.e. responder or non-responder for seizures.
  - Subject-level `GROUP NAME 2`: R_cog/NR_cog, i.e. a cognitive responder label.
  - The legend in the sheet reads "R _ responder NR_non responder, ep_epilepsy cog_cognition".
  - `biosample` is blank because these are serum samples, not the stool BioSamples. The `AGE` unit is not stated in the sheet. It is treated as years because it matches Table 1 ages (e.g. 15.3).
- **Inferred link from Lindefeldt Pat. no. to ENA id** [unverified, not applied]. Pat. no. k matches the k-th pilot P id in ascending order: 1→P03, 2→P04, 3→P05, 4→P06, 5→P08, 6→P10, 7→P11, 8→P18, 9→P19, 10→P22, 11→P23, 12→P28. This agrees with mmc1 age and response for all 8 ids I could check (ages agree within 0.2 y). Confirm with the authors before using it.
- **Contradiction with specimens.tsv.** The kd_a parents (C ids) have no clinical metadata anywhere.

## kd_epilepsy_b (Dahlin 2024 eBioMedicine, PMC11570732; PRJEB49521)

- **Found.** [verified]
  - Table 1 (CC-BY-4.0) covers 14 patients ("Pat no" 1–14, ordered by % seizure reduction): sex, age at KD start, epilepsy type, ASMs, KD ratio and β-OHB at 3 months, Resp/Nonresp, and **% seizure reduction**. Its rows are in the table with a blank `subject`.
  - mmc1 header rows (see kd_a) map **12 kd_b subjects** by exact id: P12, P14, P17, P20, P25, P34–P39, P42.
  - mmc1 subjects 9, 13 and 40 have no stool BioSample in either project. They are kept under kd_epilepsy_b with a blank `subject`.
  - mmc1 has PA.20 (pre) but PB.22 (post) where a pair might be expected. I kept it as is.
  - Subject 17 is labeled `no ep` in `GROUP NAME 1`.
  - mmc2–5 hold only group statistics.
- **Dahlin 2022** (eBioMedicine 104061, PMC9126955) is the paper that introduced PRJEB49521 ("extended cohort"; PRJEB28847 is the "pilot cohort"). [verified] Its Table 1 is group-level only (28 children, 27 with paired stool). Its supplements hold taxa, Olink proteomics and model tables, with no per-patient clinical table.
- **Does kd_b re-deposit kd_a's children?** **No.** [verified] The P ids are disjoint: kd_a has P03–P28 (12 ids) and kd_b has P01, P02, P12, P14–P17, P20, P21, P25, P27 and P30–P42 except P40 (23 ids). The two sets are one shared enrollment numbering. Dahlin 2022 analyses both deposits together, and its mmc7 table has 31 PA ids. The kd_b ids P16, P17, P27 and P31 are not in that table.
- **Is 'P' in PRJEB49521 patient rather than parent?** **Yes, patient.** [verified] The BioSample description says "fecal samples from children with therapy-resistant epilepsy before starting KD and after three months", with no parents. Dahlin 2022 and 2024 use PA/PB.NN for children before and after the diet (see the mmc1 `GROUP NAME 1` R_ep/NR_ep labels). specimens.tsv already has `role=child` here, which is correct.
- **Inferred links from Table 1 Pat no to mmc1 id** [unverified, not applied]. Exact age and response matches: Pat 1→4, 2→36, 3→37, 6→39, 9→5, 10→10, 12→38, 13→8. Pats 5 and 7 are ambiguous (two candidates each). Pats 4, 8, 11 and 14 match only approximately.

## ferreiro_preclinical_ad (Ferreiro 2023 Sci Transl Med, PMC10680783; PRJNA798058)

- **Not open access in Europe PMC.** [verified] The supplementary-files and full-text endpoints return "not open access" or 500. PMC article supplement links (Data file S1, Supplementary Material, zipped data files) returned a JavaScript "Preparing to download" challenge page instead of the files. Those pages are saved as `*.challenge.html` and were not used.
- **Found on Zenodo.** [verified] The data are in Zenodo 10.5281/zenodo.14991167 (an archive of GitHub dantaslab/preclinAD_GutMicrobiomes v1.0.0), in `230118_preclinicalAD_Ferreiro_etal_DATA_v2.RData`. The md5 matched the Zenodo record. Its object `meta` has 164 participants × 56 columns.
  - I kept 45 clinical columns: Age, Sex, Race, Years.Education, CDR, CSF Aβ42/40, tTau and pTau, PiB and AV45 SUVR and Centiloid, combined.Centiloid, `amyloid.positive.AF`, Tauopathy, `tau.positive.AF`, MRI measures, APOE, PRS, the INT_* intervals, BMI and comorbidities.
  - I dropped the microbiome-derived columns: Reads, Richness, Shannon, PCoA, FBratio and Fnl.*.
- **Codebook.** [verified, from comments in the Zenodo analysis script read as text] Sex 1 = male, 2 = female; Race 4 = Black, 5 = White, 6 = Other. `INT_*` is the interval in days between that assessment and stool collection.
- **Cross-checks.** [verified] `amyloid.positive.AF` gives 115 zeros and 49 ones, which matches the paper's 115 healthy and 49 preclinical. CDR is 0 for all 164. The data are cross-sectional (one stool per participant), so `visit` is blank.
- **Mapping.** [verified, exact id] All 164 `Participant` values equal our `subject` (BioSample sample name). That is 164 of 164 mapped.
- **License.** The GitHub LICENSE.txt is MIT; Zenodo lists "other-open". The analysis R script and `230111_ps2filt_v2.RData` were downloaded but not used. `diet.intake`, `cal.fromfat` and `total.cal` (24-h diet, per participant) also exist in the RData but were not extracted because they are not neuro outcomes.
- **Not available.** Longitudinal follow-up data are not public.
