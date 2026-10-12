---
title: "Setup"
subtitle: "About 30 minutes — do it once, before the session if you can"
---

By the end of this page you will have: **conda** installed, an environment called **`analyse`** with all the tools,
the course material on your computer, and a viewer (IGV) to look at alignments.

::: {.callout-note}
## Windows
Install **WSL2** (Ubuntu) first, then follow the *Linux* instructions inside the Ubuntu terminal.
:::

## 1. Install conda (Miniforge)

Conda is a program that installs bioinformatics tools **and** keeps them in separate "environments", so that one
project does not break another. We use **Miniforge**, a free conda installer that already points to the right
software channels (conda-forge). It also includes `mamba`, a faster installer.

### Linux

```bash
curl -L -O "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-$(uname)-$(uname -m).sh"
bash Miniforge3-$(uname)-$(uname -m).sh
```

Answer `yes` to the licence and to "initialize conda". Then **close and reopen the terminal**.

### Mac (Intel or Apple chip)

Same command (it detects your processor automatically):

```bash
curl -L -O "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-$(uname)-$(uname -m).sh"
bash Miniforge3-$(uname)-$(uname -m).sh
```

If you use Homebrew you can instead run `brew install --cask miniforge` and then `conda init "$(basename "${SHELL}")"`.
Close and reopen the terminal.

### Check

```bash
conda --version
mamba --version
```

You should see a version number for both. The prompt now starts with `(base)`.

## 2. Get the course material

```bash
git clone https://github.com/YOUR-ORG/fastq-to-genome.git
cd fastq-to-genome
ls
```

(No `git`? On the GitHub page click **Code → Download ZIP**, unzip, and open a terminal in that folder.)

## 3. Create the environment `analyse`

```bash
mamba env create -f environment.yml
```

This downloads about 20 tools: it can take 10–20 minutes. Then activate it:

```bash
conda activate analyse
```

The prompt now starts with `(analyse)`. **You must run this line in every new terminal.**

::: {.callout-warning}
## Mac with an Apple chip (M1, M2, M3…)
A few bioinformatics packages do not exist yet for Apple chips. If the installation stops with *"PackagesNotFoundError"*, use this instead:

```bash
CONDA_SUBDIR=osx-64 mamba env create -f environment.yml
conda activate analyse
conda config --env --set subdir osx-64
```
:::

## 4. Check the tools, one by one

Do **not** run a script. Type each command and look at the answer: a version number means the tool is installed.
If you see `command not found`, the environment is not active (`conda activate analyse`) or the tool failed to install —
tell the instructor, and see "Plan B" below.

```bash
fastqc --version
```
```bash
multiqc --version
```
```bash
fastp --version
```
```bash
seqkit version
```
```bash
kraken2 --version | head -1
```
```bash
spades.py --version
```
```bash
quast.py --version
```
```bash
bwa 2>&1 | grep Version
```
```bash
minimap2 --version
```
```bash
samtools --version | head -1
```
```bash
bcftools --version | head -1
```
```bash
ivar version | head -1
```
```bash
mafft --version
```
```bash
iqtree2 --version | head -1
```
```bash
fasterq-dump --version
```

## 5. Install IGV

**IGV** (Integrative Genomics Viewer) shows the reads stacked along the genome, like a zoomable photograph of an alignment.
Download the desktop version from <https://igv.org/doc/desktop/> (choose Linux or Mac), or use the browser version at <https://igv.org/app>.

## 6. Look at the samples

```bash
cat data/samples.tsv
```

There are five samples, **S01 to S05**. Four are patient samples; **S05 is a negative control (NTC, "no template control")**:
water taken through the whole protocol. A clean NTC contains (almost) no viral reads.

## 7. Real data from NCBI (SARS-CoV-2, Rift Valley fever…)

The practice data of this course are small and synthetic, so that every step runs in seconds. The commands you learn
work exactly the same on **real public data**. Here is how to get some from NCBI.

### a) Find a sequencing run

1. Open the **SRA** database: <https://www.ncbi.nlm.nih.gov/sra>
2. Search, for example:

   - SARS-CoV-2: `"Severe acute respiratory syndrome coronavirus 2"[Organism] AND "AMPLICON"[Strategy] AND "ILLUMINA"[Platform] AND "PAIRED"[Layout]`
   - Rift Valley fever: `"Rift Valley fever virus"[Organism] AND "ILLUMINA"[Platform] AND "PAIRED"[Layout]`

3. Pick a result that is **Illumina, paired-end**, with a small size (a few hundred MB at most). Note its **Run accession**:
   it starts with `SRR`, `ERR` or `DRR` (below we write `SRRXXXXXXX`: replace it with yours).
   Read the description to know which protocol was used (amplicon, capture, metagenomics).

### b) Download the reads

```bash
mkdir -p data/ncbi
cd data/ncbi
```
```bash
prefetch SRRXXXXXXX
```
```bash
fasterq-dump --split-files --threads 2 -X 200000 SRRXXXXXXX
```
```bash
gzip SRRXXXXXXX_1.fastq SRRXXXXXXX_2.fastq
cd ../..
```

`-X 200000` keeps only the first 200,000 read pairs, which is enough for practice (remove it to get everything).
`--split-files` creates `_1` (= R1) and `_2` (= R2).

Check that R1 and R2 have the same number of reads:

```bash
seqkit stats data/ncbi/*.fastq.gz
```

### c) Download the reference genome

SARS-CoV-2 (one sequence, 29.9 kb):

```bash
efetch -db nuccore -id NC_045512.2 -format fasta > data/ncbi/SARS-CoV-2_NC_045512.2.fasta
```

Rift Valley fever virus has **three segments** (L, M, S), so the reference is a FASTA file with three sequences
(RefSeq accessions NC_014397, NC_014396 and NC_014395 — check them on <https://www.ncbi.nlm.nih.gov/nuccore> before use):

```bash
efetch -db nuccore -id NC_014397,NC_014396,NC_014395 -format fasta > data/ncbi/RVFV_L_M_S.fasta
```

```bash
seqkit stats data/ncbi/*.fasta
```

::: {.callout-note}
## What changes with real data
- **Amplicon data (ARTIC):** primer sequences must be removed after mapping (`ivar trim` with the primer BED file).
- **Segmented viruses:** each segment is a separate reference sequence; coverage and consensus are produced for each one.
- **Bigger files:** the same commands just take longer.
:::

## Plan B: what if a tool will not install?

It happens (old laptop, Apple chip, no internet at the venue). You will **not** lose the session. The folder
`precomputed/` contains the **results already computed by the instructor** for the five practice samples:

| In `precomputed/` | What it is | Replaces the step |
|---|---|---|
| `bam/S01.bam` + `.bai` | where every read aligns on the genome | mapping |
| `coverage/S01.depth.tsv` | depth at each position | coverage |
| `consensus/S01.fa` | the final genome | consensus |
| `qc_summary.tsv` | one-line verdict per sample | summary |

If, say, `bwa` does not work for you, skip the mapping command and **use `precomputed/bam/S01.bam` instead of
`results/bam/S01.bam`** in the next commands. To *see* a BAM:

1. Open IGV and choose the genome: *Genomes → Load Genome from File…* → `data/reference/TOYV1.fasta`.
2. *File → Load from File…* → `precomputed/bam/S01.bam` (the `.bai` file must be in the same folder).
3. Type `TOYV1:553` in the search box and press Enter: you see the reads stacked at position 553.

## Troubleshooting

| Problem | Solution |
|---|---|
| `conda: command not found` | close and reopen the terminal; otherwise rerun the Miniforge installer and accept "initialize conda" |
| The prompt has no `(analyse)` | `conda activate analyse` |
| The environment creation is very slow | use `mamba` (not `conda`) |
| One tool is missing | install it alone: `mamba install -n analyse -c bioconda <tool>` |
