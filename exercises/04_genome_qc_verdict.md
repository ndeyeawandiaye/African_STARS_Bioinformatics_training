---
title: "Is this genome good enough?"
subtitle: "30 min"
---

**Goal:** for each sample, gather the quality numbers in one table, then take a **decision**: is the genome usable for
phylogenetics (Day 4), does it need review or re-sequencing, or must it be discarded?
A genome is never "good" or "bad" in itself: it is good **enough for a purpose**, judged on a handful of numbers.

## The numbers that matter

| Metric | Why it matters |
|---|---|
| **Total reads / % mapped** | how much data, and how much of it is the virus (low % = contamination, poor enrichment) |
| **Mean depth** | average confidence of the base calls |
| **% of genome ≥ 10x** (breadth) | how much of the genome can really be called |
| **% N** and **longest run of N** | missing information; a long run = a whole region (gene) is missing |
| **Negative control** | are there viral reads where there should be none? |

## Step 1 — Build the summary table

This one command collects, for every sample, the numbers you computed in the previous exercises:

```bash
printf "sample\ttotal_reads\tpct_mapped\tmean_depth\tpct_ge10x\tN_bases\tlongest_N_run\n" > results/qc_summary.tsv
for s in S01 S02 S03 S04 S05; do
  total=$(samtools view -c -F 2304 results/bam/$s.bam)
  mapped=$(samtools view -c -F 2308 results/bam/$s.bam)
  pm=$(awk -v m=$mapped -v t=$total 'BEGIN{printf "%.1f", 100*m/t}')
  dp=$(awk '{t+=$3; if($3>=10) n++} END{printf "%.1f\t%.1f", t/NR, 100*n/NR}' results/coverage/$s.depth.tsv)
  nb=$(grep -v '>' results/consensus/$s.fa | tr -cd 'N' | wc -c)
  run=$(grep -v '>' results/consensus/$s.fa | tr -d '\n' | grep -o 'N\+' | awk '{print length}' | sort -n | tail -1)
  printf "%s\t%s\t%s\t%s\t%s\t%s\n" "$s" "$total" "$pm" "$dp" "$nb" "${run:-0}" >> results/qc_summary.tsv
done
column -t -s $'\t' results/qc_summary.tsv
```

(`samtools view -c -F 2304` counts the primary reads; `-F 2308` the primary reads that are mapped.)

*Cross-check:* compare your table with `precomputed/qc_summary.tsv` (same numbers, plus a PASS / REVIEW / FAIL column).

## Step 2 — Take a decision for each sample

Use these **example thresholds** (many laboratories use similar ones; adapt them to your protocol):

| Criterion | Good | To review | Bad |
|---|---|---|---|
| % mapped | ≥ 90 % | 70–90 % | < 70 % |
| Genome ≥ 10x | ≥ 90 % | 70–90 % | < 70 % |
| % N | ≤ 10 % | 10–20 % | > 20 % |
| Negative control | ≤ 10 viral reads | – | more |

Fill in `exercises/answer_sheet.tsv`: for each sample, the numbers, a verdict (**use / review–re-sequence / discard**) and a
one-line justification. Then compare with your neighbour.

::: {.callout-tip collapse="true"}
## Expected table and verdicts
| Sample | Reads | % mapped | Mean depth | % ≥ 10x | % N | Longest N | Verdict | Why |
|---|---|---|---|---|---|---|---|---|
| S01 | 6,666 | 100 | 99.8 | 99.4 | 0.6 | 33 | **Use** | complete, deep, clean |
| S02 | 6,666 | 100 | 99.7 | 84.3 | 15.7 | 1,526 | **Review / re-sequence** | good depth, but a 1.5 kb gap (amplicon dropout) |
| S03 | 340 | 100 | 5.1 | 5.0 | 95.1 | 2,248 | **Discard / re-sequence** | far too little data, 95 % N |
| S04 | 6,666 | **75.0** | 74.7 | 99.4 | 0.6 | 30 | **Review** (then use) | genome complete, but 25 % off-target reads: find the contamination source |
| S05 (NTC) | 450 | 11.1 | 0.8 | 0.0 | 100 | 10,000 | **Control: to report** | 50 viral reads in a negative control |
:::

## Step 3 — Discussion questions

**1. Which sample would you re-sequence, and what would you change?**

::: {.callout-tip collapse="true"}
## Answer
- **S03**: re-sequence from a new library with more input material (re-extract, concentrate the RNA, more reads in the pool) —
  it has only 5x depth, repeating the same run will not help.
- **S02**: do not repeat everything: **re-amplify only the failed region** (around 3,500–5,000). Check whether a known mutation
  falls in a primer site; if so, add or redesign primers, or use a different primer scheme for this lineage.
- **S04**: the genome is complete; the question is the laboratory source of the off-target reads (host DNA, contaminated
  reagents). Consider host depletion or a cleaner extraction, and identify the reads with Kraken2.
:::

**2. What do you report about the negative control?**

::: {.callout-tip collapse="true"}
## Answer
Always report it, even if it looks "clean". Say: the number of reads in the NTC (450), how many map to the virus (50, i.e. 25 pairs),
their likely origin (barcode bleed from S01, whose variants they carry), and the **consequence for the run**: samples with a
signal close to that level (S03) cannot be interpreted; high-depth samples (S01, S02, S04) are not affected. If the contamination were
larger than a few reads, the whole run should be repeated.
:::

**3. Which thresholds would you set for your own laboratory?**

::: {.callout-tip collapse="true"}
## Answer
There is no universal answer; the thresholds depend on **what the genome is used for**:

- *Lineage assignment*: tolerates more N (as long as the lineage-defining positions are covered), e.g. ≥ 80–90 % of the genome.
- *Phylogenetics and transmission*: stricter, e.g. ≥ 90–95 % of the genome at ≥ 10–20x, no long run of N.
- *Negative controls*: a maximum number of viral reads (e.g. ≤ 10), or a ratio to the samples.

Write them down, test them on known samples (positive controls, replicates), apply them the same way to every run, and
review them when the protocol changes.
:::

**Next:** [Reference selection](../course/02-reference-selection.qmd) — module 2.
