---
title: "Mapping"
subtitle: "30 min"
---

**Goal:** Align trimmed SARS-CoV-2 reads to the reference genome, evaluate mapping statistics, and inspect aligned reads in a genome browser.

Activate the course environment:

```bash
conda activate analyse
```

In this exercise, we use the paired-end reads from NCBI run `SRR26396743`, cleaned in the previous session, and the SARS-CoV-2 reference genome NC_045512.2.

## Step 1 — Index the reference genome

BWA requires an index to align reads efficiently. Samtools also creates a FASTA index, which is useful for downstream analysis and visualization.

```bash
bwa index data/SARS-CoV-2_NC_045512.2.fasta
```

```bash
samtools faidx data/SARS-CoV-2_NC_045512.2.fasta
```

**Questions**

1. What files are created by `bwa index`?
2. What is the purpose of the `.fai` file?
3. Why do we index the reference before mapping?

:::{.callout-tip collapse='true'}
## Answers

- `bwa index` creates auxiliary index files that allow BWA to search the reference efficiently.
- `samtools faidx` creates a FASTA index (`.fai`) containing sequence names, lengths, and file offsets.
- Indexing avoids rebuilding the reference search structures every time we map reads.
:::

## Step 2 — Map the trimmed reads

Create an output directory:

```bash
mkdir -p results/bam
```

Run BWA-MEM and sort the resulting alignments with Samtools:

```bash


```

Index the sorted BAM file:

```bash
samtools index results/bam/SRR26396743.bam
```

Calculate the mapping statistics and save them:

```bash
samtools flagstat results/bam/SRR26396743.bam \
  | tee results/bam/SRR26396743.flagstat.txt
```

**What do these commands do?**

- `bwa mem` aligns the paired-end reads to the reference genome.
- `-t 2` uses two threads for BWA.
- `-R` adds read-group information, including the run and sample identifiers.
- `samtools sort` sorts alignments by genomic coordinate and writes a BAM file.
- `samtools index` creates an index for the BAM file.
- `samtools flagstat` summarizes alignment and pairing statistics.
- `tee` displays the results and saves them to a text file.

**Questions**

1. What is the difference between a FASTQ file and a BAM file?
2. Why do we use a reference genome?
3. Why are the reads sorted after alignment?

**Answers**

FASTQ files contain read sequences and their base-quality scores. BAM files contain alignment records, including read positions, mapping information, and flags.

The reference genome provides the coordinate system used to locate reads along the viral genome.

Sorting arranges the alignments by genomic position, making downstream analysis and regional access more efficient.

## Step 3 — Read the mapping statistics

Display the report:

```bash
cat results/bam/SRR26396743.flagstat.txt
```

Pay particular attention to these lines:

- **in total:** total number of alignment records examined.
- **mapped:** number and percentage of mapped alignment records.
- **properly paired:** number and percentage of records belonging to pairs aligned in the expected orientation and distance.
- **primary:** primary alignment records, excluding secondary and supplementary alignments.

Remember that `samtools flagstat` reports alignment records, not necessarily read pairs. For paired-end data, one read pair normally produces two alignment records.

You can also obtain a compact summary of the BAM file:

```bash
samtools idxstats results/bam/SRR26396743.bam
```

The output lists reference sequences, their lengths, the number of mapped records, and the number of unmapped records associated with each reference.

**Questions**

1. What percentage of alignment records are mapped?
2. What percentage are properly paired?
3. How many alignment records are unmapped?
4. Does the mapping result suggest that the reads are compatible with the SARS-CoV-2 reference?
5. What other factors could explain a low mapping percentage?

**Answers**

Use the values obtained from your own run. Do not assume a particular mapping percentage before analyzing the data.

A high mapping percentage indicates that many reads align to the reference, but it does not by itself prove that the sample is free of contamination or that the resulting genome is accurate.

A low mapping percentage may reflect low-quality reads, residual adapters, a reference mismatch, contamination, or a dataset that does not contain the expected organism.

## Step 4 — Visualize the alignments in IGV

IGV (Integrative Genomics Viewer) allows you to inspect aligned reads and compare their bases with the reference genome.

First, confirm that both the BAM file and its index exist:

```bash
ls -lh results/bam/SRR26396743.bam*
```

Open IGV and load the reference genome:

1. Select **Genomes → Load Genome from File…**
2. Choose `data/ncbi/SARS-CoV-2_NC_045512.2.fasta`.
3. Select **File → Load from File…**
4. Load `results/bam/SRR26396743.bam`.
5. Navigate to a genomic region by entering a coordinate, for example `NC_045512.2:1000-2000`, if that is the chromosome label displayed by IGV.

Zoom in to examine individual reads and their mismatches relative to the reference.

**Questions**

1. Do the reads cover the whole reference genome or only some regions?
2. Can you see bases that differ from the reference?
3. Are the differences supported by multiple reads?
4. Do the supporting reads have good base quality?
5. Can you conclude that a mismatch is a true variant simply because it appears in one read?

**Answers**

A mismatch may represent a genuine variant, a sequencing error, an alignment artifact, or another technical issue.

Before interpreting a mismatch, examine its supporting read depth, base quality, mapping quality, strand distribution, and position within the reads. A single observation is not sufficient to establish a true variant.

No specific variant positions or allele frequencies are assumed in this exercise; these must be determined from the actual data.

## Step 5 — Explore read coverage

Use Samtools to calculate the number of reads covering each reference position:

```bash
samtools depth -aa results/bam/SRR26396743.bam \
  > results/bam/SRR26396743.depth.tsv
```

Calculate the mean depth across the reference, including positions with zero coverage:

```bash
awk '{sum += $3; n++} END {
  if (n > 0) printf "Mean depth: %.2f\n", sum/n;
  else print "No positions found"
}' results/bam/SRR26396743.depth.tsv
```

Calculate the proportion of reference positions covered by at least one read:

```bash
awk '{total++; if ($3 > 0) covered++}
END {
  if (total > 0)
    printf "Reference covered: %.2f%%\n", 100*covered/total;
  else
    print "No positions found"
}' results/bam/SRR26396743.depth.tsv
```

**Questions**

1. What is the mean read depth?
2. What percentage of the reference is covered by at least one read?
3. Are there regions with zero coverage?
4. Why can a high mapping percentage coexist with low coverage in some regions?

**Answers**

Mapping percentage measures how many alignment records map to the reference. Coverage describes how many reads support each reference position.

A dataset may have a high mapping percentage while still containing poorly covered regions. Those regions may be unreliable for consensus generation or variant analysis.

## Final question

Why do we **sort and index** a BAM file?

**Answer**

Sorting arranges the alignments by genomic coordinate. Indexing creates a lookup structure that allows programs such as IGV and Samtools to access a specific genomic region without scanning the entire file.

Many downstream tools require a coordinate-sorted BAM file and its index.

**Next:** [Coverage and consensus](03_coverage_consensus.md).
