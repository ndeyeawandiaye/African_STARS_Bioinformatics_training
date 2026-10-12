#!/usr/bin/env bash
# Build the dataset (reference + outbreak genomes + your S01 consensus) and align it with MAFFT.
# Usage: bash scripts/11_align.sh [consensus.fa]     (default: results/consensus/S01.fa)
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/config.sh"
need mafft
CONS="${1:-${RESULTS}/consensus/S01.fa}"
OUT="${RESULTS}/phylo"; mkdir -p "$OUT"
[ -s "$CONS" ] || CONS="${ROOT}/precomputed/consensus/S01.fa"
echo "Using consensus: $CONS"
{ sed 's/^>.*/>TOYV1_ref/' "$REF"; cat "${ROOT}/data/outbreak/sequences.fasta"; cat "$CONS"; } > "${OUT}/all.fasta"
grep -c '>' "${OUT}/all.fasta"
mafft --auto --preservecase --thread "$THREADS" "${OUT}/all.fasta" > "${OUT}/aln.fasta"
echo "Alignment: ${OUT}/aln.fasta"
