---
title: "Coverage and consensus"
subtitle: "45 min"
---

**Goal:** measure how well the genome is covered, find the holes, build the consensus genome and list the variants.
We start with **S01**, then repeat on the other samples.

::: {.callout-note}
If a tool does not work for you, use the ready-made files: replace `results/bam/` by `precomputed/bam/`,
`results/coverage/` by `precomputed/coverage/` (see *Plan B* in the Setup page).
:::

## Step 1 — Depth at every position

*Depth* = number of reads covering a position. `-a` asks for **all** positions, including the ones with zero reads.

```bash
mkdir -p results/coverage results/consensus results/variants
```
```bash
samtools depth -a results/bam/S01.bam > results/coverage/S01.depth.tsv
```
```bash
head -3 results/coverage/S01.depth.tsv
```

The three columns are: reference name, position, depth. A quick summary per reference:

```bash
samtools coverage results/bam/S01.bam
```

(`meandepth` = mean depth, `coverage` = % of positions with at least 1 read.)

## Step 2 — Mean depth and breadth at ≥ 10x

*Breadth* = the part of the genome with enough depth to call a base (here ≥ 10x, the threshold of this course).

```bash
awk '{t+=$3; if($3>=10) n++} END{printf "mean depth %.1f   genome at >=10x: %.1f%%\n", t/NR, 100*n/NR}' results/coverage/S01.depth.tsv
```

## Step 3 — Find the low-depth regions

This command merges consecutive positions with depth < 10 into intervals (BED format: reference, start, end):

```bash
awk 'BEGIN{OFS="\t"} $3<10{ if(!on){start=$2; on=1} end=$2; next } on{print $1,start-1,end; on=0} END{if(on) print $1,start-1,end}' results/coverage/S01.depth.tsv
```

## Step 4 — Repeat for the other samples

```bash
for s in S02 S03 S04 S05; do
  samtools depth -a results/bam/$s.bam > results/coverage/$s.depth.tsv
  echo -n "$s  "
  awk '{t+=$3; if($3>=10) n++} END{printf "mean depth %.1f   >=10x: %.1f%%\n", t/NR, 100*n/NR}' results/coverage/$s.depth.tsv
done
```

Then the low-depth regions of S02:

```bash
awk 'BEGIN{OFS="\t"} $3<10{ if(!on){start=$2; on=1} end=$2; next } on{print $1,start-1,end; on=0} END{if(on) print $1,start-1,end}' results/coverage/S02.depth.tsv
```

**Questions**

1. For each sample: mean depth, % of the genome at ≥ 10x, positions of the low-depth regions.
2. In IGV, look at S02 (`TOYV1:3000-5500`). Where is the gap and how long is it? Which laboratory step could explain it?

::: {.callout-tip collapse="true"}
## Answers
| Sample | Mean depth | Genome ≥ 10x | Low-depth regions |
|---|---|---|---|
| S01 | 99.8 | 99.4 % | only the two ends (first ~30 and last ~30 bases) |
| S02 | 99.7 | **84.3 %** | ends **and one large hole around 3,500–5,000** |
| S03 | 5.1 | **5.0 %** | almost the whole genome |
| S04 | 74.7 | 99.4 % | only the two ends |
| S05 (NTC) | 0.8 | 0.0 % | the whole genome |

S02: the hole spans about **1,500 bases (positions ≈ 3,500 to 5,000)**, where the depth falls to nearly 0, while it is ~100x
elsewhere. This is **amplicon dropout**: in an amplicon protocol the genome is amplified in overlapping pieces; if a
mutation falls in a primer site, or if some amplicons fail (degraded RNA, low input, pool imbalance), the pieces are
missing from the library and no reads come from that region. The ends of every genome are always poorly covered (reads
start/stop there).
:::

## Step 5 — Build the consensus genome with iVar

`samtools mpileup` lists the bases of all reads at each position; `ivar consensus` keeps the majority base and writes `N` when
there is not enough information. The options: `-m 10` minimum depth, `-q 20` minimum base quality, `-t 0.5` a base must be seen in at least
50 % of the reads, `-n N` write N for the missing positions.

```bash
samtools mpileup -aa -A -d 0 -Q 0 results/bam/S01.bam | ivar consensus -p results/consensus/S01.raw -q 20 -t 0.5 -m 10 -n N
```
```bash
sed '1s/.*/>S01/' results/consensus/S01.raw.fa > results/consensus/S01.fa
```
```bash
head -c 300 results/consensus/S01.fa
```

For the other samples:

```bash
for s in S02 S03 S04 S05; do
  samtools mpileup -aa -A -d 0 -Q 0 results/bam/$s.bam | ivar consensus -p results/consensus/$s.raw -q 20 -t 0.5 -m 10 -n N
  sed "1s/.*/>$s/" results/consensus/$s.raw.fa > results/consensus/$s.fa
done
```

## Step 6 — Count the N

Number of `N` in a consensus, and the length of the longest run of N:

```bash
grep -v '>' results/consensus/S01.fa | tr -cd 'N' | wc -c
```
```bash
grep -v '>' results/consensus/S01.fa | tr -d '\n' | grep -o 'N\+' | awk '{print length}' | sort -n | tail -1
```

For all samples:

```bash
for s in S01 S02 S03 S04 S05; do
  n=$(grep -v '>' results/consensus/$s.fa | tr -cd 'N' | wc -c)
  run=$(grep -v '>' results/consensus/$s.fa | tr -d '\n' | grep -o 'N\+' | awk '{print length}' | sort -n | tail -1)
  echo "$s  N=$n  longest run=${run:-0}"
done
```

::: {.callout-tip collapse="true"}
## Expected values
| Sample | N bases | % N | Longest N run |
|---|---|---|---|
| S01 | 63 | 0.6 % | 33 |
| S02 | 1,566 | 15.7 % | **1,526** |
| S03 | 9,507 | 95.1 % | 2,248 |
| S04 | 58 | 0.6 % | 30 |
| S05 | 10,000 | 100 % | 10,000 |
:::

## Step 7 — List the variants (VCF)

```bash
bcftools mpileup -f data/reference/TOYV1.fasta -Q 20 -d 1000000 -a AD results/bam/S01.bam \
  | bcftools call -mv --ploidy 1 -Oz -o results/variants/S01.vcf.gz
```
```bash
bcftools index results/variants/S01.vcf.gz
```
```bash
bcftools view -H results/variants/S01.vcf.gz | cut -f1,2,4,5,6
```

Each line is a variant: position, reference base, alternative base, quality. How many variants does S01 have, and do they
match what you saw in IGV (position 553)?

::: {.callout-tip collapse="true"}
## Answer
S01 carries **10 variants** relative to the reference (8 shared with the outbreak lineage, such as 553 T>G, 3299 C>A,
5753 C>A, and 2 private ones, 269 A>C and 7782 G>C). Position 553 is in the list, as seen in IGV. Sequencing errors
(like position 1372) do **not** appear: they are too rare and have low quality.
:::

## Step 8 — Change the depth threshold

Rebuild the S01 consensus requiring 30 reads instead of 10, and compare the N:

```bash
samtools mpileup -aa -A -d 0 -Q 0 results/bam/S01.bam | ivar consensus -p results/consensus/S01.m30 -q 20 -t 0.5 -m 30 -n N
grep -v '>' results/consensus/S01.m30.fa | tr -cd 'N' | wc -c
```

::: {.callout-tip collapse="true"}
## Answer
There are **more N** (about 180 instead of 63: the genome ≥ 30x is 98.2 % instead of 99.4 %). A higher threshold
makes each base call **more reliable** but the genome **less complete**. There is no universal value: it is a compromise that
each laboratory chooses and documents (10x is common for surveillance; 20–30x for sensitive analyses).
:::

## Final question

S02 has a mean depth of about 100x. Why is its consensus still incomplete?

::: {.callout-tip collapse="true"}
## Answer
A **mean** hides the distribution: S02 has ~118x on 84 % of the genome and ~0x on the other 16 %, which gives a mean near 100x.
Bases without reads cannot be called, so they become N. Mean depth is not enough: always look at the **breadth** (% ≥ 10x)
and the **longest run of N**.
:::

**Next:** [Is this genome good enough?](04_genome_qc_verdict.md)
