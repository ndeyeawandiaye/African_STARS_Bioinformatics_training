#!/usr/bin/env bash
# Step 5 - Consensus genome from the mapped reads (iVar). Positions with depth < MIN_DEPTH become N.
# Usage: bash scripts/05_consensus.sh [sample ...]
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/config.sh"
need samtools; need ivar
OUT="${RESULTS}/consensus"; mkdir -p "$OUT"
for s in $(get_samples "$@"); do
  bam="${RESULTS}/bam/${s}.bam"
  [ -f "$bam" ] || { echo "ERROR: $bam missing - run 03_map.sh first" >&2; exit 1; }
  echo "[05_consensus] $s  (min depth ${MIN_DEPTH}, min base quality ${MIN_BASEQ}, min frequency ${MIN_FREQ})"
  samtools mpileup -aa -A -d 0 -Q 0 "$bam" \
    | ivar consensus -p "${OUT}/${s}.tmp" -q "$MIN_BASEQ" -t "$MIN_FREQ" -m "$MIN_DEPTH" -n N > /dev/null
  # give the sequence a clean name (the sample ID) instead of iVar's long header
  awk -v id="$s" 'NR == 1 { print ">" id; next } { print }' "${OUT}/${s}.tmp.fa" > "${OUT}/${s}.fa"
  rm -f "${OUT}/${s}.tmp.fa" "${OUT}/${s}.tmp.qual.txt"
done
echo "Done. Consensus genomes: ${OUT}/"
