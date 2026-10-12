# precomputed/ — plan B

Ready-made outputs for the five samples, so the session can continue if a tool will not install.

| Folder / file | Content |
|---|---|
| `bam/` | sorted, indexed paired-end alignments (`S0X.bam`, `.bai`) and `flagstat` |
| `coverage/` | per-base depth (`S0X.depth.tsv`) |
| `consensus/` | consensus genome per sample (`S0X.fa`) |
| `qc_summary.tsv` | one-line verdict per sample |

These files were generated with a Python stand-in (minimap2 via `mappy`, samtools via `pysam`) using the same
thresholds as the shell pipeline (depth ≥ 10, base quality ≥ 20, frequency ≥ 0.5). Small differences with a run of
iVar are possible. Instructors: replace them with a real run using `tools/refresh_precomputed.sh`.

Use them with: `python3 scripts/07_summary.py --results precomputed`
