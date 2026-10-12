#!/usr/bin/env python3
"""Plan B without IQ-TREE: a neighbour-joining tree from SNP distances (needs biopython).
Writes results/phylo/tree.nwk. NJ is a distance method: fine for a first look, not a substitute for ML + bootstrap.
Usage: python3 scripts/12b_tree_fallback.py [--results results]
"""
import argparse
from pathlib import Path
from Bio import Phylo
from Bio.Phylo.TreeConstruction import DistanceMatrix, DistanceTreeConstructor

ROOT = Path(__file__).resolve().parent.parent
ap = argparse.ArgumentParser()
ap.add_argument("--results", default=str(ROOT / "results"))
a = ap.parse_args()
aln = Path(a.results) / "phylo/aln.fasta"


def read(p):
    d, n = {}, None
    for l in open(p):
        if l.startswith(">"):
            n = l[1:].strip(); d[n] = []
        else:
            d[n].append(l.strip().upper())
    return {k: "".join(v) for k, v in d.items()}


seqs = read(aln)
names = list(seqs)


def dist(x, y):
    comp = diff = 0
    for a_, b_ in zip(x, y):
        if a_ in "ACGT" and b_ in "ACGT":
            comp += 1
            diff += a_ != b_
    return diff / comp if comp else 0.0


m = [[dist(seqs[names[i]], seqs[names[j]]) for j in range(i + 1)] for i in range(len(names))]
tree = DistanceTreeConstructor().nj(DistanceMatrix(names, m))
tree.root_with_outgroup("TOYV1_ref")
Phylo.write(tree, Path(a.results) / "phylo/tree.nwk", "newick")
print("NJ tree ->", Path(a.results) / "phylo/tree.nwk")
