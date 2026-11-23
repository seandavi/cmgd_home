# External longitudinal gut-metagenome cohorts with neurocognitive / neurodevelopmental / neurological outcomes

Research date: 2026-11-23. Scope: public human stool **shotgun** metagenomes with repeated stool and/or repeated outcome measurement in the same subjects. Studies already curated in cMD (iMSMS_2022, WallenZD_2022, BoktorJC_2023, …, BrooksB_2017) were excluded. None of the candidates below appears in that list.

How I verified things: I counted run accessions with the ENA portal API (`/ena/portal/api/count?result=read_run&query=study_accession=X AND library_strategy=WGS`). I checked per-sample attributes by pulling one BioSample record per project (NCBI efetch or EBI BioSamples). I took data-availability statements from the papers' full text (Europe PMC XML). Labels used throughout: **[verified]** means I fetched it and saw it. **[paper]** means the paper says it but I did not check it in the repository. **[inference]** is my own reading. **[unverified]** means I could not confirm it.

## TL;DR

1. **GAINS (Zeamer et al., UMass)** is the best adult candidate. It has 856 open WGS runs in PRJNA1446836, and each BioSample carries the subject ID, sampling day, cohort group (HC/MCI/AD), **ADAS-Cog-13, a memory z-score and an executive-function z-score**. Visits are every 90 days. It is ready to ingest.
2. **eLABE (Lee et al. 2026, *eBioMedicine*)** is the best pediatric candidate: 187 children, 905 WGS stool samples at 4/8/12/24/36 months, and Bayley-III, ITSEA and PAPA at several ages. Reads are open (PRJNA911205). Sample metadata matched to SRA accessions is in Supplementary Table S1, so the metadata comes from the supplement, not from the BioSample records.
3. **RESONANCE (Bonham et al. 2023, *Sci Adv*)** has open reads: PRJNA695570 has 1,767 WGS runs, and each BioSample has subject ID, timepoint and age. Subject/timepoint metadata and brain-volume tables are on Dryad under CC0. Two things are unverified: whether the cognitive scores are in the Dryad CSV, and how Dryad sample IDs join to SRA (the download returned 403 to my automated fetch).
4. Second tier, usable with some manual curation: the **ASU microbiota-transfer-therapy (MTT) autism trial** (PRJNA782533, 79 WGS runs, baseline/10 weeks/2 years; per-subject outcomes are in the Kang 2017/2019 papers), the **Haran 2019 nursing-home AD cohort** (PRJNA529586, 490 WGS runs, day-coded longitudinal samples, diagnosis only), **M4EFaD Bangladesh** (PRJNA1087376, 230 WGS runs; Bayley-4 and EEG on figshare; one stool timepoint so far) and **NHBCS** (PRJNA296814; shotgun only at 6 weeks and 1 year; the SRS-2 outcome is not public).
5. The main gap: most PD, MS and dementia trials with shotgun reads (FMT-PD Finland PRJEB68317, the MS-onset cohort PRJNA1245671, ketogenic-diet epilepsy) deposit reads with **no clinical or outcome metadata**. Using them means a data-use request to the authors. Many well-known pediatric cognition studies (VDAART, CHILD, CHaRM, UNC Carlson) and longitudinal PD/MS studies are 16S-only.

## Ranked main table

Rank = usefulness to cMD (shotgun + open reads + open longitudinal outcome metadata first).

| # | Study / cohort | Population | Seq | Accession (runs verified) | Reads | Outcome metadata public? | Subjects / samples / timepoints / span | Neuro outcome (repeated?) |
|---|---|---|---|---|---|---|---|---|
| 1 | Zeamer 2025 (bioRxiv/PMC11952313); Zeamer 2026 *Gut Microbes* 10.1080/19490976.2026.2676162 — **GAINS** | Community older adults (60+), MA, USA: HC/MCI/AD | WGS | PRJNA1446836 — **856 WGS runs** [verified] | Open | **Yes, in BioSample** (`study_id`, `DaySample`, `cohort_subset`, `ADAS.COG.13`, `Memory_sum_Z`, `EF_sum_Z`, age, sex) [verified on SAMN56833100] | 260 enrolled [paper]; visits every 90 days [paper]; sample count beyond runs unverified | ADAS-Cog-13, CDR, MMSE, NIH Toolbox cognition at every visit [paper] — **repeated** |
| 2 | Lee 2026 *eBioMedicine* 133:106533, PMID 42913303 — **eLABE** (WashU) | Infants/toddlers, St. Louis, enriched for social disadvantage | WGS (project also has 16S) | PRJNA911205 — **1,019 WGS + 275 AMPLICON runs** [verified]; the project also holds maternal samples from Warner 2023 [verified: BioSample has `Mother/Child status`, `Dyad id`] | Open | **Yes, in Supplementary Table S1** ("Sample metadata is available in Supplementary Table S1", with SRA accessions) [paper]; BioSample has only mother/child + dyad ID [verified] | 187 children / 905 samples / 5 timepoints (4, 8, 12, 24, 36 months) [paper] | Bayley-III (cognitive, language, motor), ITSEA, PAPA "at multiple ages" [paper] — repeated |
| 3 | Bonham 2023 *Sci Adv* 9:eadi0497, PMID 38134274, 10.1126/sciadv.adi0497 — **RESONANCE** (ECHO) | Healthy children 0–~12 y, Rhode Island | WGS (project also has 16S) | PRJNA695570 — **1,767 WGS + 613 AMPLICON runs** [verified]; includes mothers (alias `M…`) and children (`C…`) [verified] | Open | Partly. BioSample has `subject id`, `timepoint`, `host age` [verified on SAMN17619207]. Dryad 10.5061/dryad.fxpnvx0zq (CC0) has `complete_filtered_dataset.csv` with subject/timepoint metadata and `brain_normalized.csv` (MRI volumes) [verified README]. Cognitive-score columns not confirmed (download blocked) [unverified] | 381 children / 493 stool samples in the paper [paper]; accelerated longitudinal design | Mullen (MSEL), Bayley, WPPSI-4, WISC-V composites; MRI segmentation; repeated in a subset [paper] |
| 4 | Nirmalkar 2022 *IJMS* 23:13481, PMID 36362265 (shotgun); Kang 2017 *Microbiome*, Kang 2019 *Sci Rep* PMID 30967657 (clinical) — **ASU MTT, NCT02504554** | Children with ASD + GI symptoms, plus typically developing (TD) controls and donors, Arizona | WGS | PRJNA782533 — **79 WGS runs** [verified] | Open | Timepoint only in BioSample description (e.g., `MTT_10wk`) [verified on SAMN23383816]; per-subject CARS/ABC/SRS/VABS-II/PGI-III in the Kang papers' supplements [unverified] | ASD 18 at baseline, 18 at 10 weeks, 16 at 2 years; TD 20; donors 7 [paper] / 3 timepoints / ~2 y | CARS, ABC, SRS, VABS-II, PGI-III, GSRS [paper] — repeated |
| 5 | Haran 2019 *mBio* 10:e00632-19, PMID 31064831 — **UMass nursing-home AD cohort** | Elderly nursing-home residents, MA | WGS | PRJNA529586 — **490 WGS runs** [verified] | Open | BioSample has subject (title `subject_CH1-…`), `collection_day`, `specimen_number` [verified on SAMN17216961/SAMN17216872]; **no dementia or cognition field**; AD status presumably in the mBio supplement [unverified] | 108 residents, ~300 samples per UMass press release [secondary]; 490 runs now deposited | Dementia diagnosis (AD vs other vs none). Repeated cognitive scores unverified |
| 6 | Portlock 2025 *Nat Commun* 16:473, PMID 39773949 — **M4EFaD** (Bangladesh) | 12-month-olds with moderate acute malnutrition vs well-nourished, Dhaka | WGS | PRJNA1087376 — **230 WGS runs** [verified] | Open | BioSample has `host_subject_id`, `subject_age_months` [verified on SAMN40442963]; Bayley-4, Wolke, EEG, anthropometry on figshare 10.17608/k6.auckland.25560768 [paper] | ~230 children; **one stool timepoint (12 mo) in this paper** [paper/inference]; protocol plans stool at 1, 2 and 3 y (PLOS One 10.1371/journal.pone.0296529) [paper] | Bayley-4, Wolke, EEG power at enrollment [paper] — not yet repeated in public data |
| 7 | Laue 2020 *Sci Rep* 10:15515, PMID 32968156 — **NHBCS** | Birth cohort, New Hampshire | 16S (6 wk–3 y) + WGS subset (6 wk, 1 y) | PRJNA296814 — **1,082 WGS + 1,902 AMPLICON runs** [verified] | Open | **No.** "Epidemiologic data are not publicly available" (Laue 2022, PMC10319341) [paper, via search excerpt] | 273 with ≥1 sequenced stool; WGS n=101 (6 wk) and 103 (1 y) [paper] | SRS-2 at 3 y (single) [paper]; other NHBCS behavior papers exist (Laue 2021 *Pediatr Res*) |
| 8 | Scheperjans 2024 *JAMA Neurol* 81:925, PMID 39073834 — **FMT-PD trial, Finland** | PD patients, FMT vs placebo | WGS | PRJEB68317 — **416 WGS runs** [verified]; visit encoded in alias (`PRO1`, `V1_ab`, `V5`) [verified] | Open | **No** clinical fields in BioSample [verified on SAMEA115136727]; paper data-sharing statement not checked [unverified] | 45 patients randomized [paper] / multiple visits / 12 mo | MDS-UPDRS etc. [paper]; cognitive endpoints unverified |
| 9 | Lindefeldt 2019 *npj Biofilms Microbiomes*; Dahlin 2024 (PMC11570732) — **ketogenic diet in pediatric epilepsy** (Stockholm) | Children with drug-resistant epilepsy | WGS | PRJEB28847 — **48 WGS runs**; PRJEB49521 — **46 WGS runs** [verified] | Open | Per-sample seizure response not confirmed in ENA [unverified]; supplements hold metabolomics [paper] | ~28 children / baseline + 3 mo [paper] | Seizure reduction (neurological, not cognitive) |
| 10 | Maglione 2026 *eBioMedicine* 132:106470, PMID 42700718 — **MS at onset** (Italy) | Treatment-naive MS + healthy donors | WGS | PRJNA1245671 — **89 WGS runs** [verified] (paper reports 53 pwMS + 55 HD = 108; discrepancy) | Open | **No** (BioSample has alias only) [verified on SAMN47761366] | 53 pwMS / stool at diagnosis / clinical + MRI over 1 y [paper] | EDSS, MRI lesion activity over 1 y (outcome repeated, stool probably single) [paper/inference] |
| 11 | Fahur Bottino 2025 *Nat Commun* 16:660 — **Khula** (Wellcome LEAP 1kD) | Infants, Cape Town | WGS | PRJNA1128723 — **429 WGS runs** [verified] | Open | **No** outcome fields in BioSample [verified on SAMN43038867] | Longitudinal infant + maternal [secondary] | Cohort designed for 1,000-day neurodevelopment; no public outcome linkage found [unverified] |
| 12 | Vaher 2024 *Cell Rep Med* (PMC11722115); Vaher 2026 *Gut Microbiology* (PMC13375144) — **Theirworld Edinburgh Birth Cohort** (preterm) | Very preterm neonates | 16S + WGS | Edinburgh DataVault, **controlled** [paper] | Controlled | Controlled (consent limits use to approved perinatal studies) [paper] | 147 neonates (2024); 73 with 9-month and 2-year outcomes (2026) [paper] | Bayley-III / neurodevelopment at 9 mo and 2 y; MRI [paper] |

### Considered, not ranked as longitudinal

- **Ferreiro 2023 *Sci Transl Med* 15:eabo2984 (PMID 37315112), preclinical AD, WashU Knight ADRC.** WGS, PRJNA798058, **164 WGS runs** [verified]. BioSample has no clinical fields [verified on SAMN25046680]. The profile page calls it a "cross-sectional study". News coverage says a 5-year follow-up has started [secondary]. Worth watching for a longitudinal release.
- **Chaudhari 2023 *GeroScience* (MiaGB pilot).** WGS, PRJNA912638 [paper]. The paper says the study is cross-sectional (48 subjects); the MiaGB consortium plans yearly follow-up.
- **Bauch 2025 *IJMS* 26:4735 (Tübingen, normal cognition → MCI over 4 years).** Shotgun per the Microbiome Repo listing, but PRJEB85717 has **only 1 run** in ENA [verified]. Not usable yet.
- **Vacaras 2026 *Microorganisms* (RRMS, shotgun, baseline + 1 y, n=29).** Data "available from the corresponding author upon request" [paper].
- **De Sciscio 2025 *npj Parkinson's Dis* (FMT-PD pilot, shotgun).** Data on request [paper].
- **Metcalfe-Roach 2024 *Mov Disord* (PD incidence and progression, shotgun).** Not open access. The GitHub code repo has no accession [verified]. Read availability unverified.

## Per-dataset notes

**1. GAINS (Zeamer).** This is the only candidate where repeated cognitive scores sit directly in the BioSample records. Columns seen: `study_id` (subject), `DaySample` (day since enrollment), `UnifiedNumber` (visit index), `cohort_subset`, `age`, `male`, `polypharm5`, `ADAS.COG.13`, `Memory_sum_Z`, `EF_sum_Z`. Collection date is a range (2020-01/2023-01). Caveats:
- A companion abstract (Huang 2025, PMC11710613) describes paired **oral** and fecal samples. The sample name I checked ends in `STL`, so filter on name suffix or `env_medium` before ingesting [inference].
- The 2025 preprint said data "will be deposited upon article acceptance". The 2026 *Gut Microbes* paper gives PRJNA1446836 [paper].
- An ENA "sample" count query returned 29, which does not match the 856 runs. Treat the sample count as unverified until it is pulled through NCBI.

**2. eLABE (Lee 2026).** Reads were sequenced on NovaSeq X 2×150 and deposited with human reads removed [paper]. PRJNA911205 also holds Warner 2023 *Nat Commun* maternal and infant data, including 16S runs. Subset to child WGS runs using Supplementary Table S1. Outcomes are Bayley-III, ITSEA and PAPA, plus social-disadvantage covariates. The exact ages of each outcome assessment are not spelled out in what I read beyond "at multiple ages" [paper]. License CC BY-NC-ND (article).

**3. RESONANCE (Bonham 2023).** Stool was sequenced at Dalhousie IMR on NextSeq 550 2×150 [paper]. Raw reads are not cited in the Sci Adv paper. PRJNA695570 comes from Peterson 2021 *Front Microbiol* ("Raw and processed data is available through SRA (NCBI BioProject PRJNA695570)"). Its BioSamples are RESONANCE samples from the Klepac-Ceraj lab with subject/timepoint fields, and the run count (1,767 WGS) far exceeds the 493 samples in Bonham 2023. That points to later uploads [inference]. The Dryad README says `complete_filtered_dataset.csv` "contains subject- and timepoint-associated metadata for all stool samples", keyed by `subject`, `timepoint` and the `omni` biospecimen ID. To confirm before ingesting:
- (a) that the cognitive score columns are in that CSV (code at github.com/Klepac-Ceraj-Lab/Resonance)
- (b) the `omni` ↔ SRA `sample_alias` (e.g., `C0324_3F_1A`) mapping.

ECHO data-sharing rules may apply to the richer phenotypes [inference].

**4. ASU MTT autism (Kang/Nirmalkar).** Open-label FMT, 10-week treatment, 2-year follow-up. The BioSample description field holds the group/timepoint (`MTT_10wk`, etc.), and `source_material_id` looks like a subject/visit code. The paper says "The study metadata and clinical data are available in Kang et al." Plan to curate the outcome tables by hand from the Kang 2017/2019 supplements [unverified that per-subject tables exist]. Kang 2017/2019 microbiome data were 16S (separate projects; see context table).

**5. Haran 2019 nursing-home AD.** BioSample titles encode subject, specimen number and collection day, so the longitudinal structure is recoverable. The outcome is dementia diagnosis rather than repeated cognitive scores. The paper's data statement says data are "available … upon written request", but reads are public in PRJNA529586. Per-sample AD status needs checking against the mBio supplementary data [unverified]. GAINS (#1) supersedes this cohort for cognitive scores.

**6. M4EFaD Bangladesh (Portlock 2025).** Open on three fronts:
- reads (SRA)
- lipidomics (MTBLS10066)
- processed EEG, Bayley, Wolke and anthropometry (figshare)

The public data are cross-sectional at 12 months. The trial protocol describes stool collection at 1, 2 and 3 years, so later releases may make it longitudinal [paper].

**7. NHBCS (Laue).** Large amplicon + WGS project. WGS covers only the 6-week and 1-year stools, and the neurobehavioral outcome (SRS-2 at 3 y) is not public. Useful only with a data-use agreement.

**8–11.** Reads are open but have no clinical linkage. Each needs an author request (see Gaps).

**12. TEBC preterm.** The most deeply phenotyped preterm neurodevelopment cohort with shotgun data, but access is controlled. Listed for completeness.

## 16S-only, for context (not usable by cMD)

| Study | Cohort / population | Outcome | Accession (as stated by paper) | Basis |
|---|---|---|---|---|
| Sordillo 2019 *JAMA Netw Open* 10.1001/jamanetworkopen.2019.0905 | VDAART infants | ASQ-3 at 3 y | not checked | search abstract (16S per abstract is not explicit — **unverified**) |
| Matsuyama 2022 (PMC9540001) | CHaRM, Brisbane toddlers | Bayley-III at 24 mo + longitudinal | not checked | abstract: "using 16S rRNA sequencing" |
| Davias 2025 (PMC11795817) | CHILD cohort | Bayley-III | not checked | title/abstract (metabolites + 16S; **sequencing type unverified**) |
| Kolobaric 2024 *Mol Psychiatry* (PMC11449789) | Korean older adults, 268 (70 at 2 y) | MMSE, depression (SGDS-K) at 2 y | not checked | paper figure: "amplicon sequence variant table" |
| Li N 2021 *Front Cell Infect Microbiol* (PMC8560686) | ASD FMT, China, 40 children | CARS, ABC, SRS at weeks 0/4/12 | PRJNA758217 | paper: "for 16s rRNA sequencing" |
| Kang 2017 / Kang 2019 *Sci Rep* (PMID 30967657) | ASU MTT | CARS etc. to 2 y | not checked | Nirmalkar 2022 describes prior MTT microbiome work as 16S [paper] |
| Aho 2019 | Finnish PD, 64+64, two stools ~2.25 y apart | PD progression | PRJEB27564 | BioProject text: "amplicon sequencing of the V3-V4" |
| Devolder 2023 *Gut Microbes* (PMC9980703) | Belgian MS, 111 | Long-term EDSS worsening | PRJEB45550 | paper: "Raw 16S rRNA amplicon sequencing" |
| Schwerdtfeger 2025 *Cell Rep Med* (PMC12047500) | CLIMB MS (Boston) | EDSS, MRI over 2 y | PRJNA1123247 | paper: "limited by the use of 16S sequencing" |
| Ghosh 2020 *Gut* NU-AGE | Older Europeans, 1-y MedDiet | Frailty, cognition | not public per Ghosh 2022 | Ghosh 2022 table lists NU-AGE as 16S |

## Gaps / what to ask authors for

1. **GAINS (Bucci/Haran, UMass).** Confirm stool vs oral sample flags, the total subject and sample counts, and whether CDR, MMSE and NIH Toolbox scores can be added to the BioSample records. Ask how GAINS overlaps with the PRJNA529586 nursing-home cohort.
2. **eLABE (Mitreva/Warner, WashU).** Get Supplementary Table S1 (sample ↔ SRR ↔ age ↔ Bayley/ITSEA/PAPA). Confirm which runs in PRJNA911205 are child WGS and whether any were resequenced (NovaSeq X runs vs the 2023 runs).
3. **RESONANCE (Klepac-Ceraj/Bonham, Wellesley).** Get the mapping from Dryad `omni` IDs to SRA samples, confirm the cognitive columns in `complete_filtered_dataset.csv`, and ask whether ECHO rules restrict redistributing those scores through cMD. Also ask about outcome linkage for Khula (PRJNA1128723) and the other cohorts in Fahur Bottino 2025.
4. **ASU MTT (Krajmalnik-Brown/Adams).** Get the per-subject, per-timepoint CARS/ABC/SRS/VABS-II table keyed to `source_material_id`.
5. **FMT-PD Finland (Scheperjans), MS onset (Rolla/Cordero, Turin), KD epilepsy (Prast-Nielsen/Dahlin).** Ask for a per-sample clinical table (visit, arm, MDS-UPDRS/EDSS/seizure response, and any cognitive tests such as MoCA) under whatever terms they allow.
6. **Ferreiro / Knight ADRC (Dantas/Ances).** Ask whether follow-up stool and longitudinal amyloid/cognition data will be deposited, and whether the PRJNA798058 metadata (amyloid/tau status, CDR) can be released at sample level.
7. **Bauch (Laske, Tübingen).** Ask when the remaining PRJEB85717 runs will be released, along with visit-level MCI conversion labels.
8. **Not searched in depth** (possible further leads): ADHD and depression shotgun trials with cognitive endpoints, post-stroke cognition (my impression is these are mostly 16S, unverified), Bonham/Klepac-Ceraj follow-up papers on RESONANCE, and Chinese aging cohorts with shotgun data and repeated cognition (e.g., Shen 2025 *Curr Dev Nutr*, 755 shotgun metagenomes; access unknown).

## Sources (kept)

- GAINS: PRJNA1446836 (ENA count; NCBI BioSample SAMN56833100); Zeamer 2025 PMC11952313; Zeamer 2026 PMC13203045 (data statement).
- eLABE: Lee 2026 PMC13718489 (data-sharing statement, methods); PRJNA911205 (ENA counts; BioSample SAMN32165325).
- RESONANCE: Bonham 2023 PMC10745691; Dryad 10.5061/dryad.fxpnvx0zq (README); Peterson 2021 *Front Microbiol* (PRJNA695570 statement); PRJNA695570 (ENA counts; BioSample SAMN17619207).
- MTT: Nirmalkar 2022 PMC9654974; PRJNA782533 (ENA count; BioSample SAMN23383816).
- Haran 2019 (PMID 31064831); PRJNA529586 (ENA count; BioSamples SAMN17216961, SAMN17216872).
- Portlock 2025 PMC11707170; PRJNA1087376 (ENA count; BioSample SAMN40442963).
- Laue 2020 PMC7511970; PRJNA296814 (ENA counts).
- Scheperjans 2024 PMID 39073834; PRJEB68317 (ENA count; BioSample SAMEA115136727).
- Dahlin 2024 PMC11570732; PRJEB28847, PRJEB49521 (ENA counts).
- Maglione 2026 PMC13688122; PRJNA1245671 (ENA count; BioSample SAMN47761366).
- Fahur Bottino 2025 (PMID 39809768); PRJNA1128723 (ENA count; BioSample SAMN43038867).
- Ferreiro 2023 (PMID 37315112); PRJNA798058 (ENA count; BioSample SAMN25046680).
- Deprioritized: Microbiome Repo (colorado.edu) summaries, which are machine-written and used only for discovery; news coverage (UMass, WashU, alzra.org), used only as secondary context.
