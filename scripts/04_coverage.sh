#!/usr/bin/env bash
# Step 4 - Depth of coverage along the genome, and the regions below MIN_DEPTH.
# Usage: bash scripts/04_coverage.sh [sample ...]
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/config.sh"
need samtools
OUT="${RESULTS}/coverage"; mkdir -p "$OUT"
for s in $(get_samples "$@"); do
  bam="${RESULTS}/bam/${s}.bam"
  [ -f "$bam" ] || { echo "ERROR: $bam missing - run 03_map.sh first" >&2; exit 1; }
  echo "[04_coverage] $s"
  # one line per position: contig, position (1-based), depth  (-a keeps positions with zero depth)
  samtools depth -a "$bam" > "${OUT}/${s}.depth.tsv"
  samtools coverage "$bam" > "${OUT}/${s}.coverage.txt"
  # BED file of the stretches where depth < MIN_DEPTH (0-based, half-open)
  awk -v min="$MIN_DEPTH" 'BEGIN { OFS = "\t" }
       $3 < min { if (!on) { on = 1; start = $2 - 1; chr = $1 } last = $2; next }
       on       { print chr, start, last; on = 0 }
       END      { if (on) print chr, start, last }' "${OUT}/${s}.depth.tsv" > "${OUT}/${s}.low_depth.bed"
done
echo "Done. Depth tables and low-depth BED files: ${OUT}/"
