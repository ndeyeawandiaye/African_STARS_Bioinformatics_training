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

:::{.callout-tip collapse='true'}
## Installing WSL2 with Ubuntu (Windows only)

WSL2 (Windows Subsystem for Linux 2) allows you to run a Linux environment, such as Ubuntu, directly on Windows without installing a separate virtual machine.

**Step 1: Open PowerShell as administrator**

1. Open the Windows Start menu.
2. Search for `PowerShell`.
3. Right-click it and select **Run as administrator**.

**Step 2: Install WSL2 and Ubuntu**

Run the following command in PowerShell:

```powershell
wsl --install
```

Restart your computer if prompted.

**Step 3: Set up Ubuntu**

1. Open Ubuntu from the Windows Start menu.
2. Create a Linux username and password when prompted.
3. Wait for the initial setup to finish.

*Note:* When entering your password, no characters will appear on the screen. This is normal.

**Step 4: Update Ubuntu**

In the Ubuntu terminal, run:

```bash
sudo apt update
sudo apt upgrade -y
```

**Step 5: Verify the installation**

Open PowerShell and run:

```powershell
wsl --list --verbose
```

Check that Ubuntu uses WSL version `2`.

If necessary, set Ubuntu to WSL2 with:

```powershell
wsl --set-version Ubuntu 2
```

You can now follow the Linux instructions in this course inside the Ubuntu terminal.

**Official documentation:** [Install WSL — Microsoft Learn](https://learn.microsoft.com/en-us/windows/wsl/install)

> **Important:** These instructions apply only to Windows. If you are using macOS, you do not need WSL2; use the macOS Terminal and follow compatible instructions instead.
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
trimmomatic -version
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
fasterq-dump --split-3 --threads 2  SRR26396743
```
```bash
gzip SRR26396743_1.fastq SRR26396743_2.fastq
cd ..
```

`--split-3` separates paired-end reads into separate FASTQ files: two files for reads that form a pair (_1.fastq and _2.fastq) and a third file (.fastq) for reads that do not have a matching mate.

Check that R1 and R2 have the same number of reads:

```bash
seqkit stats data/*.fastq.gz
```
:::{.callout-tip collapse='true'}
### Results
| File | Format | Type | Number of reads | Total bases | Min. length | Average length | Max. length |
|---|---|---|---:|---:|---:|---:|---:|
| `SRR26396743_1.fastq.gz` | FASTQ | DNA | 330,144 | 48,517,409 | 51 | 147.0 | 151 |
| `SRR26396743_2.fastq.gz` | FASTQ | DNA | 330,185 | 48,275,763 | 50 | 146.2 | 151 |
:::


### c) Download the reference genome

SARS-CoV-2 (one sequence, 29.9 kb):


```bash
curl -fL --retry 5 --retry-delay 2 \
  "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=nuccore&id=NC_045512.2&rettype=fasta&retmode=text" \
  -o data/SARS-CoV-2_NC_045512.2.fasta
```
:::{.callout-tip }
- `-f`: Fail if the server returns an HTTP error.
- `-L`: Follow redirects automatically.
- `--retry 5`: Retry failed requests up to five times.
- `--retry-delay 2`: Wait two seconds between retries.
- `-o`: Save the downloaded content to a specified file.
:::

```bash
seqkit stats data/*.fasta
```
:::{.callout-tip collapse='true'}
### Results
| File | Format | Type | Number of reads | Total bases | Min. length | Average length | Max. length |
|---|---|---|---:|---:|---:|---:|---:|
data/NC_045512.2.fasta | FASTA | DNA | 1 | 29,903 | 29,903 | 29,903 | 29,903

:::

## Troubleshooting

| Problem | Solution |
|---|---|
| `conda: command not found` | close and reopen the terminal; otherwise rerun the Miniforge installer and accept "initialize conda" |
| The prompt has no `(analyse)` | `conda activate analyse` |
| The environment creation is very slow | use `mamba` (not `conda`) |
| One tool is missing | install it alone: `mamba install -n analyse -c bioconda <tool>` |
