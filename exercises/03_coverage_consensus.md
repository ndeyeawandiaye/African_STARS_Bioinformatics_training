---
title: "Coverage and consensus"
subtitle: "45 min"
---

**Goal:** Measure genome coverage, identify low-depth regions, build a consensus genome, and identify candidate variants.

We will analyze the SARS-CoV-2 sequencing run `SRR26396743` from NCBI, using the trimmed reads and BAM file generated in the previous sessions.

**Input files**

- Reference genome: `data/NC_045512.2.fasta`
- Aligned reads: `results/bam/SRR26396743.sorted.bam`
- BAM index: `results/bam/SRR26396743.sorted.bam.bai`

If a previous step failed, use the corresponding precomputed files provided with the course, if available.


## Step 1 — Calculate mean depth and genome breadth at ≥10× 

For this exercise, we will use **10× depth** as a practical threshold for assessing genome completeness.

- **Mean depth:** average number of reads covering each reference position.
- **Breadth at ≥10×:** percentage of reference positions covered by at least 10 reads.

Run:

```bash
awk '{
  total += $3
  if ($3 >= 10) covered++
  positions++
}
END {
  if (positions > 0) {
    printf "Mean depth: %.1f\n", total/positions
    printf "Genome at >=10x: %.1f%%\n", 100*covered/positions
  }
}' results/coverage/SRR26396743.depth.tsv
```


## Step 2 — Build the consensus genome with iVar

A **consensus genome** represents the most strongly supported nucleotide at each reference position, subject to the calling thresholds.

Here, we will use:

- Minimum base quality: Q20
- Minimum depth: 10 reads
- Minimum proportion of reads supporting a base: 50%
- Missing or insufficiently supported positions: `N`

Create the output directories:

```bash
mkdir -p results/coverage results/consensus results/variants
```

Run `samtools mpileup` and pass its output to `ivar consensus`:

```bash
samtools mpileup \
  -aa -A -d 0 -Q 0 \
  -f data/NC_045512.2.fasta \
  results/bam/SRR26396743.sorted.bam \
  | ivar consensus \
      -p results/consensus/SRR26396743 \
      -q 20 \
      -t 0.5 \
      -m 10 \
      -n N
```
:::{.callout-tip collapse='true'}

## Options

| Command / Option | Explanation |
|---|---|
| `samtools mpileup` | Generates per-position alignment information from the BAM file. |
| `-aa` | Includes all reference positions, including positions with zero coverage. |
| `-A` | Includes anomalous read pairs/orphan reads that would otherwise be skipped. |
| `-d 0` | Removes the maximum depth limit. |
| `-Q 0` | Sets the minimum base quality threshold in mpileup to Q0. |
| `-f data/NC_045512.2.fasta` | Specifies the reference genome in FASTA format. |
| `results/bam/SRR26396743.sorted.bam` | Input BAM file containing coordinate-sorted alignments. |
| `ivar consensus` | Generates a consensus sequence from the pileup data. |
| `-p results/consensus/SRR26396743` | Sets the output file prefix. |
| `-q 20` | Uses a minimum base quality of Q20 for consensus calling. |
| `-t 0.5` | Requires a minimum base frequency of 50% to call a consensus base. |
| `-m 10` | Requires at least 10 reads covering a position. |
| `-n N` | Uses `N` for positions where a consensus base cannot be called. |

:::
This produces a consensus FASTA file, normally named:

`results/consensus/SRR26396743.fa`

Inspect its header and sequence:

```bash
head -c 300 results/consensus/SRR26396743.fa
```


## Step 3 — Measure the number of ambiguous bases

Count the number of `N` bases:

```bash
grep -v '^>' results/consensus/SRR26396743.fa \
  | tr -cd 'N' \
  | wc -c
```

Calculate the percentage of the consensus represented by `N`:

```bash
awk '
  /^>/ {next}
  {
    n += gsub(/N/, "&")
    length_total += length($0)
  }
  END {
    if (length_total > 0)
      printf "N bases: %d\nN percentage: %.2f%%\n",
             n, 100*n/length_total
  }
' results/consensus/SRR26396743.fa
```


## Step 4 — Identify candidate variants with bcftools

We will compare the aligned reads with the reference to identify candidate single-nucleotide variants and short insertions or deletions.

Generate a VCF file:

```bash
bcftools mpileup \
  -f data/NC_045512.2.fasta \
  -Q 20 \
  -d 1000000 \
  -a AD \
  results/bam/SRR26396743.sorted.bam \
  | bcftools call \
      -mv \
      --ploidy 1 \
      -Oz \
      -o results/variants/SRR26396743.vcf.gz
```
:::{.callout-tip collapse='true'}
### Options

| Command / Option | Explanation |
|---|---|
| `bcftools mpileup` | Generates per-position read data for variant detection. |
| `-f data/NC_045512.2.fasta` | Specifies the reference genome in FASTA format. |
| `-Q 20` | Excludes bases with a base quality below Q20. |
| `-d 1000000` | Sets the maximum read depth per position to 1,000,000. |
| `-a AD` | Adds allele-depth (`AD`) information. |
| `results/bam/SRR26396743.sorted.bam` | Input BAM file containing aligned reads. |
| `bcftools call` | Identifies candidate variants from the read data. |
| `-m` | Uses the multiallelic variant-calling model. |
| `-v` | Outputs variant sites only. |
| `--ploidy 1` | Assumes a haploid genome. |
| `-Oz` | Writes the VCF output in compressed BGZF format. |
| `-o results/variants/SRR26396743.vcf.gz` | Specifies the output VCF file. |

**Output:** A compressed VCF file containing candidate variants identified by comparing the sequencing reads with the SARS-CoV-2 reference genome.
:::


Index the VCF:

```bash
bcftools index results/variants/SRR26396743.vcf.gz
```

Display the variant records:

```bash
bcftools view -H results/variants/SRR26396743.vcf.gz \
  | cut -f1,2,4,5,6
```
:::{.callout-tip}
The columns displayed are:

1. Reference sequence
2. Position
3. Reference allele
4. Alternative allele
5. Variant quality (QUAL)
:::

Count the reported variant records:

```bash
bcftools view -H results/variants/SRR26396743.vcf.gz \
  | wc -l
```


## Step 5 — Change the consensus depth threshold

A higher minimum depth can make the consensus more conservative, but it can also increase the number of ambiguous bases.

Build a second consensus requiring at least 30 reads per position:

```bash
samtools mpileup \
  -aa -A -d 0 -Q 0 \
  -f data/NC_045512.2.fasta \
  results/bam/SRR26396743.sorted.bam \
  | ivar consensus \
      -p results/consensus/SRR26396743.m30 \
      -q 20 \
      -t 0.5 \
      -m 30 \
      -n N
```

Count the ambiguous bases in the second consensus:

```bash
grep -v '^>' results/consensus/SRR26396743.m30.fa \
  | tr -cd 'N' \
  | wc -c
```

Compare the results with the consensus generated at 10×.

## Step 6 — Is this genome good enough?

A genome is not simply "good" or "bad": it is **good enough for a specific purpose**, based on several quality metrics.

## The numbers that matter

| Metric | Why it matters |
|---|---|
| **Total reads / % mapped** | Indicates the amount of sequencing data and the proportion mapping to the virus. A low mapping rate may indicate contamination or poor enrichment. |
| **Mean depth** | Indicates the average sequencing coverage at each reference position. |
| **% of genome at ≥ 10× depth** | Measures how much of the genome has sufficient coverage for reliable consensus calling. |
| **% N / longest run of Ns** | Indicates missing sequence information. Long runs of Ns may correspond to missing genomic regions. |
| **Negative control (NTC)** | Checks whether viral reads are detected in a sample that should contain no viral material. |


## illustrative thresholds
These are **illustrative thresholds**, not universal standards. Adapt them to the sequencing protocol and intended analysis.


| Criterion | Good | To review | Poor |
|---|---|---|---|
| **% mapped** | ≥ 90% | 70–89.9% | < 70% |
| **Genome at ≥ 10×** | ≥ 90% | 70–89.9% | < 70% |
| **% N** | ≤ 10% | > 10–20% | > 20% |
| **Negative control** | No concerning viral signal | Investigate low-level signal | Clear evidence of contamination |

**Next:** [Is this genome good enough?](04_genome_qc_verdict.md)
