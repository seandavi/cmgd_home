# m4efad_khula: per-subject metadata notes

Build: `scripts/.venv/bin/python -I scripts/build.py . <specimens.tsv>` writes `subject_observations.tsv`
(24,734 rows). The venv in `scripts/.venv` has only openpyxl and polars, because the system python3 has no openpyxl.

## m4efad (Portlock 2025, Nat Commun 16:473, PMC11707170)

**Found**
- [verified] figshare 10.17608/k6.auckland.25560768 (v1, the only version) has per-subject TSVs keyed by `ID` (LCC####). The license is **CC BY 4.0** (figshare API). I downloaded and loaded these files whole: `meta.tsv` (234 IDs, 73 fields: sex, `Condition` MAM/Well-nourished, delivery mode, breastfeeding, household SES/WASH), `anthro.tsv` (234; Weight, MUAC, HC, WLZ_WHZ), `bayley.tsv` (221; 5 BSID-IV domain scores), `wolkes.tsv` (217; 5 Wolke dimensions) and `psd.tsv` (175; 23 regional EEG band PSDs). All figshare MD5s matched the API's `computed_md5`.
- [verified] The paper says anthropometry, Bayley and EEG "were collected upon enrolment" at 12 ± 1 months. So I set `visit=enrolment` for anthro, bayley, wolkes and psd rows. meta rows have a blank visit. Units come from the paper: kg/cm for anthropometry, and PSD in µV²/Hz, log10-transformed. Bayley and Wolke units are blank. The Bayley values look like raw scores, but the source doesn't say [unverified].
- [verified] Per-sample age: the Khula paper's source data (PMC11733223 MOESM5, sheet `Figure1B`, datasource `1kDLEAP-M4EFAD`) gives `ageMonths` for 74 M4EFaD stools, keyed by `sample`=C### (our `specimen_name`) and `subject_id`=`m4efad-LCC####`. Its code (`raw/github_microbiomeagemodel2024/allcohorts_data_loading_nofeed.jl`) computes `ageMonths = samplingAge/30.5`. For these rows I therefore set `age_days = ageMonths × 30.5`, **not** the brief's ×30.4375. All 74 come out as integer days (asserted in build.py). Range: 10.95–13.28 months. That sheet's license is the article's, CC BY-NC-ND 4.0.
- Not included: `quality.tsv` (HQ read depth, sequencing QC; I used it only for the check below) and the microbiome, lipid and pathway profiles.

**Mapping** [verified]: figshare `ID` matches BioSample `host_subject_id` (= our `subject`) exactly.
- 229 of our 230 subjects are mapped.
- One of ours has no figshare data: **LCC3072** (SAMN40442949, C246).
- Five figshare IDs have no SRA sample and stay unmapped: LCC1013, LCC1111, LCC1158, LCC2009, LCC2031.
- MOESM5 M4EFaD rows: 73 of 74 map (C### and LCC id both match). C202/`m4efad-LCC2031` is not in PRJNA1087376.

**Contradiction to flag**:
- [verified] `quality.tsv` lists LCC2031 with 35.46 M HQ reads and has no LCC3072. Our BioSample C246 says LCC3072, with 9.56 M read pairs (19.1 M reads) in the ENA run.
- [verified] For the 229 matched subjects, HQ reads ≤ raw reads in every case.
- [unverified] So figshare's LCC2031 is not C246's data. I can't tell whether LCC3072 is a mislabel; left unmapped.

**Not per-subject**: MOESM3 Supplementary Data 1 (Table 1 group means), and Data 2–11 (model and differential results). The trial protocol plans stool at 1, 2 and 3 y, but only the 12-month timepoint is public [verified: all 230 BioSamples have `subject_age_months`=12].

## khula (Fahur Bottino 2025, Nat Commun 16:660, PMC11733223)

**Found**
- [verified] Data availability points to Dryad 10.5061/dryad.dbrv15f9z (CC0), Zenodo 10.5281/zenodo.12822332 (redirects to record 14603451, a code zip, MIT) and GitHub Klepac-Ceraj-Lab/MicrobiomeAgeModel2024 (code only; data is pulled from S3 presigned URLs that have expired, HTTP 400).
- [verified] MOESM5 source data: `Figure1B` (427 Khula samples) and `Figure2A` (426; adds `visit`) give `subject_id` (`khula-191-<8 digits>`), `sample` (SEQ#####) and `ageMonths` per stool. I wrote one `ageMonths` row per sample, with `age_days = ageMonths × 30.4375` and `visit` taken from Figure2A. One sample is missing from Figure2A, so its visit is blank. Ages agree between the two sheets (asserted). Range by visit: 3mo 2.13–5.34, 6mo 5.38–11.9, 12mo 11.63–17.97 months.
- MOESM3 is the STORMS checklist plus a consortium list, with no subject data [verified].

**Not public / not found**
- **No neurodevelopmental outcomes for Khula are in this paper or its deposits** [verified for MOESM3/5 and the GitHub tree]. This paper is age-prediction only.
- Dryad file downloads are blocked for scripts: the API returns 401 "must have current bearer token", and the web `file_stream` sits behind an Anubis bot check. I got only the file list (`raw/dryad_khula/files.json`): `inputs_with_testdata.csv`, `ecs_metadata.csv`, `visit_annotation_glossary.xlsx`, taxonomic inputs and model .jld files. These look like age plus taxa, not outcomes [unverified]. They would need a browser or token download.
- Related Khula papers that do carry neuro outcomes (outside the assigned paper, so I only checked them):
  - Codevelopment of microbial metabolism and VEP (PMC12345167): data on Dryad via scripts, code at Zenodo 13625448/GitHub EEGMicrobiome. The repo has only FSEA summary CSVs [verified].
  - Microbiome–behavior coupling / PCI (PMC13269231): says subject demographics are on Dryad 10.5061/dryad.15dv41p9k. That DOI currently returns "cannot be viewed" (not yet public) [verified]. GitHub PCIVEPMBiome2024 has only `data/samples.txt`.
  - Both are worth revisiting for VEP/PCI per-subject data.

**Mapping** [verified, documented key chain]:
- Chain: MOESM5 `sample` (SEQ#####) → ENA `library_name` for PRJNA1128723 (`raw/ena_khula/filereport.tsv`; all 427 found) → BioSample → our `subject` (from BioSample titles in specimens.tsv). Visit agrees with specimens.tsv for every sample (0 mismatches).
- 248 of our 252 subjects are mapped; 419 of 427 rows have `subject`.
- **9 biosamples whose titles lack a subject** (blank `subject` in specimens.tsv, all 3mo, Z3MO-*) got `subject` through other samples sharing the same `khula-191-*` id. None of those subjects already has a 3mo sample. This disagrees with specimens.tsv (blank there). Examples: SAMN43038866→2ylen545a1uhz, SAMN43038867→kisnlttt1o8y.
- 1 biosample with no title subject (SAMN43038873, `khula-191-44859353`) has no siblings, so it stays unmapped.
- **Conflicts with BioSample titles; I left these unmapped**:
  - `khula-191-30130345` / `khula-191-30172716` are swapped between our subjects 2cg5oggqhmemi and 3i5sgvcl1w2ln. 3mo: SEQ00369→2cg5, SEQ00462→3i5s. 12mo: SEQ03087 (30172716)→2cg5, SEQ03151 (30130345)→3i5s.
  - Our yi7q65a8o7fo is reached from both `khula-191-40983013` (3mo, 6mo) and `khula-191-40983031` (12mo). This looks like a digit transposition [unverified].
- 2 of our biosamples are not in the source data: SAMN43292897 and SAMN43293012.

## Sources (URL → file, sha256, license)
| file | URL | sha256 | license |
|---|---|---|---|
| raw/figshare_m4efad/meta.tsv | https://ndownloader.figshare.com/files/51155876 | 2b2aed61cd08527a6c9a6eed0d7c9cd85d786e621d5db8e0aff9e81fd0990590 | CC-BY-4.0 |
| raw/figshare_m4efad/anthro.tsv | https://ndownloader.figshare.com/files/51155849 | 0904d136a5572e65f7bb5fadd0c5499cc98304584f4f18d0b0f67297db31bd8c | CC-BY-4.0 |
| raw/figshare_m4efad/bayley.tsv | https://ndownloader.figshare.com/files/51155852 | 6c54d9d1d2fd6dad3729175d898f4c0720f9505161bb6804298756dbb51fdb59 | CC-BY-4.0 |
| raw/figshare_m4efad/wolkes.tsv | https://ndownloader.figshare.com/files/51155843 | 92863bf660d59cab217551284a05c9322b7b1c3414c4d31f61cccf276bfef14c | CC-BY-4.0 |
| raw/figshare_m4efad/psd.tsv | https://ndownloader.figshare.com/files/51155846 | 5c90c4b1fe4be270733a0648138b2c134149d492db460b9f0fd57ba3546d320c | CC-BY-4.0 |
| raw/figshare_m4efad/quality.tsv | https://ndownloader.figshare.com/files/51155873 | fe0e624c6af9d126f0241ebf5bab663de876fb498cc71461fca6682c0dc8785a | CC-BY-4.0 |
| raw/europepmc_khula/41467_2025_56072_MOESM5_ESM.xlsx | https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11733223/supplementaryFiles (zip) | 46cb999fd869c10fc2094e74b7aa8d578dfaf537144a0ba4fe848858d8d65190 | CC-BY-NC-ND-4.0 (article license; no separate supplement license) |
| raw/europepmc_m4efad/41467_2024_55798_MOESM3_ESM.xlsx | https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11707170/supplementaryFiles (zip) | 06f129e5283acc854de89551ce999390ae9b88f2dd55c48abbd2da281a0d78c2 | CC-BY-NC-ND-4.0 (article) |
| raw/ena_khula/filereport.tsv (mapping only) | see raw/ena_khula/URL.txt | 6cb8fe6053a2c5f42cd50302d46d4df7c24f4cecc03ea60ef33ee1dc6945bc0b | INSDC (unrestricted) |
| raw/ena_m4efad/filereport.tsv (check only) | see raw/ena_m4efad/URL.txt | cb148943c0d17ce8b03f838475d592aa820e2ec506538fbf5be1c327e9ea7b62 | INSDC (unrestricted) |

Redistribution: the figshare rows (CC BY 4.0) can go in a public repo with attribution. The MOESM5 age rows are CC BY-NC-ND 4.0 by the article license, which makes them questionable in a public repo; the same data is on CC0 Dryad, if someone can download it.
