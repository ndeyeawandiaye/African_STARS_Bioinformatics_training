#!/usr/bin/env bash
# Shared settings, sourced by every script. Override any value from the shell, e.g.
#   THREADS=4 MIN_DEPTH=20 bash scripts/run_all.sh S01
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REF="${REF:-${ROOT}/data/reference/TOYV1.fasta}"
SAMPLE_SHEET="${SAMPLE_SHEET:-${ROOT}/data/samples.tsv}"
RESULTS="${RESULTS:-${ROOT}/results}"
THREADS="${THREADS:-2}"
MIN_DEPTH="${MIN_DEPTH:-10}"   # minimum depth to call a base (otherwise N)
MIN_BASEQ="${MIN_BASEQ:-20}"   # minimum base quality (Phred) used for the consensus
MIN_FREQ="${MIN_FREQ:-0.5}"    # a base must be seen in at least this fraction of reads

# Sample IDs: those given on the command line, otherwise every row of the sample sheet.
get_samples() {
  if [ "$#" -gt 0 ]; then printf '%s\n' "$@"; else tail -n +2 "$SAMPLE_SHEET" | cut -f1; fi
}

# Absolute path of the R1 / R2 file of a sample (columns 5 and 6 of the sample sheet).
fastq_r1() { awk -F'\t' -v s="$1" 'NR>1 && $1==s {print $5}' "$SAMPLE_SHEET" | sed "s#^#${ROOT}/#"; }
fastq_r2() { awk -F'\t' -v s="$1" 'NR>1 && $1==s {print $6}' "$SAMPLE_SHEET" | sed "s#^#${ROOT}/#"; }

# Stop with a clear message when a tool is missing.
need() {
  command -v "$1" >/dev/null 2>&1 || {
    echo "ERROR: '$1' not found. Did you activate the environment?  conda activate fastq2genome" >&2
    exit 1
  }
}
