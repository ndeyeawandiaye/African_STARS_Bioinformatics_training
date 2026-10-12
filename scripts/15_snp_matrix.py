#!/usr/bin/env python3
"""Pairwise SNP distances between genomes of an alignment (N / gaps ignored; compared sites reported).
Usage: python3 scripts/15_snp_matrix.py <alignment.fasta> [--out results/phylo/snp_matrix.tsv] [--ids S01,OB03,...]
"""
import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ap = argparse.ArgumentParser()
ap.add_argument("alignment")
ap.add_argument("--out", default=str(ROOT / "results/phylo/snp_matrix.tsv"))
ap.add_argument("--ids", default="")
a = ap.parse_args()
seqs, n = {}, None
for l in open(a.alignment):
    if l.startswith(">"):
        n = l[1:].strip(); seqs[n] = []
    else:
        seqs[n].append(l.strip().upper())
seqs = {k: "".join(v) for k, v in seqs.items()}
ids = [i for i in a.ids.split(",") if i] or list(seqs)
Path(a.out).parent.mkdir(parents=True, exist_ok=True)
with open(a.out, "w") as f:
    f.write("\t" + "\t".join(ids) + "\n")
    for i in ids:
        row = []
        for j in ids:
            row.append(str(sum(1 for x, y in zip(seqs[i], seqs[j]) if x in "ACGT" and y in "ACGT" and x != y)))
        f.write(i + "\t" + "\t".join(row) + "\n")
print("SNP matrix ->", a.out)
