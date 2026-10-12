#!/usr/bin/env python3
"""Plan B without MAFFT. The toy genomes have no indels, so the 'alignment' is just the concatenated FASTA
(every sequence has the same length). Checks that lengths are equal and writes results/phylo/aln.fasta.
Usage: python3 scripts/11b_align_fallback.py [consensus.fa] [--results results]
"""
import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ap = argparse.ArgumentParser()
ap.add_argument("consensus", nargs="?", default=None)
ap.add_argument("--results", default=str(ROOT / "results"))
a = ap.parse_args()
cons = Path(a.consensus or Path(a.results) / "consensus/S01.fa")
if not cons.exists():
    cons = ROOT / "precomputed/consensus/S01.fa"


def records(p, rename=None):
    name, seq = None, []
    for l in open(p):
        if l.startswith(">"):
            if name:
                yield name, "".join(seq)
            name, seq = rename or l[1:].split()[0], []
        else:
            seq.append(l.strip().upper())
    if name:
        yield name, "".join(seq)


recs = list(records(ROOT / "data/reference/TOYV1.fasta", "TOYV1_ref"))
recs += list(records(ROOT / "data/outbreak/sequences.fasta"))
recs += list(records(cons))
lens = {len(s) for _, s in recs}
assert len(lens) == 1, f"sequences have different lengths: {lens}"
out = Path(a.results) / "phylo"
out.mkdir(parents=True, exist_ok=True)
with open(out / "aln.fasta", "w") as f:
    for n, s in recs:
        f.write(f">{n}\n{s}\n")
print(f"{len(recs)} sequences x {lens.pop()} sites -> {out / 'aln.fasta'}")
