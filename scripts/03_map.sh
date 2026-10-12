#!/usr/bin/env bash
# Step 3 - Map the trimmed reads to the reference (minimap2, short-read preset), sort and index the BAM.
# Usage: bash scripts/03_map.sh [sample ...]
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/config.sh"
need minimap2; need samtools
OUT="${RESULTS}/bam"; mkdir -p "$OUT"
for s in $(get_samples "$@"); do
  r1="${RESULTS}/trimmed/${s}_R1.fastq.gz"; r2="${RESULTS}/trimmed/${s}_R2.fastq.gz"
  [ -f "$r1" ] && [ -f "$r2" ] || { echo "ERROR: trimmed reads of '$s' missing - run 02_trim.sh first" >&2; exit 1; }
  echo "[03_map] $s"
  minimap2 -ax sr -t "$THREADS" -R "@RG\tID:${s}\tSM:${s}" "$REF" "$r1" "$r2" 2> "${OUT}/${s}.minimap2.log" \
    | samtools sort -@ "$THREADS" -o "${OUT}/${s}.bam" -
  samtools index "${OUT}/${s}.bam"
  samtools flagstat "${OUT}/${s}.bam" > "${OUT}/${s}.flagstat.txt"
done
echo "Done. BAM + index: ${OUT}/   (open them in IGV)"
