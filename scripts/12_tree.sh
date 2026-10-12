#!/usr/bin/env bash
# Maximum-likelihood tree with IQ-TREE 2 (ultrafast bootstrap), rooted on the reference genome.
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/config.sh"
need iqtree2
OUT="${RESULTS}/phylo"
[ -s "${OUT}/aln.fasta" ] || { echo "Run scripts/11_align.sh first"; exit 1; }
iqtree2 -s "${OUT}/aln.fasta" -m MFP -B 1000 -T "$THREADS" --seed 1 -o TOYV1_ref --prefix "${OUT}/tree" -redo
echo "Tree: ${OUT}/tree.treefile"
