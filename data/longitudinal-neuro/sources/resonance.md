# resonance: Bonham 2023 *Sci Adv* 9:eadi0497 (PMID 38134274, PMC10745691)

## What I found

- **The Dryad files can't be downloaded anonymously.** [verified] The Dryad API v2 metadata is public: dataset version 302646, license CC0-1.0, 8 files with sha256 digests (saved as `raw/dryad/dataset.json` and `files.json`). Every `/api/v2/files/<id>/download` and `/api/v2/datasets/.../download` call returns 401 "must have current bearer token". The web `file_stream` URLs return an Anubis bot-challenge page. I did not try to get past either.
- **The same inputs are on OSF, and those are public.** [verified] OSF project `ybs32` ("ECHO RESONANCE Microbiome", license CC-By Attribution 4.0 via the OSF API). The Resonance repo's `Setup/src/download_locations.jl` names these files:
  - `/inputs/timepoints.tar.gz` (OSF `pva98`) contains `timepoints_metadata.csv`: 493 rows, 361 children. Columns: `subject, timepoint, ageMonths, sex, race, education, date, cogScore, sample, sample_base, read_depth, filter_00to120, filter_00to06, filter_18to120`. `Setup/bin/derive.jl` writes this file from kid rows (`isKid`, age ≤120 mo, cogScore present). It is the "uploads" table behind the Dryad deposit.
  - `/inputs/brain.tar.gz` (OSF `yatwr`) contains `brain_normalized.csv`: 180 visits, 157 subjects, 98 columns: 96 normalized FreeSurfer-style region volumes plus `Gray-matter` and `White-matter`. Its sha256 `b38d0a06…2e68` is **identical to the Dryad `brain_normalized.csv` digest**, so the same bytes are also on Dryad under CC0. [verified]
- **Not obtained: Dryad `complete_filtered_dataset.csv`** (6.9 MB, 401). From derive.jl it is probably the timepoints table joined with the taxa [unverified]. The OSF timepoints file already has the outcome and covariate columns.
- **Not public: Mullen subscales** (expressive language, gross motor, visual reception). The Figure 3 subscale scripts read them from the lab's internal metadata (`Resonance.load(Metadata())`, column `Mullen::mullen_ExpressivelanguageT`). They are not in the OSF/Dryad inputs. [verified in code]
- **Paper supplements** (Europe PMC zip: figures plus `sciadv.adi0497_sm.pdf`; Resonance repo `manuscript/assets/TableS1-6.csv`) hold model importances and benchmarks only. No per-subject data. [verified for the CSVs; the PDF contents were checked via `supplement.tex` in the repo, since there is no pdftotext]. Table 1 in the paper is a summary table, so it is not in this table.
- **Other Klepac-Ceraj-Lab repos** [verified; no license file, so "unknown"]:
  - `echo_metadata/master_fecal_samples.csv`: sample logistics keyed on `C0052_5F_1A`-style ids (collection dates, batches). No outcomes.
  - `VKCComputing.jl/sra/*.tsv`: SRA submission sheets for the C/M-named runs (SRR ↔ SAMN ↔ sample_name, subject, timepoint).

  Neither has FG ids, so neither is in the table.

## Contents of `subject_observations.tsv`

- 23,117 rows: 5,477 from timepoints and 17,640 from brain.
- Timepoints fields:
  - Subject-level, with blank visit: `sex`, `race`, `education`. The paper uses `education` as maternal education. I checked that each is constant within a subject.
  - Visit-level: `ageMonths` (unit months) and `cogScore`. There are 489 cogScore rows for 361 children.
  - Sample-level: `date`, `sample`, `sample_base`, `read_depth`, `filter_*`.
- `cogScore` is the full-scale composite from MSEL (<4 y), WPPSI-4 or WISC-V (>6 y), normalized to a common scale (`raw/github_Resonance/main.tex`). The file doesn't say which instrument each row used, and I did not infer it.
- `age_days` = `ageMonths` × 30.4375. The source's months look like days×12/365 (for example, 98.4931 mo = 2995.8 d), so this conversion adds about +0.07% (≈2 days at 8 y). `ageMonths` is the age at the stool/timepoint. Whether the cognitive test happened on the same day is [unverified].
- Brain rows have visit set but `age_days` blank, because the file drops `AgeInDays`.

## ID mapping

- The source `subject` is the family number. All rows are children (derive.jl `isKid` filter). Our child subject is `C<n>` (e.g. `C0052_5F_1A` → `C52`). I filled `subject = "C"+int(subject)` only when that value exists in specimens.tsv.
  - Timepoints: 293 of 361 children mapped.
  - Brain: 156 of 157 mapped.
- `sample_base` is an `FG#####` seqprep id. 198 of 493 rows match a specimens.tsv `specimen_name` exactly (196 BioSamples; FG00016 has 2 tech-rep rows). For all 198, BioSample `subject_id`/`timepoint` equal the source subject/timepoint [verified]. `biosample` is filled only for these exact matches, and only on sample-level fields.
- The other 295 rows have no FG BioSample. For each one, a C-named child specimen exists at the same (family, visit), and its collection_date matches the source `date` in 351 of 356 visit matches. That suggests the same physical sample under its collection name, but no source documents an FG ↔ C-name key. So `biosample` is left blank there [unverified join].

## Contradictions with specimens.tsv

- **789 FG-named specimens have blank `role` and `subject`.** All 68 unmapped children own FG specimens in our table. The source treats these as kid samples. Assigning them `C<n>` would map every subject [inference].
- **`host_age` on FG-named BioSamples looks wrong.** For the 61 FG specimens with an age that match the source, specimens `age_days` differs from the source `ageMonths` by up to about 3,500 days. For example, FG00211 is 3.39 mo in the source but 3,628.6 d in the BioSample, while collection dates agree. C-named child specimens agree with the source (330 of 354 within 31 days). FG `age_days` also disagrees with the C-named specimen at the same visit in 38 of 38 cases. [verified] Don't trust FG `age_days`.

## Licenses

| Source | License |
|---|---|
| OSF timepoints and brain | CC-BY-4.0 (node license) [verified] |
| Dryad copy of brain_normalized | CC0-1.0 [verified via API] |
| Resonance code | MIT |
| echo_metadata, VKCComputing | unknown (no license) |
| Article supplements | per Sci Adv (CC BY 4.0 article license) [unverified] |

## Raw files (URL, sha256)

- `raw/osf_ybs32/timepoints.tar.gz` (https://osf.io/download/pva98/): 398e7141e7c1858d03e7aed0d9c50fc74e510d6d67c51744fba41dc0b733e370
  - `extracted/timepoints_metadata.csv`: d3db84efee1ca578102e4abcfa779e3a4e408b1557f94e835a79c0527f972b41
- `raw/osf_ybs32/brain.tar.gz` (https://osf.io/download/yatwr/): c170c6d13290d2da5fcbb3dce6a8a065eb5eb997dfbca499f458aed8d1e51ded
  - `extracted/brain_normalized.csv`: b38d0a06adf5e3b0a8d45386a1042e9dbb2dc3af5f8483245a3d9d1d33a32e68
- `raw/dryad/dataset.json` (https://datadryad.org/api/v2/datasets/doi%3A10.5061%2Fdryad.fxpnvx0zq): 3c7a475c…2e74
- `raw/dryad/files.json` (https://datadryad.org/api/v2/versions/302646/files): c03ce752…2949
- `raw/europepmc_PMC10745691/supp.zip` (Europe PMC supplementaryFiles): df946dc7…4e13
- `raw/github_Resonance/TableS{1..6}.csv` (raw.githubusercontent.com/Klepac-Ceraj-Lab/Resonance/HEAD/manuscript/assets/)
- `raw/github_echo_metadata/master_fecal_samples.csv`: 08bb25a2…f3fa
- `raw/github_VKCComputing/metadata-{8908067,9353778}-processed-ok.tsv` (…/VKCComputing.jl/HEAD/sra/)

Rebuild: `python3 -I scripts/build_observations.py raw/osf_ybs32/extracted/timepoints_metadata.csv raw/osf_ybs32/extracted/brain_normalized.csv <specimens.tsv> subject_observations.tsv`
