#!/usr/bin/env bash
# Step 1 - Quality control of the RAW reads (FastQC for each file, MultiQC for the overview)
# Usage: bash scripts/01_qc.sh [sample ...]        (no argument = all samples)
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/config.sh"
need fastqc; need multiqc
OUT="${RESULTS}/qc_raw"; mkdir -p "$OUT"
for s in $(get_samples "$@"); do
  r1="$(fastq_r1 "$s")"; r2="$(fastq_r2 "$s")"
  [ -f "$r1" ] && [ -f "$r2" ] || { echo "ERROR: FASTQ files of '$s' not found (check data/samples.tsv)" >&2; exit 1; }
  echo "[01_qc] $s"
  fastqc -q -t "$THREADS" -o "$OUT" "$r1" "$r2"
done
multiqc -q -f -o "$OUT" "$OUT"
echo "Done. Open ${OUT}/multiqc_report.html in a browser."
