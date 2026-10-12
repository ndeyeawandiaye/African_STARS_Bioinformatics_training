---
title: "Mapping"
subtitle: "30 min"
---

**Goal:** align the trimmed reads to the reference genome, and read the mapping statistics.

## Step 1 — Index the reference

The aligner and samtools need an index of the reference. You do it once.

```bash
bwa index data/reference/TOYV1.fasta
```
```bash
samtools faidx data/reference/TOYV1.fasta
```

## Step 2 — Map the reads of S01

`bwa mem` aligns the read pairs and writes SAM text to the screen; the pipe `|` sends it to `samtools sort`, which
orders the reads by position and saves a compact BAM file.

```bash
mkdir -p results/bam
```
```bash
bwa mem -t 2 -R "@RG\tID:S01\tSM:S01" data/reference/TOYV1.fasta \
    results/trimmed/S01_R1.fastq.gz results/trimmed/S01_R2.fastq.gz \
  | samtools sort -@ 2 -o results/bam/S01.bam -
```
```bash
samtools index results/bam/S01.bam
```
```bash
samtools flagstat results/bam/S01.bam | tee results/bam/S01.flagstat.txt
```

(`-R` adds a read-group label with the sample name; `tee` prints the result and also saves it.)

## Step 3 — Map the other four samples

Same commands, repeated by a loop:

```bash
for s in S02 S03 S04 S05; do
  bwa mem -t 2 -R "@RG\tID:${s}\tSM:${s}" data/reference/TOYV1.fasta \
      results/trimmed/${s}_R1.fastq.gz results/trimmed/${s}_R2.fastq.gz \
    | samtools sort -@ 2 -o results/bam/${s}.bam -
  samtools index results/bam/${s}.bam
  samtools flagstat results/bam/${s}.bam > results/bam/${s}.flagstat.txt
done
```

::: {.callout-note}
**Prefer minimap2?** It is faster and also works for long reads. For paired Illumina reads:
`minimap2 -ax sr -t 2 data/reference/TOYV1.fasta R1.fastq.gz R2.fastq.gz | samtools sort -o out.bam -`.
:::

## Step 4 — Read the flagstat files

```bash
cat results/bam/S01.flagstat.txt
```

The lines to read: **in total** (all reads), **mapped** (reads aligned to the reference, with %), **properly paired**
(both mates aligned in the expected orientation and distance). Fill in your
[answer sheet](https://github.com/YOUR-ORG/fastq-to-genome/blob/main/exercises/answer_sheet.tsv) (columns total reads, % mapped).

To see all samples at once:

```bash
for s in S01 S02 S03 S04 S05; do echo "== $s"; grep -E "in total|mapped \(|properly paired" results/bam/$s.flagstat.txt; done
```

::: {.callout-tip collapse="true"}
## Expected values
The numbers below are for the raw reads; after trimming you get very slightly fewer reads, but the **percentages are the same**.

| Sample | Total reads | % mapped | % properly paired |
|---|---|---|---|
| S01 | 6,666 | 100 % | 100 % |
| S02 | 6,666 | 100 % | 100 % |
| S03 | 340 | 100 % | 100 % |
| S04 | 6,666 | **75 %** | 75 % |
| S05 (NTC) | 450 | **11 %** | 11 % |
:::

## Questions

**1. Which sample has a low % mapped? What could the unmapped reads be?**

::: {.callout-tip collapse="true"}
## Answer
**S04**: only 75 % of its reads map (and S05, the negative control, 11 %). The 25 % of unmapped reads in S04 do not come
from the virus: they are **contamination or off-target material** (host DNA, bacteria, reagent contaminants, another sample).
To find out what they are, extract them and classify them:

```bash
samtools fastq -f 12 -n -1 results/S04_unmapped_R1.fq -2 results/S04_unmapped_R2.fq -0 /dev/null -s /dev/null results/bam/S04.bam
kraken2 --db <PATH_TO_DB> --paired results/S04_unmapped_R1.fq results/S04_unmapped_R2.fq --report results/S04.kraken.txt --output -
```

(`-f 12` = both mates unmapped. You can also paste a few reads in NCBI BLAST.) In this simulated dataset they come from a
non-viral genome. A low % mapped is a **laboratory clue** (poor enrichment, contamination), not necessarily a bad genome:
S04 still has about 75 reads per position (see next exercise).
:::

**2. Which samples have almost no reads? What does the NTC (S05) contain, and is that acceptable?**

::: {.callout-tip collapse="true"}
## Answer
**S03** has only 340 reads (about 5x depth on a 10 kb genome): too little material (low viral load, failed library or
under-represented in the pool). **S05** is the negative control and should contain no viral reads. It has 450 reads, of which
**50 (25 pairs) map to the virus**: that is **not acceptable without a comment**. The most likely cause is **barcode bleed**
(index hopping) from a very abundant sample on the same run, here S01. You can check it: the reads in the NTC carry S01's variants
(e.g. an A instead of the reference C at position 5753, in 4 of the NTC reads: open `results/bam/S05.bam` in IGV and go to `TOYV1:5753`). The other reads are background contamination.

Consequence: S03 has 340 reads, the same order of magnitude as the 50 reads in the NTC, so **S03 cannot be trusted**:
a good part of its signal could be contamination. Always report the NTC and interpret low-depth samples with it in mind.
:::

**3. Open `results/bam/S01.bam` in IGV (reference: `data/reference/TOYV1.fasta`). Zoom on a position where reads differ from the reference. Is it a sequencing error or a real variant? How can you tell?**

How to open it: *Genomes → Load Genome from File…* → `data/reference/TOYV1.fasta`; *File → Load from File…* → `results/bam/S01.bam`
(or `precomputed/bam/S01.bam`). Type `TOYV1:553` in the box and press Enter, then do the same for `TOYV1:1372`.
Coloured letters on the reads are bases that differ from the reference.

::: {.callout-tip collapse="true"}
## Answer
- At **position 553**, the reference has a T, but **all ~100 reads** show a **G** (the column is entirely one colour). Present in
  every read, on both strands, with good quality: it is a **real variant** (a SNP of the sample).
- At **position 1372**, only **2 reads out of ~115** show an A; the other reads match the reference. Few reads, scattered,
  with a low base quality (the two reads have Q4 and Q24: paler colour in IGV), in the second half of the reads: a **sequencing error**.

Rule of thumb: a real variant is seen in (almost) **all the reads** that cover the position; an error in **a few**.
:::

## Final question

Why do we **sort** and **index** a BAM file?

::: {.callout-tip collapse="true"}
## Answer
Sorting puts the reads in order of position along the genome. The index (`.bai`) is a table of contents that tells a program
where a given region is in the file. Together they let IGV, `samtools depth` or a variant caller **jump directly to a region**
instead of reading the whole file, and many tools refuse a BAM that is not sorted and indexed.
:::

**Next:** [Coverage and consensus](03_coverage_consensus.md).
