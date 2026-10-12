#!/usr/bin/env python3
"""Step 7 - Genome QC summary: the numbers needed to decide "is this genome good enough?".

Reads, for each sample, the files written by the previous steps:
    <results>/bam/<sample>.flagstat.txt        (step 3)
    <results>/coverage/<sample>.depth.tsv      (step 4)
    <results>/consensus/<sample>.fa            (step 5)
and writes <results>/qc_summary.tsv. Standard library only.

Examples
    python3 scripts/07_summary.py                       # all samples of data/samples.tsv, from results/
    python3 scripts/07_summary.py S01 S02               # only these samples
    python3 scripts/07_summary.py --results precomputed # use the pre-computed files (plan B)
    python3 scripts/07_summary.py --min-depth 20 --min-breadth 95

The thresholds are defaults, NOT universal rules: adapt them to your protocol and to the use of the genome.
"""
import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def read_fasta(path):
    return "".join(l.strip() for l in open(path) if not l.startswith(">")).upper()


def parse_flagstat(path):
    total = mapped = pct = None
    for line in open(path):
        m = re.match(r"(\d+) \+ \d+ in total", line)
        if m and total is None:
            total = int(m.group(1))
        m = re.match(r"(\d+) \+ \d+ mapped \(([\d.]+|N/A)%", line)
        if m and mapped is None:
            mapped = int(m.group(1))
            pct = None if m.group(2) == "N/A" else float(m.group(2))
    if pct is None and total:
        pct = 100.0 * mapped / total
    return total or 0, mapped or 0, pct or 0.0


def parse_depth(path, min_depth):
    n = s = ok = 0
    for line in open(path):
        parts = line.split("\t")
        if len(parts) < 3:
            continue
        d = int(parts[2])
        n += 1
        s += d
        ok += d >= min_depth
    return (n, s / n if n else 0.0, 100.0 * ok / n if n else 0.0)


def sample_types(sheet):
    types = {}
    if sheet.exists():
        for i, line in enumerate(open(sheet)):
            f = line.rstrip("\n").split("\t")
            if i and len(f) > 1:
                types[f[0]] = f[1]
    return types


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("samples", nargs="*", help="sample IDs (default: all rows of the sample sheet)")
    ap.add_argument("--results", default=str(ROOT / "results"), help="results folder (default: results/)")
    ap.add_argument("--sample-sheet", default=str(ROOT / "data" / "samples.tsv"))
    ap.add_argument("--min-depth", type=int, default=10, help="depth threshold (default 10)")
    ap.add_argument("--min-breadth", type=float, default=90.0, help="min %% of genome at >= min-depth (default 90)")
    ap.add_argument("--min-mapped", type=float, default=90.0, help="min %% of reads mapped (default 90)")
    ap.add_argument("--max-ntc-reads", type=int, default=10, help="max mapped reads tolerated in a negative control")
    a = ap.parse_args()

    res = Path(a.results)
    types = sample_types(Path(a.sample_sheet))
    samples = a.samples or list(types)
    if not samples:
        sys.exit("No samples found: give sample IDs or check data/samples.tsv")

    cols = ["sample", "type", "total_reads", "mapped_reads", "pct_mapped", "mean_depth", f"pct_genome_ge{a.min_depth}x",
            "genome_length", "n_bases", "pct_N", "longest_N_run", "verdict", "flags"]
    rows = []
    for s in samples:
        need = [res / "bam" / f"{s}.flagstat.txt", res / "coverage" / f"{s}.depth.tsv", res / "consensus" / f"{s}.fa"]
        missing = [str(p) for p in need if not p.exists()]
        if missing:
            print(f"[skip] {s}: missing {', '.join(missing)}", file=sys.stderr)
            continue
        total, mapped, pct_mapped = parse_flagstat(need[0])
        glen, mean_depth, breadth = parse_depth(need[1], a.min_depth)
        seq = read_fasta(need[2])
        n = seq.count("N")
        longest = max((len(m.group()) for m in re.finditer("N+", seq)), default=0)
        flags = []
        if types.get(s, "sample") == "NTC":
            verdict = "CONTROL-CHECK" if mapped > a.max_ntc_reads else "CONTROL-OK"
            if mapped > a.max_ntc_reads:
                flags.append(f"negative control has {mapped} mapped reads (barcode bleed or contamination?)")
        else:
            if breadth < a.min_breadth:
                flags.append(f"only {breadth:.1f}% of the genome at >={a.min_depth}x")
            if pct_mapped < a.min_mapped:
                flags.append(f"only {pct_mapped:.1f}% of reads map (off-target reads / contamination?)")
            verdict = "FAIL" if breadth < a.min_breadth else ("REVIEW" if flags else "PASS")
        rows.append([s, types.get(s, "sample"), total, mapped, f"{pct_mapped:.1f}", f"{mean_depth:.1f}", f"{breadth:.1f}",
                     len(seq), n, f"{100.0 * n / len(seq) if seq else 0:.1f}", longest, verdict, "; ".join(flags)])

    if not rows:
        sys.exit("Nothing to summarise.")
    out = res / "qc_summary.tsv"
    with open(out, "w") as f:
        f.write("\t".join(cols) + "\n")
        for r in rows:
            f.write("\t".join(map(str, r)) + "\n")
    widths = [max(len(str(x)) for x in [c] + [r[i] for r in rows]) for i, c in enumerate(cols[:-1])]
    print("  ".join(c.ljust(w) for c, w in zip(cols[:-1], widths)))
    for r in rows:
        print("  ".join(str(x).ljust(w) for x, w in zip(r[:-1], widths)) + ("   <- " + r[-1] if r[-1] else ""))
    print(f"\nWritten: {out}")
    print(f"Thresholds used: depth >= {a.min_depth}x, genome breadth >= {a.min_breadth}%, mapped reads >= {a.min_mapped}%.")


if __name__ == "__main__":
    main()
