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

## 1. Install Conda (Miniconda)

Conda is a program that installs bioinformatics tools and keeps them in separate **environments**, so that one project does not break another. We use **Miniconda**, a lightweight, free Conda installer. We will add the `conda-forge` and `bioconda` channels to install the bioinformatics tools required for this course.

### Linux

Download and install the latest Miniconda installer for your system:

```bash
mkdir -p ~/miniconda-installer
cd ~/miniconda-installer

curl -LO https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-$(uname -m).sh
bash Miniconda3-latest-Linux-$(uname -m).sh
```

Follow the instructions. Accept the licence and answer **yes** when asked whether to initialize Conda. Then close and reopen the terminal.

### Mac (Intel or Apple chip)

Download and install Miniconda:

```bash
mkdir -p ~/miniconda-installer
cd ~/miniconda-installer

curl -LO https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-$(uname -m).sh
bash Miniconda3-latest-MacOSX-$(uname -m).sh
```

Follow the instructions. Accept the licence and initialize Conda when prompted. Then close and reopen the terminal.

### Configure Conda channels

Run these commands once:

```bash
conda config --add channels defaults
conda config --add channels bioconda
conda config --add channels conda-forge
conda config --set channel_priority strict
```

### Check the installation

```bash
conda --version
conda info
```

You should see the Conda version and installation details. The terminal prompt may start with `(base)`.

**Note:** Miniconda does not include `mamba` by default. You can use `conda` instead, or install `mamba` in the base environment:

```bash
conda install -n base -c conda-forge mamba
```


## 2. Create the Conda environment `analyse`

If you installed `mamba`, run:

```bash
mamba env create -f environment.yml
```

Otherwise, use:

```bash
conda env create -f environment.yml
```

The installation may take 10–20 minutes or longer, depending on your internet connection and computer.

Activate the environment:

```bash
conda activate analyse
```

The prompt should now start with `(analyse)`. **Run this activation command in every new terminal before using the course tools.**

# Warning: Mac with an Apple chip (M1, M2, M3, M4…)

Most common bioinformatics tools are available for Apple Silicon, but some packages may not be. If environment creation fails with `PackagesNotFoundError`, first check whether all required packages support your Mac's architecture.

As a fallback, you can try creating an Intel-compatible environment using Rosetta 2, provided it is installed and supported by your setup. Do not force `osx-64` for the entire environment unless necessary, because this can require additional compatibility configuration and may run more slowly.

## 3. Check the tools, one by one

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

## 4. Install IGV

**IGV** (Integrative Genomics Viewer) shows the reads stacked along the genome, like a zoomable photograph of an alignment.
Download the desktop version from <https://igv.org/doc/desktop/> (choose Linux or Mac), or use the browser version at <https://igv.org/app>.


## 5. Real data from NCBI (SARS-CoV-2, Rift Valley fever…)

The practice data of this course are small, so that every step runs in seconds. The commands you learn
work exactly the same on **real public data**. Here is how to get some from NCBI.

### a) Find a sequencing run

1. Open the **SRA** database: <https://www.ncbi.nlm.nih.gov/sra>
2. Search your pathogene, for example:

   - Rift Valley fever: `"Rift Valley fever virus"[Organism] AND "ILLUMINA"[Platform] AND "PAIRED"[Layout]`

3. Pick a result that is **Illumina, paired-end**, with a small size (a few hundred MB at most). Note its **Run accession**:
   it starts with `SRR`, `ERR` or `DRR` (below we write `SRRXXXXXXX`: replace it with yours).
   Read the description to know which protocol was used (amplicon, capture, metagenomics).

### b) Download the reads

```bash
mkdir -p data
cd data
```
```bash
prefetch SRR26396743
```
```bash
fasterq-dump --split-files --threads 2 -X 200000 SRR26396743
```
```bash
gzip SRR26396743_1.fastq SRR26396743_2.fastq
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

## Troubleshooting

| Problem | Solution |
|---|---|
| `conda: command not found` | close and reopen the terminal; otherwise rerun the Miniforge installer and accept "initialize conda" |
| The prompt has no `(analyse)` | `conda activate analyse` |
| The environment creation is very slow | use `mamba` (not `conda`) |
| One tool is missing | install it alone: `mamba install -n analyse -c bioconda <tool>` |
