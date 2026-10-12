---
title: "FASTQ and quality control"
subtitle: "30 min"
---

**Goal:** understand what is inside a FASTQ file, check the quality of the reads, and clean them.
Open a terminal in the course folder and activate the environment (`conda activate analyse`).
Each grey box is a command: copy it, paste it, press Enter, and read the answer **before** going on.

## Step 1 — Look at a read

A FASTQ file stores four lines per read: name, sequence, `+`, quality. The file is compressed (`.gz`), so we use `zcat`.

```bash
zcat data/fastq/S01_R1.fastq.gz | head -4
```

**Questions**

1. Which line is the sequence? Which is the quality string?
2. Convert the first 5 quality characters to Phred scores (ASCII code − 33).

::: {.callout-tip collapse="true"}
## Answers
1. Line 1 = read name (`@SIM01:7:...`, with the sample barcode at the end), line 2 = sequence (150 bases),
   line 3 = `+`, line 4 = quality (150 characters: one per base).
2. The first read of S01 starts with the quality characters `C G D E G`. Their ASCII codes are 67, 71, 68, 69, 71, so
   the Phred scores are **34, 38, 35, 36, 38** (all above Q30 = at most 1 error in 1,000 bases).
:::

## Step 2 — Count the reads

Four lines per read, so the number of reads is the number of lines divided by 4.

```bash
echo $(( $(zcat data/fastq/S01_R1.fastq.gz | wc -l) / 4 ))
```

Now all samples (R1 files):

```bash
for f in data/fastq/*_R1.fastq.gz; do echo -n "$f  "; echo $(( $(zcat $f | wc -l) / 4 )); done
```

Or with `seqkit`, which also gives lengths and mean quality:

```bash
seqkit stats data/fastq/*.fastq.gz
```

::: {.callout-tip collapse="true"}
## Answers
S01: **3,333** read pairs (so 3,333 reads in R1 and 3,333 in R2). The same for S02 and S04. **S03 has only 170 pairs** and
**S05 (negative control) 225 pairs**. Always check that R1 and R2 have the same number of reads.
:::

## Step 3 — Quality control of the raw reads (FastQC + MultiQC)

**FastQC** analyses one FASTQ file and produces an HTML report. **MultiQC** collects all the reports into a single page.

```bash
mkdir -p results/qc_raw
```
```bash
fastqc -t 2 -o results/qc_raw data/fastq/*.fastq.gz
```
```bash
multiqc results/qc_raw -o results/qc_raw
```

Open `results/qc_raw/multiqc_report.html` in your browser (double-click it, or `open results/qc_raw/multiqc_report.html` on a Mac,
`xdg-open …` on Linux). Look at three sections: **General Statistics**, **Per base sequence quality**, **Adapter content**.

**Questions**

1. Which samples have fewer reads than the others?
2. Compare R1 and R2: where does the quality drop?
3. Is there adapter content?

::: {.callout-tip collapse="true"}
## Answers
1. **S03** (340 reads) and **S05** (450 reads) are far below the 6,666 reads of S01, S02 and S04.
2. In every sample, quality is highest at the start of the read and decreases towards the **3′ end**. R2 drops faster than R1
   (about 92 % of R1 bases are ≥ Q30, against about 73 % for R2). This is typical of Illumina paired-end data.
3. Yes: the **Adapter content** plot shows adapter sequence at the 3′ end of the reads. It comes from short fragments:
   when the DNA fragment is shorter than the read, the sequencer reads through into the adapter. It must be removed.
:::

## Step 4 — Trim with fastp

fastp removes the adapters, cuts the low-quality tails and drops reads that become too short. First S01 alone:

```bash
mkdir -p results/trimmed results/fastp
```
```bash
fastp -i data/fastq/S01_R1.fastq.gz -I data/fastq/S01_R2.fastq.gz \
      -o results/trimmed/S01_R1.fastq.gz -O results/trimmed/S01_R2.fastq.gz \
      --detect_adapter_for_pe --cut_tail --cut_tail_mean_quality 20 \
      --qualified_quality_phred 20 --length_required 50 \
      -j results/fastp/S01.json -h results/fastp/S01.html -w 2
```

Read the summary printed by fastp (reads before / after filtering, adapter trimmed reads, Q30 rate). Then do the same
for the four other samples (this loop repeats the same command):

```bash
for s in S02 S03 S04 S05; do
  fastp -i data/fastq/${s}_R1.fastq.gz -I data/fastq/${s}_R2.fastq.gz \
        -o results/trimmed/${s}_R1.fastq.gz -O results/trimmed/${s}_R2.fastq.gz \
        --detect_adapter_for_pe --cut_tail --cut_tail_mean_quality 20 \
        --qualified_quality_phred 20 --length_required 50 \
        -j results/fastp/${s}.json -h results/fastp/${s}.html -w 2
done
```

What the options mean: `--detect_adapter_for_pe` finds the adapters automatically; `--cut_tail` trims the 3′ end while the
quality is low; `--length_required 50` drops reads shorter than 50 bases.

## Step 5 — Check the trimmed reads

```bash
mkdir -p results/qc_trimmed
```
```bash
fastqc -t 2 -o results/qc_trimmed results/trimmed/*.fastq.gz
```
```bash
multiqc results/qc_trimmed -o results/qc_trimmed
```

**Questions**

1. How many reads and bases were removed?
2. Did the R2 tail improve? Is the adapter content gone?

::: {.callout-tip collapse="true"}
## Answers
1. Only a small part of the data: usually **a few percent of the bases** and a small number of reads (the shortest fragments).
   The exact figures are in the fastp output (*reads passed filter*) and in `results/fastp/S01.html`.
2. Yes. The quality curve of R2 stays high for longer (the poor tail was cut) and the **adapter content curve is flat**.
   Reads are now slightly shorter, on average, than 150 bases, which is normal.
:::

## Final question

A base has quality **Q20**. What is the probability that it is wrong?

::: {.callout-tip collapse="true"}
## Answer
P = 10^(−Q/10) = 10^(−2) = **1 %**: one base in 100 is expected to be wrong. At Q30 it is 1 in 1,000.
:::

**Next:** [Mapping](02_mapping.md).
