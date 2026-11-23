# Longitudinal neuro cohorts: runs, readsets, specimens, subjects

Public shotgun stool metagenomes with neurocognitive, neurodevelopmental or neurological
outcomes, gathered 2026-11-23 for cMD. Candidates and ranking:
[`docs/research/longitudinal-neuro-cohorts-external.md`](../../docs/research/longitudinal-neuro-cohorts-external.md).
None of these is in cMD curation. Only `ms_onset_turin` is registered in telemetry
(collection `PRJNA1245671`); its 89 registered readset ids equal the ones here.

## Files

| File | One row per | Source |
|---|---|---|
| `studies.tsv` | study | hand-written (study_key, BioProject, PMID/DOI, outcome) |
| `runs.tsv` | WGS run | ENA portal `filereport` (AMPLICON runs dropped) |
| `readsets.tsv` | BioSample | all WGS runs of the BioSample; `readset_id` per ADR-0007, computed by `../nextflow_telemetry/src/nextflow_telemetry/readset.py` |
| `biosample_attributes.tsv.gz` | BioSample attribute | NCBI BioSample (EBI BioSamples for SAMEA); title, description and sample-name ids as `_title`, `_description`, `_id:<db>` |
| `specimens.tsv` | BioSample | derived: specimen type, role, family, subject, visit, days/age, with `basis` |
| `subject_observations.tsv.gz` | (subject, timepoint, field) value | BioSample (GAINS) + supplements/deposits under open licenses |
| `sources/<group>.md` | source group | what was found, where, sha256, license, id mapping, gaps |
| `local/` (gitignored) | | raw downloads, per-group builds, and observations we may not redistribute |

`subject_key = <study_key>:<subject>`; subject ids are never global. `specimens.basis` says how
each study's subject/time was derived: `stated` (own BioSample attribute), `parsed` (from a
name/title with an unambiguous pattern, codes confirmed against the paper), `inferred` (our
reading; check before relying on it). Rules and their evidence are comments in
`scripts/longitudinal_neuro/build_specimens.py`.

`subject_observations` columns: study_key, subject (ours, blank if unmapped), source_subject_id,
biosample (when the value belongs to one specimen), visit, days_from_baseline, age_days, field
(the source's column name, verbatim), value (verbatim), unit, source_url, source_file,
source_sha256, source_location, license. Values are not harmonized.

## License split

Rows go public only when the first token of `license` is CC0, CC-BY-4.0/3.0, MIT or INSDC.
Everything else (CC-BY-NC-ND, unknown) is written to `local/subject_observations.tsv.gz` and
stays out of this public repo:

| study | public | local only | why local |
|---|---|---|---|
| gains | ADAS-Cog-13, memory/EF z-scores per visit (BioSample) | | |
| elabe | Warner 2023 Supp. Data 2 (CC BY) | Lee 2026 S1: Bayley-III, ITSEA, PAPA, ages, covariates | CC BY-NC-ND |
| resonance | OSF `ybs32`: cogScore per visit, ages, sex, education, brain volumes | | |
| asu_mtt | Kang 2019 supplement: CARS, ABC, SRS, VABS-II, PGI, GSRS by visit | | |
| m4efad | figshare: Bayley-4, Wolke, EEG, anthropometry (enrolment) | 74 sample ages | CC BY-NC-ND |
| khula | | per-sample ages only | CC BY-NC-ND |
| haran_nh_ad | | dementia/AD status, meds, frailty (GitLab repo) | no license |
| ms_onset_turin | | EDSS at onset and 12 months, MRI flags | CC BY-NC-ND |
| kd_epilepsy_a/b | seizure/cognitive responder, diet ratio (8 and 12 subjects) | | |
| ferreiro_preclinical_ad | CDR, amyloid/tau, CSF, PET, APOE (cross-sectional) | | |
| fmt_pd_finland, nhbcs | nothing per subject is public | | |

## Rebuild

```bash
python3 -I scripts/longitudinal_neuro/fetch_runs.py data/longitudinal-neuro        # runs, readsets
python3 -I scripts/longitudinal_neuro/fetch_biosamples.py data/longitudinal-neuro  # ~5 min
python3 -I scripts/longitudinal_neuro/build_specimens.py data/longitudinal-neuro
# per-group builds read raw files under local/sources/<group>/raw (see sources/<group>.md):
#   python3 -I scripts/longitudinal_neuro/sources/elabe/build.py data/longitudinal-neuro/local/sources/elabe \
#     data/longitudinal-neuro/runs.tsv data/longitudinal-neuro/specimens.tsv
python3 -I scripts/longitudinal_neuro/build_observations.py data/longitudinal-neuro \
  data/longitudinal-neuro/local/sources/*/subject_observations.tsv
```

ENA and BioSample are live sources, so a rerun can differ. Raw supplement bytes exist only in
`local/`; capture them into `cmgd-private` through the telemetry source catalog
(`nf-meta sources`) before relying on them long term.

## Known issues

- eLABE dyads 19, 30 and 166 hold two children each; their Lee specimens have no subject.
- RESONANCE `FG…` specimens have no role or subject in BioSample, and their `host_age` is
  wrong (dropped). 196 of them link to subjects through the OSF sample id; the rest are unlinked.
  `cogScore` mixes MSEL/WPPSI/WISC without saying which.
- Haran: about a third of dementia values are a literal `#REF!`; 19 residents appear under two
  id spellings (CH1-101 / CH1101), kept separate.
- Khula: two paper ids are swapped between subjects; left unmapped.
- ms_onset_turin: 11 of the 69 MS patients were not treatment-naive (paper excluded them);
  37 of the paper's healthy donors come from PREDICT1 and have no stool here.
- GAINS and eLABE report `read_count` 0 for some runs in ENA (50 and 836): check before dispatch.
