---
title: "Setup"
subtitle: "15 min"
---

1. Get the repository and enter it.
   ```bash
   git clone <URL-OF-THE-REPO> fastq-to-genome && cd fastq-to-genome
   ```
2. Create and activate the environment (once).
   ```bash
   mamba env create -f environment.yml    # or: conda env create -f environment.yml
   conda activate fastq2genome
   ```
3. Check that everything is installed.
   ```bash
   bash scripts/00_check_setup.sh
   ```
4. Open `data/samples.tsv`: five samples (S01–S05), one of them a negative control (NTC).

**Tool will not install?** Use plan B: skip to `precomputed/` (see its README) and open the BAMs in IGV.
