# From FASTQ to genome — hands-on dry lab

Practical session of the NGS training (African STARS Fellowship / CARE / Institut Pasteur): go from raw paired-end Illumina reads (R1 + R2) to a checked genome.

> **Real public data.** The reads are downloaded from NCBI SRA (run `SRR26396743`, SARS-CoV-2) and the reference is `NC_045512.2`. No synthetic data, no patient information.

## Pipeline

| Step | Tool | Purpose |
|---|---|---|
| 1. Quality control | FastQC + MultiQC | Quality of the raw reads |
| 2. Trimming | trimmomatic | Remove adapters and low-quality bases |
| 3. Assembly | SPAdes | Assemble reads into contigs / scaffolds |
| 4. Identification | Kraken2 or BLAST | Which organisms? Contamination? |
| 5. Assembly quality | QUAST | N50, length, genome fraction |
| 6. Mapping and consensus | BWA / minimap2, samtools, bcftools, iVar | Next lessons |


## Quick start

```bash
https://github.com/ndeyeawandiaye/African_STARS_Bioinformatics_training.git && cd African_STARS_Bioinformatics_training
mamba env create -f environment.yml      # or conda
conda activate analyse
```

Download the data (details in the Setup lesson):

```bash
mkdir -p data && cd data
prefetch SRR26396743
fasterq-dump --split-3 --threads 2 SRR26396743
gzip SRR26396743_1.fastq SRR26396743_2.fastq
cd ..
curl -fL --retry 5 --retry-delay 2 \
  "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=nuccore&id=NC_045512.2&rettype=fasta&retmode=text" \
  -o data/SARS-CoV-2_NC_045512.2.fasta
seqkit stats data/*.fastq.gz       # R1 and R2 must have the same number of reads
```

## Course website

https://ndeyeawandiaye.github.io/African_STARS_Bioinformatics_training/


## Troubleshooting

- `command not found`: activate the environment with `conda activate analyse`.
- Slow solver: use `mamba`.
- macOS: use `gzcat` or `gzip -dc` instead of `zcat`.
- Apple Silicon / Windows: use WSL2 on Windows; if a package is missing on ARM, see the Setup lesson.
- NCBI download fails (`curl: (56)`): retry, or download the files from the NCBI website.

## Instructor notes

- Run the whole pipeline once before the session.
- Keep `solutions/` out of the participants' copy.
- Add a `LICENSE` file (e.g. MIT for code, CC BY 4.0 for the material).