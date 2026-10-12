# 03 — Coverage and consensus (45 min)

1. Compute coverage statistics:
   ```bash
   bash scripts/04_coverage.sh  # results/coverage/
   ```
2. For each sample note: mean depth, % of the genome at ≥ 10x, and the positions of the low-depth regions.
3. In IGV, look at S02. Where is the gap and how long is it? Which laboratory step could explain it?
4. Build the consensus genomes:
   ```bash
   bash scripts/05_consensus.sh # results/consensus/S0X.fa
   bash scripts/06_variants.sh  # results/variants/S0X.vcf.gz
   ```
5. Count the N in each consensus:
   ```bash
   grep -v '>' results/consensus/S01.fa | tr -cd 'N' | wc -c
   ```
6. Re-run S01 with another depth threshold and compare:
   ```bash
   MIN_DEPTH=30 RESULTS=results_d30 bash scripts/run_all.sh S01
   ```
   What changes? Why is the threshold a compromise?

**Question:** S02 has a mean depth of about 100x. Why is its consensus still incomplete?
