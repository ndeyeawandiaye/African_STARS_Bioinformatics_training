#!/usr/bin/env bash
# Instructor tool: run the REAL pipeline (needs the conda env) and copy its outputs into precomputed/,
# replacing the Python stand-in outputs. Run once before the session to make plan B match plan A exactly.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
bash scripts/run_all.sh
rm -rf precomputed && mkdir -p precomputed/{bam,coverage,consensus,variants}
for s in $(tail -n +2 data/samples.tsv | cut -f1); do
  cp results/bam/$s.bam results/bam/$s.bam.bai precomputed/bam/ 2>/dev/null || true
  cp results/bam/$s*.flagstat.txt precomputed/bam/ 2>/dev/null || true
  cp results/coverage/$s* precomputed/coverage/ 2>/dev/null || true
  cp results/consensus/$s* precomputed/consensus/ 2>/dev/null || true
  cp results/variants/$s* precomputed/variants/ 2>/dev/null || true
done
cp results/qc_summary.tsv precomputed/
echo "precomputed/ refreshed from a real run. Check file names against exercises/ and commit."
