#!/usr/bin/env python3
"""Generate the SYNTHETIC outbreak dataset used on Days 4-5 (standard library only, deterministic).

Reads data/reference/TOYV1.fasta and solutions/truth_variants.tsv (so that sample S01 of the dry lab
fits into the outbreak) and writes:

data/outbreak/sequences.fasta        27 consensus genomes (OB01-OB27)
data/outbreak/metadata.tsv           collection date + region of each genome
data/outbreak/lineage_definitions.tsv  simplified lineage nomenclature (defining SNPs)
data/reference/candidates/*.fasta    3 candidate references for the "reference selection" exercise
solutions/outbreak_truth.tsv         true lineage of each genome (instructor only)
"""
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SEED = 20261013
rng = random.Random(SEED)
BASES = "ACGT"


def read_fasta(path):
    seq = "".join(l.strip() for l in open(path) if not l.startswith(">"))
    return seq.upper()


def wrap(s, n=70):
    return "\n".join(s[i:i + n] for i in range(0, len(s), n))


def mutate(seq, snps):
    s = list(seq)
    for pos, ref, alt in snps:          # pos is 1-based
        assert s[pos - 1] == ref, (pos, ref, s[pos - 1])
        s[pos - 1] = alt
    return "".join(s)


ref = read_fasta(ROOT / "data/reference/TOYV1.fasta")
L = len(ref)

# TV.2 defining SNPs = the clade SNPs of S01 (so S01 belongs to TV.2)
tv2 = []
for line in open(ROOT / "solutions/truth_variants.tsv").read().splitlines()[1:]:
    s, pos, r, a, t = line.split("\t")
    if s == "S01" and t == "shared":
        tv2.append((int(pos), r, a))
used = {p for p, _, _ in tv2}
s01_private = {int(l.split("\t")[1]) for l in open(ROOT / "solutions/truth_variants.tsv").read().splitlines()[1:]
               if l.startswith("S01")}
used |= s01_private


def new_snps(n):
    out = []
    while len(out) < n:
        p = rng.randrange(60, L - 60)
        if p in used:
            continue
        used.add(p)
        r = ref[p - 1]
        out.append((p, r, rng.choice([b for b in BASES if b != r])))
    return sorted(out)


tv21 = new_snps(3)
tv22 = new_snps(3)
tv3 = new_snps(6)

lineages = {
    "TV.1": ("root", []),
    "TV.2": ("TV.1", tv2),
    "TV.2.1": ("TV.2", tv21),
    "TV.2.2": ("TV.2", tv22),
    "TV.3": ("TV.1", tv3),
}
full = {
    "TV.1": [],
    "TV.2": tv2,
    "TV.2.1": tv2 + tv21,
    "TV.2.2": tv2 + tv22,
    "TV.3": tv3,
}

# (lineage, region, first date, last date, count)
plan = [
    ("TV.1", "Region B", "2026-01-12", "2026-02-10", 2),
    ("TV.1", "Region D", "2026-01-20", "2026-02-15", 1),
    ("TV.3", "Region B", "2026-02-10", "2026-03-20", 5),
    ("TV.2", "Region A", "2026-03-01", "2026-03-05", 3),
    ("TV.2", "Region C", "2026-03-12", "2026-03-12", 1),
    ("TV.2.1", "Region A", "2026-03-20", "2026-04-20", 7),
    ("TV.2.1", "Region C", "2026-04-02", "2026-04-02", 1),
    ("TV.2.2", "Region C", "2026-03-25", "2026-04-25", 6),
    ("TV.2.2", "Region C", "2026-04-28", "2026-04-28", 1),   # low-quality genome
]


def rand_date(a, b):
    from datetime import date, timedelta
    d0, d1 = date.fromisoformat(a), date.fromisoformat(b)
    return (d0 + timedelta(days=rng.randint(0, (d1 - d0).days))).isoformat()


records = []
for lin, region, a, b, n in plan:
    for _ in range(n):
        priv = new_snps(rng.choice([0, 1, 1, 2, 3]))
        seq = mutate(ref, full[lin] + priv)
        records.append(dict(lin=lin, region=region, date=rand_date(a, b), seq=seq, lowq=False))
records[-1]["lowq"] = True
# low quality genome: a 2,300 bp block of N + scattered N
s = list(records[-1]["seq"])
for i in range(4100, 6400):
    s[i] = "N"
for _ in range(40):
    s[rng.randrange(L)] = "N"
records[-1]["seq"] = "".join(s)

rng.shuffle(records)
out = ROOT / "data/outbreak"
out.mkdir(parents=True, exist_ok=True)
with open(out / "sequences.fasta", "w") as f, open(out / "metadata.tsv", "w") as m, \
        open(ROOT / "solutions/outbreak_truth.tsv", "w") as t:
    m.write("sample_id\tcollection_date\tregion\n")
    t.write("sample_id\ttrue_lineage\tnote\n")
    for i, r in enumerate(records, 1):
        sid = f"OB{i:02d}"
        f.write(f">{sid}\n{wrap(r['seq'])}\n")
        m.write(f"{sid}\t{r['date']}\t{r['region']}\n")
        t.write(f"{sid}\t{r['lin']}\t{'low-quality genome (exclude)' if r['lowq'] else ''}\n")

with open(out / "lineage_definitions.tsv", "w") as f:
    f.write("lineage\tparent\tdefining_snps\n")
    for lin, (parent, snps) in lineages.items():
        f.write(f"{lin}\t{parent}\t{','.join(f'{p}{r}>{a}' for p, r, a in snps) or '-'}\n")

# candidate references
cand = ROOT / "data/reference/candidates"
cand.mkdir(parents=True, exist_ok=True)
div = list(ref)
for p in rng.sample(range(L), 800):          # ~8 % divergent "other virus"
    div[p] = rng.choice([b for b in BASES if b != ref[p]])
cands = {
    "TOYV1_TV1": ref,
    "TOYV1_TV2": mutate(ref, tv2),
    "TOYV2_divergent": "".join(div),
}
for name, seq in cands.items():
    (cand / f"{name}.fasta").write_text(f">{name}\n{wrap(seq)}\n")
print("outbreak dataset written:", len(records), "genomes")
