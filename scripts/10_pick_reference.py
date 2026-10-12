#!/usr/bin/env python3
"""Compare a consensus genome with candidate reference genomes (same-length, ungapped toy genomes).

Usage: python3 scripts/10_pick_reference.py <consensus.fa> [candidate.fasta ...]
Default candidates: data/reference/candidates/*.fasta
For each candidate: compared sites (non-N), mismatches, identity %. Lowest mismatches = closest reference.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def read_fasta(p):
    name, seq = None, []
    for l in open(p):
        if l.startswith(">"):
            name = name or l[1:].split()[0]
        else:
            seq.append(l.strip().upper())
    return name, "".join(seq)


if len(sys.argv) < 2:
    sys.exit(__doc__)
qname, q = read_fasta(sys.argv[1])
cands = sys.argv[2:] or sorted(str(p) for p in (ROOT / "data/reference/candidates").glob("*.fasta"))
print(f"query: {qname} ({len(q)} bp, {q.count('N')} N)")
print("candidate\tcompared\tmismatches\tidentity_pct")
rows = []
for c in cands:
    name, r = read_fasta(c)
    if len(r) != len(q):
        print(f"{name}\t(different length: {len(r)})")
        continue
    comp = mism = 0
    for a, b in zip(q, r):
        if a in "ACGT" and b in "ACGT":
            comp += 1
            mism += a != b
    rows.append((mism, name, comp))
for mism, name, comp in sorted(rows):
    print(f"{name}\t{comp}\t{mism}\t{100 * (comp - mism) / comp:.2f}")
if rows:
    print("closest reference:", sorted(rows)[0][1])
