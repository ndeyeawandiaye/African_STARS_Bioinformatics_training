#!/usr/bin/env python3
"""Generate the SYNTHETIC teaching dataset used in the dry lab.

Everything is deterministic (fixed seed): re-running this script reproduces
the same files byte for byte. Standard library only.

What it creates
---------------
data/reference/TOYV1.fasta     10 kb synthetic "virus" reference
data/fastq/<sample>_R{1,2}.fastq.gz   Illumina-style paired-end reads
data/samples.tsv               sample sheet + (synthetic) metadata
solutions/truth_variants.tsv   the SNPs really present in each sample
solutions/contaminant.fasta    the off-target genome used for S04 / S05

Samples (each one teaches a different QC lesson)
------------------------------------------------
S01  clean run                  -> complete, high-quality genome
S02  amplicon-style dropout     -> good mean depth but a hole in the genome
S03  very low depth (~5x)       -> mostly N, not usable
S04  25 % off-target reads      -> genome OK, but low % mapped (contamination)
S05  negative control (NTC)     -> should be empty; a few reads leaked in
"""
import argparse
import gzip
import json
import random
from pathlib import Path

SEED = 20261012
REF_LEN = 10_000
CONT_LEN = 6_000
READ_LEN = 150
DROPOUT = (3500, 5000)  # 0-based, half-open: the "hole" in S02
ADAPTER_R1 = "AGATCGGAAGAGCACACGTCTGAACTCCAGTCA"
ADAPTER_R2 = "AGATCGGAAGAGCGTCGTGTAGGGAAAGAGTGT"
COMP = str.maketrans("ACGTN", "TGCAN")

SAMPLES = [
    dict(id="S01", viral_pairs=3333, off_pairs=0, bleed_pairs=0, dropout=False, private_snps=2,
         date="2026-03-02", region="Region A", kind="sample", index="ATCACG+CGATGT"),
    dict(id="S02", viral_pairs=3333, off_pairs=0, bleed_pairs=0, dropout=True, private_snps=4,
         date="2026-03-05", region="Region A", kind="sample", index="TTAGGC+TGACCA"),
    dict(id="S03", viral_pairs=170, off_pairs=0, bleed_pairs=0, dropout=False, private_snps=3,
         date="2026-03-09", region="Region B", kind="sample", index="ACAGTG+GCCAAT"),
    dict(id="S04", viral_pairs=2500, off_pairs=833, bleed_pairs=0, dropout=False, private_snps=5,
         date="2026-03-11", region="Region C", kind="sample", index="CAGATC+ACTTGA"),
    dict(id="S05", viral_pairs=0, off_pairs=200, bleed_pairs=25, dropout=False, private_snps=0,
         date="2026-03-11", region="", kind="NTC", index="GATCAG+TAGCTT"),
]


def revcomp(s):
    return s.translate(COMP)[::-1]


def rand_seq(rng, n, weights=(0.28, 0.22, 0.22, 0.28)):
    return "".join(rng.choices("ACGT", weights=weights, k=n))


def mutate(genome, positions, rng):
    g = list(genome)
    out = []
    for p in sorted(positions):
        alt = rng.choice([b for b in "ACGT" if b != g[p]])
        out.append((p, g[p], alt))
        g[p] = alt
    return "".join(g), out


def qualities(n, rng, mate):
    base = 37.0 if mate == 1 else 36.0
    slope = 0.045 if mate == 1 else 0.05
    q = []
    for i in range(n):
        m = base - slope * i
        if mate == 2 and i > 110:
            m -= 0.12 * (i - 110)
        v = int(round(rng.gauss(m, 2.2)))
        if rng.random() < 0.003:
            v = rng.randint(2, 12)
        q.append(min(40, max(2, v)))
    return q


def add_errors(seq, quals, rng):
    s = list(seq)
    for i, q in enumerate(quals):
        if rng.random() < 10 ** (-q / 10):
            s[i] = rng.choice([b for b in "ACGT" if b != s[i]])
    return "".join(s)


def make_pairs(genome, n_pairs, rng, exclude=None, leak=0.02):
    """Simulate n_pairs read pairs. Fragments overlapping `exclude` are mostly rejected."""
    L = len(genome)
    pairs = []
    while len(pairs) < n_pairs:
        flen = max(90, min(500, int(rng.gauss(250, 50))))
        if flen > L:
            continue
        start = rng.randrange(0, L - flen + 1)
        end = start + flen
        if exclude and start < exclude[1] and end > exclude[0] and rng.random() > leak:
            continue
        frag = genome[start:end]
        if rng.random() < 0.5:
            frag = revcomp(frag)
        r1 = frag[:READ_LEN]
        r2 = revcomp(frag)[:READ_LEN]
        if len(r1) < READ_LEN:  # short fragment: read-through into the adapter
            r1 = (r1 + ADAPTER_R1 + rand_seq(rng, READ_LEN))[:READ_LEN]
        if len(r2) < READ_LEN:
            r2 = (r2 + ADAPTER_R2 + rand_seq(rng, READ_LEN))[:READ_LEN]
        q1, q2 = qualities(READ_LEN, rng, 1), qualities(READ_LEN, rng, 2)
        pairs.append((add_errors(r1, q1, rng), q1, add_errors(r2, q2, rng), q2))
    return pairs


def write_fastq(path, sample_id, index, pairs, rng):
    order = list(range(len(pairs)))
    rng.shuffle(order)
    with open(path[0], "wb") as f1, open(path[1], "wb") as f2:
        g1 = gzip.GzipFile(filename="", mode="wb", fileobj=f1, mtime=0)
        g2 = gzip.GzipFile(filename="", mode="wb", fileobj=f2, mtime=0)
        for n, i in enumerate(order):
            s1, q1, s2, q2 = pairs[i]
            tile, x, y = rng.randint(1101, 1128), rng.randint(1000, 30000), rng.randint(1000, 30000)
            name = f"SIM01:7:HFSIM{sample_id[1:]}:1:{tile}:{x}:{y}"
            for g, mate, s, q in ((g1, 1, s1, q1), (g2, 2, s2, q2)):
                g.write(f"@{name} {mate}:N:0:{index}\n{s}\n+\n{''.join(chr(v + 33) for v in q)}\n".encode())
        g1.close()
        g2.close()


def wrap_fasta(name, seq, width=70):
    return f">{name}\n" + "\n".join(seq[i:i + width] for i in range(0, len(seq), width)) + "\n"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=str(Path(__file__).resolve().parent.parent), help="repository root")
    root = Path(ap.parse_args().out)
    for d in ("data/reference", "data/fastq", "solutions"):
        (root / d).mkdir(parents=True, exist_ok=True)

    rng = random.Random(SEED)
    ref = rand_seq(rng, REF_LEN)
    contaminant = rand_seq(random.Random(SEED + 1), CONT_LEN, weights=(0.2, 0.3, 0.3, 0.2))
    (root / "data/reference/TOYV1.fasta").write_text(
        wrap_fasta("TOYV1 synthetic reference genome (10,000 bp)", ref))
    (root / "solutions/contaminant.fasta").write_text(
        wrap_fasta("OFFTARGET synthetic contaminant (6,000 bp)", contaminant))

    # shared "clade" mutations + private mutations per sample, never inside the S02 hole
    allowed = [p for p in range(200, REF_LEN - 200) if not (DROPOUT[0] - 100 <= p < DROPOUT[1] + 100)]
    clade_pos = rng.sample(allowed, 8)
    truth, genomes = [], {}
    for s in SAMPLES:
        if s["kind"] != "sample":
            continue
        priv = rng.sample([p for p in allowed if p not in clade_pos], s["private_snps"])
        g, muts = mutate(ref, clade_pos + priv, rng)
        genomes[s["id"]] = g
        truth += [(s["id"], p + 1, r, a, "shared" if p in clade_pos else "private") for p, r, a in muts]

    with open(root / "solutions/truth_variants.tsv", "w") as f:
        f.write("sample\tposition_1based\tref\talt\ttype\n")
        for row in truth:
            f.write("\t".join(map(str, row)) + "\n")

    with open(root / "data/samples.tsv", "w") as meta:
        meta.write("sample_id\tsample_type\tcollection_date\tregion\tR1\tR2\n")
        for s in SAMPLES:
            r = random.Random(f"{SEED}-{s['id']}")
            pairs = []
            if s["viral_pairs"]:
                pairs += make_pairs(genomes[s["id"]], s["viral_pairs"], r, DROPOUT if s["dropout"] else None)
            if s["off_pairs"]:
                pairs += make_pairs(contaminant, s["off_pairs"], r)
            if s["bleed_pairs"]:
                pairs += make_pairs(genomes["S01"], s["bleed_pairs"], r)
            r1 = root / "data/fastq" / f"{s['id']}_R1.fastq.gz"
            r2 = root / "data/fastq" / f"{s['id']}_R2.fastq.gz"
            write_fastq((r1, r2), s["id"], s["index"], pairs, r)
            meta.write(f"{s['id']}\t{s['kind']}\t{s['date']}\t{s['region']}\t"
                       f"data/fastq/{r1.name}\tdata/fastq/{r2.name}\n")
            print(f"{s['id']}: {len(pairs)} read pairs")

    (root / "solutions/design.json").write_text(json.dumps(
        {"seed": SEED, "ref_len": REF_LEN, "read_len": READ_LEN, "s02_dropout_1based": [DROPOUT[0] + 1, DROPOUT[1]],
         "clade_positions_1based": sorted(p + 1 for p in clade_pos),
         "samples": {s["id"]: {k: v for k, v in s.items() if k.endswith("pairs")} for s in SAMPLES}}, indent=2) + "\n")


if __name__ == "__main__":
    main()
