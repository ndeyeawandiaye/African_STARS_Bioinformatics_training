#!/usr/bin/env bash
# Step 6 (optional) - Call variants against the reference and write a VCF (bcftools).
# Remember: a VCF lists the variants that were called, but it does NOT replace the BAM for inspecting the alignments.
# Usage: bash scripts/06_variants.sh [sample ...]
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/config.sh"
need bcftools; need samtools
OUT="${RESULTS}/variants"; mkdir -p "$OUT"
for s in $(get_samples "$@"); do
  bam="${RESULTS}/bam/${s}.bam"
  [ -f "$bam" ] || { echo "ERROR: $bam missing - run 03_map.sh first" >&2; exit 1; }
  echo "[06_variants] $s"
  bcftools mpileup -f "$REF" -d 10000 -Q "$MIN_BASEQ" "$bam" 2> /dev/null \
    | bcftools call -mv --ploidy 1 -Ov -o "${OUT}/${s}.vcf" 2> /dev/null
  echo "  $(grep -vc '^#' "${OUT}/${s}.vcf") variant(s) called"
done
echo "Done. VCF files: ${OUT}/"
