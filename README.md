# From FASTQ to genome — hands-on dry lab

Practical session (≈ 3 h) of the NGS training (African STARS Fellowship / CARE / Institut Pasteur):
go from raw paired-end Illumina reads to a **consensus genome** and decide whether it is good enough
for phylogenetics (Day 4).

> **All data are synthetic.** A 10 kb toy virus (`TOYV1`) and five simulated samples. No real patient data.

## Repository map

| Path | Content |
|---|---|
| `data/` | reference (`reference/TOYV1.fasta`), FASTQ files, sample sheet (`samples.tsv`) |
| `scripts/` | pipeline steps `00`–`07` and `run_all.sh`; settings in `config.sh` |
| `exercises/` | step-by-step instructions and `answer_sheet.tsv` |
| `precomputed/` | plan B: BAM, coverage, consensus and QC summary |
| `solutions/` | instructor material (answers, truth) — **remove or publish only after the session** |
| `tools/` | data simulator and tools to regenerate `precomputed/` |

## Quick start

```bash
git clone <URL-OF-THE-REPO> fastq-to-genome && cd fastq-to-genome
mamba env create -f environment.yml      # or conda
conda activate fastq2genome
bash scripts/00_check_setup.sh
bash scripts/run_all.sh                  # whole pipeline, all samples
```

Visualisation: [IGV desktop](https://igv.org/doc/desktop/) or the [igv.org web app](https://igv.org/app)
(not in the conda environment).

## Session flow (3 h)

| Time | Part | File |
|---|---|---|
| 0:00–0:45 | Bridge talk: formats, sequencers, assembly strategies | slides |
| 0:45–1:00 | Setup | `exercises/00_setup.md` |
| 1:00–1:30 | FASTQ and QC | `exercises/01_fastq_and_qc.md` |
| 1:30–2:00 | Mapping | `exercises/02_mapping.md` |
| 2:00–2:45 | Coverage and consensus | `exercises/03_coverage_consensus.md` |
| 2:45–3:15 | Genome QC and verdict | `exercises/04_genome_qc_verdict.md` |

## The five samples

| Sample | What the participants should discover |
|---|---|
| S01 | a good genome (reference case) |
| S02 | good mean depth, but a large uncovered region |
| S03 | far too little data |
| S04 | many reads are not from the virus |
| S05 | negative control with reads in it |

## Plan B (no install possible)

Use `precomputed/`: open the BAMs in IGV, read `qc_summary.tsv`, and do exercises 03–04 from those files.
Regenerate the summary with `python3 scripts/07_summary.py --results precomputed`.

## Deliverables

Each participant (or pair) returns `exercises/answer_sheet.tsv` filled in: one verdict and a justification per sample.

## Troubleshooting

- `command not found`: the environment is not active → `conda activate fastq2genome`.
- Slow solver: use `mamba` (or `conda config --set solver libmamba`).
- Apple Silicon / Windows: use WSL2 on Windows; if a bioconda package is missing on ARM, use plan B.
- Re-run a single step on one sample: `bash scripts/03_map.sh S02`.

## Instructor notes

- Test the whole pipeline once on your own machine before the session. The shell scripts were written to be
  standard, but **they were not run end-to-end with the real tools during preparation**; `precomputed/` comes from a
  Python stand-in. Then run `tools/refresh_precomputed.sh` so plan B matches plan A.
- Regenerate the data (deterministic, seed 20261012): `python3 tools/simulate_data.py`, then
  `pip install -r tools/requirements.txt && python3 tools/make_precomputed.py`.
- Keep `solutions/` out of the participants' copy (private branch, or delete before sharing), and publish it afterwards.
- Choose a licence (e.g. MIT for code, CC BY 4.0 for the material) and add a `LICENSE` file.
- Day 4 and 5 can be added as `exercises/05_*.md` modules in the same repository.
