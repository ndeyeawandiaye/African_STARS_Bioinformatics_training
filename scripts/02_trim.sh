#!/usr/bin/env bash
# Step 2 - Trim adapters and low-quality tails (fastp). Also produces an HTML QC report per sample.
# Usage: bash scripts/02_trim.sh [sample ...]
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/config.sh"
need fastp
OUT="${RESULTS}/trimmed"; QC="${RESULTS}/qc_trimmed"; mkdir -p "$OUT" "$QC"
for s in $(get_samples "$@"); do
  r1="$(fastq_r1 "$s")"; r2="$(fastq_r2 "$s")"
  [ -f "$r1" ] && [ -f "$r2" ] || { echo "ERROR: FASTQ files of '$s' not found" >&2; exit 1; }
  echo "[02_trim] $s"
  fastp -i "$r1" -I "$r2" \
        -o "${OUT}/${s}_R1.fastq.gz" -O "${OUT}/${s}_R2.fastq.gz" \
        --detect_adapter_for_pe \
        --cut_tail --cut_tail_mean_quality 20 \
        --qualified_quality_phred 20 --length_required 50 \
        --thread "$THREADS" \
        --html "${QC}/${s}.fastp.html" --json "${QC}/${s}.fastp.json" 2> "${QC}/${s}.fastp.log"
done
echo "Done. Trimmed reads: ${OUT}/   Reports: ${QC}/"
