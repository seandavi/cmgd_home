# elabe: per-subject metadata notes

Study: eLABE (WashU), BioProject PRJNA911205. There are two papers on this BioProject:
- Lee 2026 *eBioMedicine* 133:106533, PMID 42913303, PMC13718489, doi 10.1016/j.ebiom.2026.106533. It covers the 836 newer child WGS specimens plus 69 older ones.
- Warner 2023 *Nat Commun* 14, PMID 37726348, PMC10509221, doi 10.1038/s41467-023-41421-4. It covers the 183 older mother/child WGS specimens ("Mother/Child status", "Dyad id" BioSamples).

Output: `subject_observations.tsv` has 13,743 rows (Lee S1: 12,675; Warner SD2: 1,068). There are no duplicate (subject, source_subject_id, biosample, visit, field, source) keys [verified]. To rebuild: `python3 -I scripts/build.py . <runs.tsv> <specimens.tsv>`.

## Sources (raw files landed whole)

| file | URL | sha256 | license |
|---|---|---|---|
| raw/epmc_PMC13718489/supp.zip (contains mmc1.pdf, mmc2.xlsx, mmc3.pdf, figures) | https://www.ebi.ac.uk/europepmc/webservices/rest/PMC13718489/supplementaryFiles | f5bb6140…a98906 | CC-BY-NC-ND-4.0 |
| raw/epmc_PMC13718489/mmc2.xlsx (Supplementary Tables S1–S10) | from the zip above | c82c25ea…b977 | CC-BY-NC-ND-4.0 |
| raw/epmc_fulltext_PMC13718489/fullTextXML.xml | https://www.ebi.ac.uk/europepmc/webservices/rest/PMC13718489/fullTextXML | f87b3ac8…eb48 | CC-BY-NC-ND-4.0 |
| raw/epmc_PMC10509221/supp.zip | https://www.ebi.ac.uk/europepmc/webservices/rest/PMC10509221/supplementaryFiles | 5345ff85…8906 | CC-BY-4.0 |
| raw/epmc_PMC10509221/41467_2023_41421_MOESM5_ESM.xlsx (Supplementary Data 2) | from the zip above | 0451eae9…0cfce607422502300821ce134b82eb62213e7fce6 | CC-BY-4.0 |

The full hashes are in the `source_sha256` column. `sha256sum raw/*/*` reproduces them.

Licenses:
- Lee 2026 is CC BY-NC-ND 4.0. The article XML says so, and Europe PMC reports `cc by-nc-nd` [verified]. Because of the ND clause, check before redistributing the derived table in a public repo.
- Warner 2023 is CC BY. Europe PMC reports `cc by` [verified].
- I assume the supplement license follows the article license [unverified].

## Lee 2026: Supplementary Table S1 ("Database of sample data including all relevant data")

What it has [verified]:
- 905 rows, one per sample. Each row has the Sample ID and the SRA run (SRR3599…/SRR36000…).
- Sample timepoint fields: `Actual timepoint (months)` and `Assigned time points` (4/8/12/24/36 MOL; 187/187/187/187/157).
- Maternal characteristics:
  - SD score: prenatal, Y1, Y2, Y3
  - INR: per trimester and average
  - Area Deprivation Index
  - race
  - maternal age at birth
  - BMI before pregnancy and at delivery
  - route of delivery
  - gestational age (weeks)
- Child characteristics: birth weight, sex, antibiotics in the last 7 days, and diet (breastfeeding, table/solid/fatty-sugary foods).
- Outcomes:
  - Bayley-III composite (Cognition, Language, Motor at 12/24/36 MOL)
  - ITSEA T-score (Externalizing, Internalizing, Dysregulation at 12/24/36 MOL)
  - PAPA symptom counts (Internalizing and Externalizing at 24/36 MOL)
- Also: raw read counts and 56 gut-brain-module CPMs.

There is no subject or individual ID column. The paper's models use an "Individual ID" random effect, but that ID is not in S1 [verified].

How I turned it into rows:
- **Per-sample fields** have `biosample` filled, `visit` = `Assigned time points`, and `age_days` = actual months × 30.4375, rounded to 0.1. The original months value is kept as the `Actual timepoint (months)` row. Per-sample fields are: Sample ID, actual/assigned timepoint, antibiotics and the four diet fields.
- **Subject-level fields** (maternal characteristics, child sex, GA, birth weight, outcomes) repeat on every sample of a child. I collapsed them to one row per child after checking that the non-missing values are identical within the child (0 conflicts) [verified].
  - Outcome rows get `visit` = "12 MOL"/"24 MOL"/"36 MOL" and a nominal `age_days` = months × 30.4375. These are nominal ages: exact assessment dates are not public.
  - SD rows get visit `Prenatal`/`Y1`/`Y2`/`Y3`. INR rows get visit `1st/2nd/3rd trimester`.
- **Field names:** the column names are verbatim. Where S1 has a group header over a column, I prefixed it as `<group header> | <column>`. Without that, ITSEA and PAPA would both have "Internalizing 24 MOL" and the names would collide.
- **Units** come from the column headers or group headers. PAPA's "symptom count" and maternal age "years" come from the paper text and Table 1 [verified].
- **Skipped:** cells that are blank or `-`. GBM CPMs and read counts are microbiome-derived, not clinical.

ID mapping [verified]:
- Each S1 SRR maps to a BioSample through runs.tsv, and that BioSample is in specimens.tsv: 905/905. The S1 Sample ID equals the SRA sample alias / specimen_name for 890 of them.
- For 15 rows at 24 MOL, S1 has a different `TB000…` Sample ID (e.g. TB0003018027 vs AB47608768 on SRR35999977). I joined these on the SRR, and the S1 ID is kept in the `Sample ID` row.
- `source_subject_id` = `<BioSample dyad id>|Child`. S1 has no subject ID, so the dyad comes from the BioSample `dyad_id` / `Dyad id` attribute, i.e. specimens.tsv `family_id`.
- Of the 905 samples, 69 are older Warner-deposit child specimens (all 4 MOL; specimens.tsv subject `<dyad>C`). The other 836 are the newer deposit. **specimens.tsv has blank `role` and `subject` for all 836 newer specimens**, so their per-sample rows have blank `subject`.
- For subject-level rows, I filled `subject` only when the child's samples include a Warner-deposit specimen that has a subject in specimens.tsv. The other samples in that dyad were judged to be the same child because S1 lists identical child/maternal values for them. Result: **69 of 187 children mapped, 118 unmapped**. Lee rows with `subject` filled: 2,599 of 12,675.
- Suggested fix, not applied: assign `<dyad_id>C` to the 836 newer specimens in specimens.tsv. S1 confirms they are all children. Dyads 19, 30 and 166 are the exception (next point). [inference]

**Contradictions with the BioSample/specimens data [verified]:**
- BioSample dyad ids **19, 30 and 166** each hold **two different children** in S1, with 5 samples each. The children differ in sex, gestational age, birth weight and prenatal SD, so they are not twins of one mother. It looks like a dyad-id collision or error in the newer deposit.
  - These children's subject-level values are emitted **per sample** (`biosample` filled) so the two children are never merged. `source_subject_id` is the same for both (`19|Child`, etc.), so tell them apart by biosample.
  - specimens.tsv `family_id` lumps them together.
- Missing-value coding in S1 is inconsistent:
  - Some BMI values are `-99` (33 rows, almost certainly a missing code).
  - Some INR/SD cells are `0` in one sample and `-` in other samples of the same child.
  - I kept the values verbatim. I collapsed after dropping `-`, so a child can end up with `0` where other samples had `-`. Treat INR `0` (56 rows) and BMI `-99` with caution.
- S1 has ITSEA "36 MOL" columns with values for 23 children. The paper text says ITSEA was given at 12 and 24 MOL only. I kept the values as given.
- specimens.tsv has blank `visit`, `age_days` and `collection_date` for all elabe specimens. S1 supplies the timepoint and actual age for 905 of them.

Group-level only (not in the table): the paper's Table 1 baseline means (n=187) and Supplementary Tables S2–S10 (model statistics).

## Warner 2023: Supplementary Data 2 ("Database of sample data, including all relevant metadata")

What it has [verified]:
- 242 rows: 121 mothers and 121 children.
- ID and sample fields: Sample ID, Mother/Child, Sex, "Age at time of sampling", Dyad ID, 16S accession, WMS accession.
- Antibiotic exposure: DOL and drug.
- Maternal metadata: SD score, Psychological Stress score, mother's IL-6 at T3.

How I turned it into rows:
- I used 179 rows whose WMS accession is in runs.tsv. Every one maps to the specimens.tsv biosample whose role and family_id match the row's Mother/Child and Dyad ID [verified, asserted in the build].
- `source_subject_id` = `<Dyad ID>|<Mother / Child>`.
- 179 subjects mapped, 0 unmapped. Sex/SD/PS/IL-6 are one row per subject. SD/PS/IL-6 are maternal values that the source repeats on the child rows, and I kept them on the child as given.
- I skipped the 63 rows that have only a 16S accession. They are not our specimens, and none of those subjects has a WGS specimen in specimens.tsv.

Contradictions:
- **Child ages:** Warner SD2 gives child "Age at time of sampling" as e.g. "4.1 weeks". The column header says "sampling at 4 months", and Lee S1 gives the same samples (e.g. AB46612145) 4.13 months. So "weeks" appears to be a mislabel for months [verified that the values disagree; the cause is inference]. I left `age_days` blank for Warner child rows. Maternal "N years" was converted at × 365.25.
- SRR22682846/SRR22682847 (dyad 28) have SRA aliases AB58058474b/AB58058474a. SD2 lists them as AB46601376 (mother) and AB58058474 (child). Role and dyad agree.
- Four of our Warner-deposit specimens are not in SD2: 7C, 7M, 135M and 135C (SAMN32165370/319/315/453). 135C does appear in Lee S1.
- Of our 91 Warner-deposit children, 22 have no Lee S1 sample.
- SD2 has a 16S-only "Child" row aged "27 years" (AB50650321a). It is excluded because it is not our specimen.

## Looked for, not found
- Exact assessment ages and dates for Bayley/ITSEA/PAPA: not public; only nominal 12/24/36 MOL [verified absent in S1].
- A subject or individual ID linking the 836 newer specimens to the paper's 187 "individuals": not in S1 or BioSample beyond the dyad id [verified].
- Maternal stool for the newer deposit: none; all 836 are child samples [verified via S1].
- Other deposits (dbGaP, NDA, Zenodo, figshare) for eLABE clinical data: the data-sharing statement points only to SRA plus S1. The only GitHub repository mentioned is GBM_mapping (code) [verified]. I did not search NDA directly [unverified].
- Lee "Supplementary Data" (R scripts) is not in the Europe PMC zip (only mmc1–3 PDFs/XLSX) [verified zip listing]. I did not open mmc1.pdf or mmc3.pdf (supplementary methods and figures; pdftotext is unavailable).
