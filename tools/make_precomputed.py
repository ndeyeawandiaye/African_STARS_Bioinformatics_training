#!/usr/bin/env python3
"""Rebuild precomputed/ (the "plan B" files) with a pure-Python stand-in for the pipeline.

Needs:  pip install mappy pysam      (mappy = minimap2 as a Python library)

It uses the same aligner family (minimap2, 'sr' preset) and the same samtools code (through pysam) as the
real pipeline, and writes the same folder layout as results/:
    precomputed/bam/<s>.bam(.bai), <s>.flagstat.txt
    precomputed/coverage/<s>.depth.tsv
    precomputed/consensus/<s>.fa
    precomputed/qc_summary.tsv   (written afterwards by scripts/07_summary.py)

Differences from the shell pipeline (kept on purpose, to stay dependency-light): reads are not trimmed first
(minimap2 soft-clips adapters anyway) and the consensus is a simple majority-rule caller. For authentic
outputs, run scripts/run_all.sh on a machine with the conda environment and copy results/ here
(tools/refresh_precomputed.sh does exactly that).
"""
import argparse
import array
import gzip
import subprocess
import sys
from pathlib import Path

import mappy
import pysam

ROOT = Path(__file__).resolve().parent.parent
MIN_DEPTH, MIN_BASEQ, MIN_FREQ = 10, 20, 0.5
COMP = str.maketrans("ACGTN", "TGCAN")


def revcomp(s):
    return s.translate(COMP)[::-1]


def read_fastq(path):
    with gzip.open(path, "rt") as f:
        while True:
            name = f.readline().strip()
            if not name:
                return
            seq = f.readline().strip()
            f.readline()
            qual = [ord(c) - 33 for c in f.readline().strip()]
            yield name[1:].split()[0], seq, qual


def make_record(header, name, seq, qual, hit, mate, rg):
    a = pysam.AlignedSegment(header)
    a.query_name = name
    a.set_tag("RG", rg)
    flag = 0x1 | (0x40 if mate == 1 else 0x80)
    if hit is None:
        a.flag = flag | 0x4
        a.query_sequence = seq
        a.query_qualities = array.array("B", qual)
        return a
    rev = hit.strand == -1
    s = revcomp(seq) if rev else seq
    q = qual[::-1] if rev else qual
    left = (len(seq) - hit.q_en) if rev else hit.q_st
    right = hit.q_st if rev else (len(seq) - hit.q_en)
    cig = ([(4, left)] if left else []) + [(op, ln) for ln, op in hit.cigar] + ([(4, right)] if right else [])
    a.flag = flag | (0x10 if rev else 0)
    a.query_sequence = s
    a.reference_id = 0
    a.reference_start = hit.r_st
    a.mapping_quality = hit.mapq
    a.cigartuples = cig
    a.query_qualities = array.array("B", q)
    return a


def pair_up(a1, a2):
    m1, m2 = not a1.is_unmapped, not a2.is_unmapped
    for a, b, mb in ((a1, a2, m2), (a2, a1, m1)):
        if not mb:
            a.flag |= 0x8
        elif a.is_unmapped:
            a.reference_id, a.reference_start = b.reference_id, b.reference_start
        if mb:
            a.next_reference_id, a.next_reference_start = b.reference_id, b.reference_start
            if b.is_reverse:
                a.flag |= 0x20
    if m1 and m2:
        lo = min(a1.reference_start, a2.reference_start)
        hi = max(a1.reference_end, a2.reference_end)
        if a1.is_reverse != a2.is_reverse:
            a1.flag |= 0x2
            a2.flag |= 0x2
        left_first = a1.reference_start <= a2.reference_start
        a1.template_length = (hi - lo) if left_first else -(hi - lo)
        a2.template_length = -a1.template_length


def build_bam(sample, r1, r2, aligner, ref_name, ref_len, out_dir):
    header = pysam.AlignmentHeader.from_dict({
        "HD": {"VN": "1.6", "SO": "unsorted"}, "SQ": [{"SN": ref_name, "LN": ref_len}],
        "RG": [{"ID": sample, "SM": sample}],
        "PG": [{"ID": "minimap2", "PN": "mappy", "VN": mappy.__version__ if hasattr(mappy, "__version__") else "2"}]})
    tmp, final = out_dir / f"{sample}.unsorted.bam", out_dir / f"{sample}.bam"
    with pysam.AlignmentFile(tmp, "wb", header=header) as out:
        for (n1, s1, q1), (n2, s2, q2) in zip(read_fastq(r1), read_fastq(r2)):
            recs = []
            for mate, name, seq, qual in ((1, n1, s1, q1), (2, n2, s2, q2)):
                hit = next((h for h in aligner.map(seq) if h.is_primary), None)
                recs.append(make_record(header, name, seq, qual, hit, mate, sample))
            pair_up(*recs)
            for r in recs:
                out.write(r)
    pysam.sort("-o", str(final), str(tmp))
    pysam.index(str(final))
    tmp.unlink()
    (out_dir / f"{sample}.flagstat.txt").write_text(pysam.samtools.flagstat(str(final)))
    return final


def consensus(bam_path, ref_name, ref_len):
    seq = ["N"] * ref_len
    with pysam.AlignmentFile(str(bam_path), "rb") as bam:
        for col in bam.pileup(ref_name, 0, ref_len, truncate=True, stepper="nofilter", min_base_quality=0,
                              max_depth=1_000_000, ignore_overlaps=False):
            counts = {}
            for pr in col.pileups:
                if pr.is_del or pr.is_refskip or pr.query_position is None:
                    continue
                if pr.alignment.query_qualities[pr.query_position] >= MIN_BASEQ:
                    b = pr.alignment.query_sequence[pr.query_position]
                    counts[b] = counts.get(b, 0) + 1
            depth = sum(counts.values())
            if depth >= MIN_DEPTH:
                base, c = max(counts.items(), key=lambda kv: kv[1])
                if c / depth >= MIN_FREQ:
                    seq[col.reference_pos] = base
    return "".join(seq)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=str(ROOT / "precomputed"))
    ap.add_argument("samples", nargs="*")
    a = ap.parse_args()
    out = Path(a.out)
    for d in ("bam", "coverage", "consensus"):
        (out / d).mkdir(parents=True, exist_ok=True)

    ref_path = ROOT / "data/reference/TOYV1.fasta"
    aligner = mappy.Aligner(str(ref_path), preset="sr")
    ref_name, ref_len = aligner.seq_names[0], len(aligner.seq(aligner.seq_names[0]))
    rows = [l.rstrip("\n").split("\t") for l in open(ROOT / "data/samples.tsv")][1:]
    for sid, _type, _date, _reg, r1, r2 in rows:
        if a.samples and sid not in a.samples:
            continue
        print(f"[precomputed] {sid}")
        bam = build_bam(sid, ROOT / r1, ROOT / r2, aligner, ref_name, ref_len, out / "bam")
        (out / "coverage" / f"{sid}.depth.tsv").write_text(pysam.samtools.depth("-a", str(bam)))
        cons = consensus(bam, ref_name, ref_len)
        (out / "consensus" / f"{sid}.fa").write_text(
            f">{sid}\n" + "\n".join(cons[i:i + 70] for i in range(0, len(cons), 70)) + "\n")
    subprocess.run([sys.executable, str(ROOT / "scripts/07_summary.py"), "--results", str(out), *a.samples], check=True)


if __name__ == "__main__":
    main()
