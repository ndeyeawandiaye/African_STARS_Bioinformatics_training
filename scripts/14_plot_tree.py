#!/usr/bin/env python3
"""Draw a tree (Newick) coloured by lineage or region, as a PNG (needs biopython + matplotlib).
Usage: python3 scripts/14_plot_tree.py <tree.nwk|tree.treefile> [--color region|lineage] [--highlight S01] [--out tree.png]
"""
import argparse
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from Bio import Phylo

ROOT = Path(__file__).resolve().parent.parent
ap = argparse.ArgumentParser()
ap.add_argument("tree")
ap.add_argument("--color", choices=["region", "lineage"], default="region")
ap.add_argument("--lineages", default=str(ROOT / "results/phylo/lineages.tsv"))
ap.add_argument("--highlight", default="S01")
ap.add_argument("--out", default=str(ROOT / "results/phylo/tree.png"))
a = ap.parse_args()

meta = {}
for l in open(ROOT / "data/outbreak/metadata.tsv").read().splitlines()[1:]:
    i, d, r = l.split("\t")
    meta[i] = dict(region=r, date=d)
meta["S01"] = dict(region="Region A", date="2026-03-02")
meta["TOYV1_ref"] = dict(region="reference", date="")
lin = {}
if Path(a.lineages).exists():
    for l in open(a.lineages).read().splitlines()[1:]:
        s, lg, _ = l.split("\t")
        lin[s] = lg
for k in lin:
    meta.setdefault(k, {})["lineage"] = lin[k]

key = a.color
vals = sorted({meta.get(t, {}).get(key, "?") for t in meta})
palette = ["#2f7d4f", "#d1495b", "#00798c", "#edae49", "#7a5195", "#8d99ae", "#444444", "#e07a5f"]
col = {v: palette[i % len(palette)] for i, v in enumerate(vals)}

tree = Phylo.read(a.tree, "newick")
n = tree.count_terminals()
fig, ax = plt.subplots(figsize=(9, 0.28 * n + 1.5))
Phylo.draw(tree, axes=ax, do_show=False, label_func=lambda c: None, show_confidence=False)
# replace Bio.Phylo's default labels by coloured ones
for txt in list(ax.texts):
    txt.remove()
depths = tree.depths()
if not max(depths.values()):
    depths = tree.depths(unit_branch_lengths=True)
tips = tree.get_terminals()
for i, t in enumerate(tips, 1):
    name = t.name
    c = col.get(meta.get(name, {}).get(key, "?"), "#000")
    w = "bold" if name == a.highlight else "normal"
    ax.text(depths[t] * 1.01, i, f" {name}", va="center", color=c, fontsize=8, fontweight=w)
handles = [plt.Line2D([0], [0], marker="o", color="w", markerfacecolor=col[v], label=v) for v in vals]
ax.legend(handles=handles, title=key, loc="lower right", fontsize=8)
ax.set_xlabel("substitutions per site")
ax.set_ylabel("")
ax.set_yticks([])
fig.tight_layout()
Path(a.out).parent.mkdir(parents=True, exist_ok=True)
fig.savefig(a.out, dpi=150)
print("saved", a.out)
