---
title: "FASTQ and quality control"
subtitle: "30 min"
---


**Goal:** Understand the structure of FASTQ files, assess sequencing quality, and clean paired-end reads before mapping.

Open a terminal in the course folder and activate the environment:

```bash
conda activate analyse
```

Each grey box contains a command. Copy it, paste it into the terminal, press Enter, and examine the output before continuing.

## Step 1 — Look at a read

A FASTQ file stores four lines per read: the read identifier, nucleotide sequence, a `+` separator, and a quality string. The files are compressed (`.gz`), so we use `zcat`.

```bash
zcat data/ncbi/SRR26396743_1.fastq.gz | head -4
```

**Questions**

1. Which line contains the nucleotide sequence? Which contains the quality scores?
2. What does each character in the quality string represent?
3. Convert the first five quality characters to Phred scores using `ASCII code − 33`.

**Answers**

1. Line 1 is the read identifier, line 2 is the nucleotide sequence, line 3 is `+`, and line 4 contains the quality string.
2. Each quality character encodes the estimated confidence in the corresponding base.
3. Calculate the Phred scores from the five characters displayed in your own output. Do not assume that every FASTQ file starts with the same quality characters.

The Phred quality score is calculated as:

\[
Q=-10\log_{10}(P_{\mathrm{error}})
\]

For example, Q30 corresponds to an estimated error probability of 0.1% per base.

## Step 2 — Count the reads

Each FASTQ read occupies four lines. Therefore, the number of reads equals the number of lines divided by four.

Count the reads in R1:

```bash
echo $(( $(zcat data/ncbi/SRR26396743_1.fastq.gz | wc -l) / 4 ))
```

Count the reads in R2:

```bash
echo $(( $(zcat data/ncbi/SRR26396743_2.fastq.gz | wc -l) / 4 ))
```

Alternatively, use `seqkit` to summarize both files:

```bash
seqkit stats data/ncbi/SRR26396743_*.fastq.gz
```

**Questions**

1. How many reads are present in R1 and R2?
2. Do both files contain the same number of reads?
3. What do the R1 and R2 labels mean?

**Answers**

1. Record the read counts reported by your commands.
2. For paired-end data, R1 and R2 should contain the same number of read pairs before trimming. If the counts differ, investigate the files before proceeding.
3. R1 contains the first read of each pair, while R2 contains the second read, generally sequenced from the opposite end of the same DNA fragment.

**Important:** This practice dataset is limited to a subset of the sequencing run. Its read count may therefore be much lower than the full public dataset.

## Step 3 — Quality control of the raw reads (FastQC + MultiQC)

**FastQC** analyzes individual FASTQ files and produces HTML reports. **MultiQC** combines the results into a single report.

Create an output directory:

```bash
mkdir -p results/qc_raw
```

Run FastQC:

```bash
fastqc -t 2 -o results/qc_raw data/ncbi/SRR26396743_*.fastq.gz
```

Combine the reports:

```bash
multiqc results/qc_raw -o results/qc_raw
```

Open the report in your browser:

```bash
open results/qc_raw/multiqc_report.html
```

On Linux, you can use:

```bash
xdg-open results/qc_raw/multiqc_report.html
```

Examine three sections:

- **General Statistics:** number of reads, sequence length, and overall quality indicators.
- **Per base sequence quality:** quality distribution along the reads.
- **Adapter Content:** evidence of adapter sequences remaining in the reads.

**Questions**

1. What are the minimum and maximum read lengths?
2. Does the quality decrease towards the 3′ end?
3. Is R1 better or worse than R2?
4. Does FastQC detect adapter content?
5. Which observations suggest that trimming might be useful?

**Answers**

The answers must come from your FastQC/MultiQC report.

- Quality may decrease towards the 3′ end, but the extent depends on the dataset.
- R1 and R2 can have different quality profiles.
- Adapter contamination may be present if sequencing extends beyond a short DNA fragment into adapter sequence.

A warning in FastQC does not automatically mean that a dataset is unusable. Interpret the report in the context of the sequencing experiment.

## Step 4 — Trim reads with fastp

`fastp` can detect adapters in paired-end data, trim low-quality tails, filter short reads, and generate quality-control reports.

Create the output directories:

```bash
mkdir -p results/trimmed results/fastp
```

Run `fastp`:

```bash
fastp \
  -i data/ncbi/SRR26396743_1.fastq.gz \
  -I data/ncbi/SRR26396743_2.fastq.gz \
  -o results/trimmed/SRR26396743_1.fastq.gz \
  -O results/trimmed/SRR26396743_2.fastq.gz \
  --detect_adapter_for_pe \
  --cut_tail \
  --cut_tail_mean_quality 20 \
  --qualified_quality_phred 20 \
  --length_required 50 \
  -j results/fastp/SRR26396743.json \
  -h results/fastp/SRR26396743.html \
  -w 2
```

**What do the options mean?**

| Option | Purpose |
|---|---|
| `-i`, `-I` | Input files R1 and R2 |
| `-o`, `-O` | Output files R1 and R2 |
| `--detect_adapter_for_pe` | Detect adapters in paired-end data |
| `--cut_tail` | Trim low-quality sequence at the read ends |
| `--cut_tail_mean_quality 20` | Use a mean-quality threshold of Q20 for tail trimming |
| `--qualified_quality_phred 20` | Define a base with Q20 or higher as a qualified base for filtering statistics |
| `--length_required 50` | Discard reads shorter than 50 bases after trimming |
| `-j`, `-h` | Write JSON and HTML reports |
| `-w 2` | Use two processing threads |

Read the summary printed by `fastp`. Then open:

```bash
open results/fastp/SRR26396743.html
```

**Questions**

1. How many read pairs were processed?
2. How many reads passed filtering?
3. How many bases were removed or trimmed?
4. What proportion of reads passed filtering?
5. What is the Q30 rate before and after filtering?

**Answers**

Use the actual `fastp` summary and HTML report. The amount of trimming and filtering depends on the input reads, so there is no fixed expected number of reads or bases removed.

Remember that Q30 rate and read retention are different metrics: a dataset can have a high retention rate while still containing some low-quality bases.

## Step 5 — Check the trimmed reads

Run FastQC on the cleaned files:

```bash
mkdir -p results/qc_trimmed
```

```bash
fastqc -t 2 -o results/qc_trimmed results/trimmed/*.fastq.gz
```

Combine the reports:

```bash
multiqc results/qc_trimmed -o results/qc_trimmed
```

Open the report:

```bash
open results/qc_trimmed/multiqc_report.html
```

Compare the raw and trimmed reports.

**Questions**

1. How did the read lengths change?
2. Did the quality profile improve towards the 3′ end?
3. Did adapter content decrease?
4. How many reads were retained after filtering?
5. Are the cleaned reads suitable for the next step: mapping against the SARS-CoV-2 reference genome?

**Answers**

Look for improvements in the quality profiles and reductions in adapter content. Reads may be shorter after trimming, and some may have been discarded.

Trimming does not guarantee that every FastQC warning will disappear. Decide whether the reads are suitable for mapping based on the overall quality, read lengths, adapter content, and number of retained reads.

## Final question

A base has a Phred quality score of Q20. What is the estimated probability that the base is incorrect?

**Answer**

\[
P_{\mathrm{error}}=10^{-Q/10}=10^{-2}=0.01
\]

Therefore, Q20 corresponds to an estimated error probability of **1%**, or approximately one incorrect base per 100 bases at that quality level.

At Q30, the estimated error probability is 0.1%, or approximately one incorrect base per 1,000 bases.

**Next:** [Mapping](02_mapping.md).
