---
title: "Coverage and consensus"
subtitle: "45 min"
---

**Goal:** Measure genome coverage, identify low-depth regions, build a consensus genome, and identify candidate variants.

We will analyze the SARS-CoV-2 sequencing run `SRR26396743` from NCBI, using the trimmed reads and BAM file generated in the previous sessions.

**Input files**

- Reference genome: `data/ncbi/SARS-CoV-2_NC_045512.2.fasta`
- Aligned reads: `results/bam/SRR26396743.bam`
- BAM index: `results/bam/SRR26396743.bam.bai`

If a previous step failed, use the corresponding precomputed files provided with the course, if available.

## Step 1 — Calculate depth at every position

**Depth** is the number of reads covering a reference position. We use `-a` to include positions with zero coverage.

Create the output directories:

```bash
mkdir -p results/coverage results/consensus results/variants
```

Calculate the depth:

```bash
samtools depth -aa \
  results/bam/SRR26396743.bam \
  > results/coverage/SRR26396743.depth.tsv
```

Inspect the first three lines:

```bash
head -3 results/coverage/SRR26396743.depth.tsv
```

The output contains three columns:

1. Reference sequence name
2. Position
3. Read depth

Obtain a summary with Samtools:

```bash
samtools coverage results/bam/SRR26396743.bam
```

**Questions**

1. What is the depth at the first three reference positions?
2. Are there positions with zero coverage?
3. What are the mean depth and percentage of the reference covered by at least one read?

**Answer**

The depth varies along the genome. A position with zero coverage has no aligned reads supporting a base call. The summary values must be obtained from your own output.

## Step 2 — Calculate mean depth and genome breadth at ≥10× 

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

**Questions**

1. What is the mean depth?
2. What percentage of the genome has at least 10× coverage?
3. Does the mean depth alone tell you whether the genome is complete?

**Answer**

No. A high mean depth can coexist with poorly covered regions. Always examine both mean depth and breadth of coverage.

## Step 3 — Identify low-depth regions

We will identify consecutive positions with depth below 10× and report them as intervals.

```bash
awk 'BEGIN {OFS="\t"}
{
  if ($3 < 10) {
    if (!on) {
      start = $2
      on = 1
    }
    end = $2
  } else if (on) {
    print $1, start-1, end
    on = 0
  }
}
END {
  if (on) print $1, start-1, end
}' results/coverage/SRR26396743.depth.tsv \
  > results/coverage/SRR26396743.low_depth.bed
```

Inspect the intervals:

```bash
cat results/coverage/SRR26396743.low_depth.bed
```

Each line contains the reference name, interval start, and interval end in BED format.

**Questions**

1. How many low-depth intervals were identified?
2. What are their coordinates?
3. Which interval is the longest?
4. Are the low-depth regions located near the ends of the genome or in internal regions?

**Answer**

Use the generated BED file to identify the actual intervals. Low coverage near the genome ends can result from limitations in library preparation, read trimming, or the sequencing design. Internal gaps can have several causes, including uneven coverage, amplicon dropout, or local alignment issues. Coverage alone does not establish the cause.

## Step 4 — Visualize coverage in IGV

Open IGV and load:

- Reference: `data/ncbi/SARS-CoV-2_NC_045512.2.fasta`
- Alignment: `results/bam/SRR26396743.bam`

Inspect one of the low-depth intervals identified in Step 3.

**Questions**

1. Is coverage uniform across the region?
2. Is the region completely uncovered or only poorly covered?
3. Do reads stop abruptly at a particular coordinate?
4. What additional information would help determine why the region has low coverage?

**Answer**

IGV helps distinguish a complete coverage gap from a region with reduced depth. The shape of the coverage profile may suggest a technical issue, but further information about the library preparation and sequencing protocol is needed to establish the cause.

## Step 5 — Build the consensus genome with iVar

A **consensus genome** represents the most strongly supported nucleotide at each reference position, subject to the calling thresholds.

Here, we will use:

- Minimum base quality: Q20
- Minimum depth: 10 reads
- Minimum proportion of reads supporting a base: 50%
- Missing or insufficiently supported positions: `N`

Run `samtools mpileup` and pass its output to `ivar consensus`:

```bash
samtools mpileup \
  -aa -A -d 0 -Q 0 \
  -f data/ncbi/SARS-CoV-2_NC_045512.2.fasta \
  results/bam/SRR26396743.bam \
  | ivar consensus \
      -p results/consensus/SRR26396743 \
      -q 20 \
      -t 0.5 \
      -m 10 \
      -n N
```

This produces a consensus FASTA file, normally named:

`results/consensus/SRR26396743.fa`

Inspect its header and sequence:

```bash
head -c 300 results/consensus/SRR26396743.fa
```

**Questions**

1. What is the length of the consensus?
2. Why are some positions represented by `N`?
3. What happens when a position has fewer than 10 reads?
4. Does a consensus sequence necessarily represent a perfect reconstruction of the original viral genome?

**Answer**

A consensus can contain `N` where the evidence is insufficient under the selected thresholds. It is an estimate derived from the available reads, not a guarantee of a perfectly reconstructed genome.

The consensus quality depends on depth, base quality, mapping quality, the consensus thresholds, and the quality of the underlying sequencing data.

## Step 6 — Measure the number of ambiguous bases

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

Find the longest consecutive run of `N` bases:

```bash
grep -v '^>' results/consensus/SRR26396743.fa \
  | tr -d '\n' \
  | grep -o 'N\+' \
  | awk '{print length}' \
  | sort -n \
  | tail -1
```

If no `N` bases are present, the last command produces no output; interpret that as zero.

**Questions**

1. How many `N` bases are present?
2. What percentage of the consensus is ambiguous?
3. What is the longest consecutive run of `N`?
4. Where are the longest ambiguous regions located?

**Answer**

All values should be measured from the generated consensus. A large number of `N` bases or a long consecutive run indicates regions that cannot be confidently resolved with the chosen thresholds.

## Step 7 — Identify candidate variants with bcftools

We will compare the aligned reads with the reference to identify candidate single-nucleotide variants and short insertions or deletions.

Generate a VCF file:

```bash
bcftools mpileup \
  -f data/ncbi/SARS-CoV-2_NC_045512.2.fasta \
  -Q 20 \
  -d 1000000 \
  -a AD \
  results/bam/SRR26396743.bam \
  | bcftools call \
      -mv \
      --ploidy 1 \
      -Oz \
      -o results/variants/SRR26396743.vcf.gz
```

Index the VCF:

```bash
bcftools index results/variants/SRR26396743.vcf.gz
```

Display the variant records:

```bash
bcftools view -H results/variants/SRR26396743.vcf.gz \
  | cut -f1,2,4,5,6
```

The columns displayed are:

1. Reference sequence
2. Position
3. Reference allele
4. Alternative allele
5. Variant quality (QUAL)

Count the reported variant records:

```bash
bcftools view -H results/variants/SRR26396743.vcf.gz \
  | wc -l
```

**Questions**

1. How many variant records were reported?
2. Which reference positions contain candidate variants?
3. Do the variants have good read support?
4. Can you confirm that a variant is real based only on its presence in the VCF?

**Answer**

The VCF contains candidate variants identified by the caller. Each candidate must be interpreted using its read depth, allele support, base quality, mapping quality, and alignment context.

A variant record is not automatically proof of a biological mutation. Examine suspicious calls in IGV and apply suitable quality filters before downstream analyses.

## Step 8 — Change the consensus depth threshold

A higher minimum depth can make the consensus more conservative, but it can also increase the number of ambiguous bases.

Build a second consensus requiring at least 30 reads per position:

```bash
samtools mpileup \
  -aa -A -d 0 -Q 0 \
  -f data/ncbi/SARS-CoV-2_NC_045512.2.fasta \
  results/bam/SRR26396743.bam \
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

**Questions**

1. Did the number of `N` bases change?
2. Did the consensus become more or less complete?
3. Why might a laboratory choose a higher depth threshold?

**Answer**

A higher threshold may increase the number of ambiguous bases because positions supported by 10–29 reads no longer meet the minimum-depth requirement. This illustrates the trade-off between the completeness of the consensus and the strictness of the calling criteria.

A suitable threshold depends on the sequencing protocol, the intended use, and the laboratory's validated quality criteria.

## Final question

The genome has a mean depth of 100×, but 15% of its positions have zero coverage. Can you consider the consensus complete?

**Answer**

No. Mean depth is an average and can conceal large coverage gaps. Assess mean depth, breadth at relevant thresholds, low-depth intervals, and the number and distribution of `N` bases before deciding whether a consensus is suitable for its intended purpose.

**Next:** [Is this genome good enough?](04_genome_qc_verdict.md)
