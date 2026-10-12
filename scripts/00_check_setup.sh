#!/usr/bin/env bash
# Step 0 - Is everything installed and are the data where they should be?
set -u
source "$(dirname "${BASH_SOURCE[0]}")/config.sh"
bad=0
echo "== Tools =="
for t in fastqc multiqc fastp minimap2 samtools bcftools ivar python3; do
  if command -v "$t" >/dev/null 2>&1; then printf '  %-9s OK\n' "$t"; else printf '  %-9s MISSING\n' "$t"; bad=1; fi
done
echo "== Data =="
for f in "$REF" "$SAMPLE_SHEET"; do
  if [ -f "$f" ]; then echo "  OK       ${f#"$ROOT"/}"; else echo "  MISSING  $f"; bad=1; fi
done
for s in $(get_samples); do
  for f in "$(fastq_r1 "$s")" "$(fastq_r2 "$s")"; do
    if [ -f "$f" ]; then echo "  OK       ${f#"$ROOT"/}"; else echo "  MISSING  $f"; bad=1; fi
  done
done
if [ "$bad" -eq 0 ]; then echo "All good - you are ready."; else echo "Something is missing: ask an instructor."; exit 1; fi
