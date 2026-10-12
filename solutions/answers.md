# Instructor answers — publish AFTER the session

> Numbers below come from the Python stand-in (`precomputed/`). A real run (minimap2, samtools, iVar) should give very
> close values; check with `tools/refresh_precomputed.sh` and adjust if needed.

## Sample design

| Sample | Design | Expected lesson |
|---|---|---|
| S01 | Clean, ~100x | Reference case: PASS |
| S02 | Amplicon dropout, positions 3501–5000 | High mean depth does not mean a complete genome |
| S03 | Very low depth (~5x) | Almost everything masked with N |
| S04 | 25% off-target (contaminant) reads | Low % mapped, but the genome itself is fine: REVIEW |
| S05 | Negative control, with 25 pairs bleeding from S01 | Reads in the NTC must be reported |

Truth: `solutions/truth_variants.tsv` (8 shared clade SNPs + a few private SNPs per sample).

## Expected QC summary

| Sample | Reads | % mapped | Mean depth | % ≥ 10x | % N | Verdict |
|---|---|---|---|---|---|---|
| S01 | 6666 | 100 | 99.8 | 99.4 | 0.6 | PASS |
| S02 | 6666 | 100 | 99.7 | 84.3 | 15.7 (run of 1526 N) | FAIL |
| S03 | 340 | 100 | 5.1 | 5.0 | 95.1 | FAIL |
| S04 | 6666 | 75.0 | 74.7 | 99.4 | 0.6 | REVIEW |
| S05 (NTC) | 450 | 11.1 | 0.8 | 0.0 | 100 | CONTROL-CHECK |

## Answers by exercise

**01** Phred = ASCII − 33. Q20 → error probability 10^(−20/10) = 1%. R2 quality drops faster than R1 toward the
3′ end (about 91% vs 73% of bases ≥ Q30). Short fragments carry adapter read-through; trimming removes it and
improves the R2 tail. S03 and S05 have far fewer reads.

**02** S04 has ~25% unmapped reads (off-target/contaminant). S03 has few reads overall. The NTC should have ~no
mapped reads: here 50 reads map — barcode bleed from S01 (reads carrying S01 variants) — so it must be reported.
Sequencing errors appear in a few reads at random; real variants appear in nearly all reads at the position.
Sorting and indexing allow fast random access (IGV, samtools depth).

**03** S02 has a ~1500 bp gap (3501–5000): amplicon dropout (primer-site mutation or failed amplicons). Its mean
depth (~100x) hides it, so always check breadth and the depth profile. Raising MIN_DEPTH to 30 masks more positions in
S01 (more N, higher confidence per base): the threshold trades completeness against accuracy.

**04** S01: use. S02: do not use as is — re-run the failed amplicons or redesign primers. S03: discard/re-sequence
(low input or failed library). S04: usable after review — the viral genome is complete, but investigate the
contamination source. S05: report the 50 reads, check index design/barcode bleed, and consider the S01 run
for cross-contamination.

## Teaching points
- Mean depth ≠ complete genome: report breadth and the longest N run.
- Always read the negative control.
- A low % mapped is a wet-lab clue, not necessarily a bad genome.
- Thresholds are a decision to document, not a universal constant.
