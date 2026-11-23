# cmgd home

Home repo for curatedMetagenomicData (cMD): shared skills, cross-repo docs and
pointers to the repos that make up the system. Start agent sessions here.
Code, issues and history stay in each repo. Clone sibling repos next to this one.

Shared skills: `.claude/skills/` (`.agents/skills` links to it for pi/Codex).

## Other Repos

- Pipeline (Nextflow: QC, MetaPhlAn, HUMAnN, resistome): ../curatedMetagenomicsNextflow.
  Clone from https://github.com/seandavi/curatedMetagenomicsNextflow if missing. Read its CLAUDE.md and docs/adr first.
- Telemetry + orchestration (HPC dispatch, catalog, ETL, dashboard): ../nextflow_telemetry.
  Clone from https://github.com/seandavi/nextflow_telemetry if missing. Its CONTEXT.md is the system glossary.
- R client (cmgdr, reads public releases on cmgd-public.cancerdatasci.org): ../cmgdr.
  Clone from https://github.com/seandavi/cmgdr if missing.
- Sample metadata curation: ../curatedMetagenomicDataCuration.
  Clone from https://github.com/waldronlab/curatedMetagenomicDataCuration if missing. Owned by the Waldron lab: propose changes as PRs.
- metacurator (reproducible metadata curation from publications): ../metacurator.
  Clone from https://github.com/seandavi/metacurator if missing.
- Infrastructure (private): ../monode. Only infrastructure/terraform/apps/cmgd
  (DNS, R2) and projects/dags (cmgd assets) concern cMD.

## Data here

- data/longitudinal-neuro/: candidate longitudinal neuro cohorts (runs, readsets, specimens,
  per-subject observations). Read its README for the license split and known issues.

## Working across repos

- Each repo is cloned once; features get worktrees inside that clone.
- File issues in the repo that owns the change.
- Decisions that span repos: docs/adr/ here. Decisions about one repo: that repo's docs/adr.
