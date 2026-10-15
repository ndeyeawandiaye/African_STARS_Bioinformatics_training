---
title: "From FASTQ to assembly: QC, trimming, assembly and identification"
subtitle: "90 min"
---


**Goal:** Starting from paired-end FASTQ files (R1 + R2), assess sequencing quality, clean the reads, assemble them into contigs, identify which organisms are present (and detect contamination), and evaluate the quality of the assembly.

## Workflow overview

| Stage | Tool | Question answered |
|---|---|---|
| 1. Quality control | FastQC + MultiQC | What is the quality of the raw reads? |
| 2. Trimming | trimmomatic | Can adapters and low-quality bases be removed? |
| 3. Assembly | SPAdes | Can the reads be assembled into contigs or scaffolds? |
| 4. Identification | Kraken2 and/or BLAST | Which organisms are in the reads? Is there contamination? |
| 5. Assembly quality | QUAST | What are the N50, total length and genome fraction? |

Open a terminal in the course folder and activate the environment:

```bash
conda activate analyse
```

Check that all the tools are available:

```bash
fastqc --version && multiqc --version && trimmomatic --version && seqkit version
spades.py --version && kraken2 --version && blastn -version && quast.py --version
```

If a tool is missing, ask your instructor or install it in the environment, for example `conda install -c bioconda quast`.

Each grey box contains a command. Copy it, paste it into the terminal, press Enter, and examine the output before continuing.

---

# Part 1 — Quality control

## Step 1 — Look at a read

A FASTQ file stores four lines per read: the read identifier, nucleotide sequence, a `+` separator, and a quality string. The files are compressed (`.gz`), so we use `zcat`.

```bash
zcat data/SRR26396743_1.fastq.gz | head -4
```

**Questions**

1. Which line contains the nucleotide sequence? Which contains the quality scores?
2. What does each character in the quality string represent?

:::{.callout-tip collapse='true'}
## Answers

1. Line 1 is the read identifier, line 2 is the nucleotide sequence, line 3 is `+`, and line 4 contains the quality string.
2. Each quality character encodes the estimated confidence in the corresponding base.
:::

## Step 2 — Quality control of the raw reads (FastQC + MultiQC)

**FastQC** analyzes individual FASTQ files and produces HTML reports. **MultiQC** combines the results into a single report.

Create an output directory:

```bash
mkdir -p results/qc_raw
```

Run FastQC:

```bash
fastqc -t 2 -o results/qc_raw data/SRR26396743_*.fastq.gz
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



# Part 2 — Trimming

## Step 3 — Trim reads with trimmomatic

`trimmomatic` can detect adapters in paired-end data, trim low-quality tails, filter short reads.

Create the output directories:

```bash
mkdir -p results/trimmed results/trimmomatic
```

Run `trimmomatic`:

```bash
trimmomatic PE \
  -threads 2 \
  -phred33 \
  data/SRR26396743_1.fastq.gz \
  data/SRR26396743_2.fastq.gz \
  results/trimmed/SRR26396743_1_paired.fastq.gz \
  results/trimmed/SRR26396743_1_unpaired.fastq.gz \
  results/trimmed/SRR26396743_2_paired.fastq.gz \
  results/trimmed/SRR26396743_2_unpaired.fastq.gz \
  TRAILING:20 \
  SLIDINGWINDOW:4:20 \
  MINLEN:50
```

**What do the options mean?**

- `PE`: Processes paired-end reads.
- `-threads 2`: Uses two CPU threads.
- `-phred33`: Specifies the Phred+33 quality score encoding.
- `TRAILING:20`: Removes low-quality bases from the ends of reads when their quality score is below 20.
- `SLIDINGWINDOW:4:20`: Trims a read when the average quality score in a four-base sliding window falls below 20.
- `MINLEN:50`: Discards reads shorter than 50 bases after trimming.
- `paired`: Output files containing reads whose mates both pass filtering.
- `unpaired`: Output files containing reads whose mates do not both pass filtering.


## Step 4 — Check the trimmed reads

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


# Part 3 — Assembly

## Step 5 — Assemble the reads with SPAdes

An assembler joins overlapping reads into longer sequences called **contigs**. When paired-end information links contigs together, they can be ordered into **scaffolds**. **SPAdes** builds a de Bruijn graph from the reads and uses the R1/R2 pairing to resolve ambiguities.

Run SPAdes on the trimmed reads:

```bash
spades.py \
  -1 results/trimmed/SRR26396743_1.fastq.gz \
  -2 results/trimmed/SRR26396743_2.fastq.gz \
  --meta \
  -t 2 \
  -o results/spades
```

| Option | Purpose |
|---|---|
| `-1`, `-2` | Trimmed R1 and R2 files (paired reads) |
| `--meta` | metagenomic mode|
| `-t 2` | Use two threads |
| `-o` | Output directory |


When SPAdes finishes, look at the output folder:

```bash
ls results/spades
```

The main files are:

- `contigs.fasta`: assembled contigs
- `scaffolds.fasta`: contigs linked into scaffolds using paired-end information
- `spades.log`: log of the run


List the five longest contigs:

```bash
seqkit sort -l -r results/spades/contigs.fasta | seqkit fx2tab -n -l | head -5
```
:::{.callout-tip collapse='true'}
## result

| Metric | Contigs | Scaffolds |
|:--|--:|--:|
| Number of sequences | 14 | 12 |
| Total length (bp) | 30,249 | 30,449 |
| Longest sequence (bp) | 12,657 | 21,827 |
| N50 (bp) | 9,070 | 21,827 |
| N50_num | 2 | 1 |
| Number of `N` bases | 0 | 200 |

:::
---

# Part 4 — Identification

## Step 6 — Which organisms are in the reads? (Kraken2 or BLAST)

Assembling is not enough: we must verify that the sequences really come from the expected organism, and detect possible contamination (human DNA, bacteria, other viruses). Two complementary approaches are available.

### Option A — Kraken2 on the reads

**Kraken2** assigns a taxonomic label to each read by comparing its k-mers to a reference database. It is fast and gives an overview of **all** the organisms in the sample.

Create the output directory:

```bash
mkdir -p results/kraken2
```

Run Kraken2 on the trimmed read pairs. Replace `db/kraken2` with the path of the Kraken2 database provided for the course:

```bash
kraken2 \
  --db db/kraken2 \
  --paired \
  --gzip-compressed \
  --threads 2 \
  --report results/kraken2/SRR26396743.report \
  --output results/kraken2/SRR26396743.kraken \
  results/trimmed/SRR26396743_1.fastq.gz \
  results/trimmed/SRR26396743_2.fastq.gz
```

Look at the taxonomic summary:

```bash
head -20 results/kraken2/SRR26396743.report
```

The report has six columns: percentage of reads in the clade, number of reads in the clade, number of reads assigned directly to the taxon, rank code (`U` unclassified, `D` domain, `G` genus, `S` species, …), NCBI taxonomy ID, and scientific name.

Show only the species-level lines, sorted by percentage:

```bash
awk '$4=="S"' results/kraken2/SRR26396743.report | sort -k1,1nr | head -10
```

**Note:** a complete Kraken2 database (e.g. Standard) is very large. For this practical, a small database (such as a viral or MiniKraken index) is sufficient. Indexes are listed at <https://benlangmead.github.io/aws-indexes/k2>.

### Option B — BLAST on the contigs

**BLAST** aligns a sequence against a reference database and reports the best matches. It is slower but more precise, and works well on a few long contigs.

Extract the longest contig:

```bash
seqkit sort -l -r results/spades/contigs.fasta | seqkit head -n 1 > results/spades/longest_contig.fasta
```

Run `blastn` against the NCBI nucleotide database (remote search, internet connection required):

```bash
blastn \
  -query results/spades/longest_contig.fasta \
  -db nt \
  -remote \
  -max_target_seqs 5 \
  -outfmt "6 qseqid sseqid stitle pident length evalue bitscore" \
  -out results/spades/longest_contig.blast.tsv
```

```bash
cat results/spades/longest_contig.blast.tsv
```

The columns are: query ID, subject ID, subject title, percent identity, alignment length, E-value, and bit score.

You can also paste the sequence into the web interface: <https://blast.ncbi.nlm.nih.gov/Blast.cgi> (choose *Nucleotide BLAST*).


---

# Part 5 — Assembly quality

## Step 7 — Evaluate the assembly with QUAST

**QUAST** computes statistics describing an assembly. When a reference genome is provided, it also measures how much of the reference is covered by the assembly.

Create the output directory and run QUAST. Replace the reference path with the SARS-CoV-2 reference genome (NC_045512.2) provided in the course folder:

```bash
mkdir -p results/quast
```

```bash
quast.py \
  results/spades/contigs.fasta \
  results/spades/scaffolds.fasta \
  -r data/NC_045512.2.fasta \
  --min-contig 200 \
  -t 2 \
  -o results/quast
```

| Option | Purpose |
|---|---|
| `-r` | Reference genome (needed for genome fraction, misassemblies, NGA50) |
| `--min-contig 200` | Ignore contigs shorter than 200 bp |
| `-t 2` | Use two threads |
| `-o` | Output directory |

Display the text report and open the HTML report:

```bash
cat results/quast/report.txt
```

```bash
open results/quast/report.html
```
:::{.callout-tip collapse='true'}
## Interpretation

### Key Assembly Quality Metrics

#### 1. Assembly statistics (reference-independent)

These metrics describe the assembled sequences without requiring a reference genome.

| Metric | Meaning |
|---|---|
| `# contigs` | Number of assembled contigs meeting the specified minimum length. Fewer contigs can indicate a more continuous assembly. |
| `Largest contig` | Length of the longest assembled contig, in base pairs (bp). |
| `Total length` | Sum of the lengths of all assembled contigs or scaffolds. |
| `Total length (>= 1,000 bp)` | Combined length of sequences that are at least 1,000 bp long. |
| `Total length (>= 10,000 bp)` | Combined length of sequences that are at least 10,000 bp long. |
| `Total length (>= 50,000 bp)` | Combined length of sequences that are at least 50,000 bp long. |
| `N50` | Length of the contig or scaffold at which sequences of that length or longer account for at least 50% of the total assembly length. |
| `L50` | Minimum number of the longest contigs or scaffolds needed to account for at least 50% of the total assembly length. |
| `# N's` | Total number of ambiguous nucleotide positions (`N`) in the assembly, usually representing unresolved sequence gaps. |

#### 2. Alignment-based statistics (reference-dependent)

These metrics evaluate the assembly by comparing it with a reference genome.

| Metric | Meaning |
|---|---|
| `Genome fraction (%)` | Percentage of the reference genome covered by the assembled sequences. |
| `Duplication ratio` | Ratio of the total aligned length, including overlapping or duplicated alignments, to the reference genome length. A value near 1 generally indicates limited excess aligned sequence. |
| `Largest alignment` | Length of the longest alignment between an assembled sequence and the reference genome. |
| `Total aligned length` | Sum of the lengths of assembly regions aligned to the reference, according to the tool's alignment rules. |
| `NGA50` | Reference-based continuity metric calculated from aligned assembly blocks using the reference genome length as the benchmark. |
| `LGA50` | Minimum number of the longest aligned blocks needed to cover at least 50% of the reference genome. |
| `# misassemblies` | Number of structural inconsistencies detected when aligning the assembly to the reference genome. |
| `Misassembled contigs length` | Total length of contigs classified as misassembled by the evaluation tool. |
| `# mismatches per 100 kbp` | Number of aligned nucleotide positions that differ from the reference, normalized to 100,000 aligned bases. |
| `# indels per 100 kbp` | Number of insertion and deletion events detected in the alignments, normalized to 100,000 aligned bases. |
| `# N's per 100 kbp` | Number of ambiguous bases (`N`) per 100,000 bases of assembly sequence. |

#### 3. Interpretation guidelines

- **Continuity:** Fewer contigs, a larger longest contig, and higher N50/NGA50 values generally indicate a more continuous assembly.
- **Completeness:** A higher genome fraction indicates that more of the reference genome is represented in the assembly.
- **Structural consistency:** Fewer detected misassemblies indicate better agreement with the reference structure.
- **Sequence accuracy:** Lower mismatch and indel rates indicate fewer differences from the reference, although genuine biological variation can also contribute to these differences.
- **Ambiguous bases:** A high number of `N` bases indicates unresolved sequence positions, often associated with gaps in scaffolds.
- **Total length:** An assembly length close to the expected genome length can be reassuring, but does not by itself demonstrate completeness or accuracy.

**Important:** No single metric is sufficient to assess assembly quality. Interpret continuity, completeness, structural consistency, and sequence accuracy together. Metrics such as N50 and NGA50 are not directly interchangeable because they use different reference-length benchmarks.
:::
---

## Step 8 — Summarize your results

Complete this table with your own values:

| Stage | Metric | Value |
|---|---|---|
| Raw reads | Read pairs | |
| Raw reads | Adapter content detected? | |
| Trimming | Read pairs after trimmomatic | |
| Trimming | Q30 rate after filtering | |
| Assembly | Number of contigs | |
| Assembly | Longest contig (bp) | |
| Identification | Dominant species (Kraken2 / BLAST) | |
| Identification | Contamination detected? | |
| Assembly quality | N50 | |
| Assembly quality | Genome fraction (%) | |



**Next:** [Mapping](02_mapping.md).
