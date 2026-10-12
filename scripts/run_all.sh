#!/usr/bin/env bash
# Run the whole pipeline: QC -> trimming -> mapping -> coverage -> consensus -> variants -> genome QC summary.
# Usage: bash scripts/run_all.sh [sample ...]        (no argument = all samples)
set -euo pipefail
D="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
for step in 01_qc 02_trim 03_map 04_coverage 05_consensus 06_variants; do
  bash "${D}/${step}.sh" "$@"
done
python3 "${D}/07_summary.py" "$@"
