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
bwa index data/NC_045512.2.fasta
```

```bash
samtools faidx data/NC_045512.2.fasta
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

Align the paired-end reads :

```bash
bwa mem \
  data/NC_045512.2.fasta \
  results/trimmed/SRR26396743_1_paired.fastq.gz \
  results/trimmed/SRR26396743_2_paired.fastq.gz \
  > results/bam/SRR26396743.sam

```

Convert to BAM and sort the alignments

```bash

samtools sort \
  -@ 2 \
  -o results/bam/SRR26396743.sorted.bam \
  results/bam/SRR26396743.sam

```

Index the sorted BAM file:

```bash
samtools index results/bam/SRR26396743.sorted.bam
```

Calculate the mapping statistics and save them:

```bash
samtools flagstat results/bam/SRR26396743.sorted.bam  > results/bam/SRR26396743.flagstat.txt
```

**What do these commands do?**

- `bwa mem` aligns the paired-end reads to the reference genome.
- `-t 2` uses two threads for BWA.
- `-R` adds read-group information, including the run and sample identifiers.
- `samtools sort` sorts alignments by genomic coordinate and writes a BAM file.
- `samtools index` creates an index for the BAM file.
- `samtools flagstat` summarizes alignment and pairing statistics.

**Questions**

1. What is the difference between a FASTQ file and a BAM file?
2. Why do we use a reference genome?
3. Why are the reads sorted after alignment?

:::{.callout-tip collapse='true'}

## Answers

FASTQ files contain read sequences and their base-quality scores. BAM files contain alignment records, including read positions, mapping information, and flags.

The reference genome provides the coordinate system used to locate reads along the viral genome.

Sorting arranges the alignments by genomic position, making downstream analysis and regional access more efficient.
:::

## Step 3 — Read the mapping statistics

Display the report:

```bash
cat results/bam/SRR26396743.flagstat.txt
```
:::{.callout-tip}
## Pay particular attention to these lines:

- **in total:** total number of alignment records examined.
- **mapped:** number and percentage of mapped alignment records.
- **properly paired:** number and percentage of records belonging to pairs aligned in the expected orientation and distance.
- **primary:** primary alignment records, excluding secondary and supplementary alignments.
:::


:::{.callout-tip collapse='true'}

### Alignment Quality Assessment

After mapping the paired-end reads to the SARS-CoV-2 reference genome using BWA-MEM, `samtools flagstat` was used to summarize the alignment results.

| Metric | Result | Meaning |
|---|---:|---|
| Total reads | 662,332 | Total number of alignment records, including primary, secondary, and supplementary records. |
| Primary alignments | 659,100 | Number of primary alignment records, representing the main alignment for each read. |
| Secondary alignments | 0 | No secondary alignment records were reported. |
| Supplementary alignments | 3,232 | Additional alignment records for reads whose alignments are split across multiple genomic regions. |
| Duplicates | 0 | No reads were marked as duplicates in this BAM file. This does not prove that PCR or optical duplicates are absent. |
| Mapped reads | 662,193 (99.98%) | Percentage of alignment records classified as mapped. |
| Primary mapped reads | 658,961 (99.98%) | Percentage of primary alignment records classified as mapped. |
| Paired reads | 659,100 | Number of primary records identified as belonging to paired-end sequencing data. |
| Read 1 | 329,550 | Number of primary records identified as the first mate. |
| Read 2 | 329,550 | Number of primary records identified as the second mate. |
| Properly paired | 640,776 (97.22%) | Number of reads whose pairs satisfy BWA-MEM's expected pairing criteria. |
| Both mates mapped | 658,958 | Number of primary reads for which both the read and its mate are mapped. |
| Singletons | 3 (0.00%) | Number of primary reads mapped while their mate is unmapped. |

### Interpretation

**Mapping rate:** Approximately 99.98% of primary reads mapped to the reference genome. This high mapping rate indicates that the reads are highly compatible with the SARS-CoV-2 reference sequence.

**Properly paired reads:** Approximately 97.22% of primary reads were classified as properly paired. This suggests that most read pairs have an expected orientation and insert size.

**Supplementary alignments:** The 3,232 supplementary records represent additional alignments, often produced when a read aligns in multiple segments. These are alignment records, not necessarily additional sequencing reads.

**Singletons:** Only three primary reads were mapped while their mates were unmapped, representing a very small fraction of the data.

**Important limitation:** A high mapping rate does not, by itself, confirm that the genome assembly is complete or that all mapped bases are accurate. Coverage depth, coverage uniformity, mapping quality, and variant-level evidence should also be examined.

:::

Remember that `samtools flagstat` reports alignment records, not necessarily read pairs. For paired-end data, one read pair normally produces two alignment records.

You can also obtain a compact summary of the BAM file:

```bash
samtools idxstats results/bam/SRR26396743.sorted.bam
```

The output lists reference sequences, their lengths, the number of mapped records, and the number of unmapped records associated with each reference.


## Step 4 — Visualize the alignments in IGV

IGV (Integrative Genomics Viewer) allows you to inspect aligned reads and compare their bases with the reference genome.

First, confirm that both the BAM file and its index exist:

```bash
ls -lh results/bam/SRR26396743.sorted.bam*
```

Open IGV and load the reference genome:

1. Select **Genomes → Load Genome from File…**
2. Choose `data/NC_045512.2.fasta`.
3. Select **File → Load from File…**
4. Load `results/bam/SRR26396743.sorted.bam`.
5. Navigate to a genomic region by entering a coordinate, for example `NC_045512.2:1000-2000`, if that is the chromosome label displayed by IGV.

Zoom in to examine individual reads and their mismatches relative to the reference.

**Questions**

1. Do the reads cover the whole reference genome or only some regions?
2. Can you see bases that differ from the reference?
3. Are the differences supported by multiple reads?
4. Do the supporting reads have good base quality?
5. Can you conclude that a mismatch is a true variant simply because it appears in one read?


## Step 5 — Explore read coverage

```bash
mkdir -p results/coverage
```

Use Samtools to calculate the number of reads covering each reference position:

```bash
samtools depth -aa results/bam/SRR26396743.sorted.bam \
  > results/coverage/SRR26396743.depth.tsv
```

Obtain a summary with Samtools:

```bash
samtools coverage results/bam/SRR26396743.sorted.bam
```

:::{.callout-tip collapse='true'}
## Coverage statistics

| Metric | Result | Meaning |
|---|---:|---|
| `rname` | `NC_045512.2` | Name of the reference sequence. |
| `startpos` | 1 | First reference position included in the analysis. |
| `endpos` | 29,903 | Last reference position included in the analysis. |
| `numreads` | 662,193 | Number of alignment records overlapping the reference region. |
| `covbases` | 29,785 | Number of reference bases covered by at least one aligned read. |
| `coverage (%)` | 99.605% | Percentage of reference bases covered by at least one aligned read. |
| `meandepth` | 99.61× | Average sequencing depth across the reference region. |
| `meanbaseq` | 38 | Mean base quality score, indicating high confidence in the sequenced nucleotides. |
| `meanmapq` | 60 | Mean mapping quality score, indicating high confidence in read placement. |

:::

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



**Next:** [Coverage and consensus](03_coverage_consensus.md).
