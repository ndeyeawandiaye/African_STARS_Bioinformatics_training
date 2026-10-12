#!/usr/bin/env python3
"""Assign each genome to a lineage from its defining SNPs (a miniature version of what Pangolin/Nextclade do).

A genome gets the most specific lineage whose defining SNPs are ALL present (position called, alt allele found);
SNPs on masked (N) positions are reported as 'missing' and the call becomes uncertain if too many are missing.
Usage: python3 scripts/13_lineage.py <alignment.fasta> [--out results/phylo/lineages.tsv]
"""
import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ap = argparse.ArgumentParser()
ap.add_argument("alignment")
ap.add_argument("--out", default=str(ROOT / "results/phylo/lineages.tsv"))
a = ap.parse_args()

seqs, n = {}, None
for l in open(a.alignment):
    if l.startswith(">"):
        n = l[1:].strip(); seqs[n] = []
    else:
        seqs[n].append(l.strip().upper())
seqs = {k: "".join(v) for k, v in seqs.items()}

defs, parent = {}, {}
for l in open(ROOT / "data/outbreak/lineage_definitions.tsv").read().splitlines()[1:]:
    lin, par, snps = l.split("\t")
    parent[lin] = par
    defs[lin] = [] if snps == "-" else [re.match(r"(\d+)([ACGT])>([ACGT])", s).groups() for s in snps.split(",")]


def chain(lin):                       # all SNPs of a lineage = its own + its ancestors'
    out = []
    while lin != "root":
        out = defs[lin] + out
        lin = parent[lin]
    return out


depth = lambda lin: 0 if lin == "root" else 1 + depth(parent[lin])
rows = []
for name, s in seqs.items():
    best, best_info = "unassigned", ""
    for lin in sorted(defs, key=depth, reverse=True):
        snps = chain(lin)
        present = missing = 0
        for pos, r, alt in snps:
            c = s[int(pos) - 1]
            present += c == alt
            missing += c not in "ACGT"
        total = len(snps)
        if total == 0:
            continue
        if present == total - missing and present >= 0.5 * total and present > 0:
            best, best_info = lin, f"{present}/{total} defining SNPs" + (f", {missing} masked" if missing else "")
            break
    if best == "unassigned":
        # no lineage with defining SNPs matched: root lineage if no defining SNP of any lineage is present
        any_alt = any(s[int(p) - 1] == al for l in defs for p, r, al in defs[l])
        best, best_info = ("TV.1", "no defining SNP of other lineages") if not any_alt else ("unassigned", "mixed / check")
    rows.append((name, best, best_info))

Path(a.out).parent.mkdir(parents=True, exist_ok=True)
with open(a.out, "w") as f:
    f.write("sample_id\tlineage\tevidence\n")
    for r in rows:
        f.write("\t".join(r) + "\n")
        print("\t".join(r))
