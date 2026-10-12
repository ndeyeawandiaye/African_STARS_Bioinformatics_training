---
title: "FASTQ and quality control"
subtitle: "30 min"
---

1. Look at the first read of S01 (4 lines per read):
   ```bash
   zcat data/fastq/S01_R1.fastq.gz | head -4
   ```
   Identify: read name, sequence, `+`, quality string. Convert the first 5 quality characters to Phred scores
   (ASCII code − 33).
2. How many reads does S01_R1 contain?
   ```bash
   echo $(( $(zcat data/fastq/S01_R1.fastq.gz | wc -l) / 4 ))
   ```
3. Run QC on all samples, then open the report:
   ```bash
   bash scripts/01_qc.sh        # results/qc_raw/multiqc_report.html
   ```
   - Which samples have fewer reads than the others?
   - Compare R1 and R2: where does quality drop?
   - Is there adapter content?
4. Trim and compare:
   ```bash
   bash scripts/02_trim.sh      # results/trimmed + results/qc_trimmed
   ```
   How many reads and bases were removed? Did the R2 tail improve?

**Question:** a base has Q20. What is the probability that it is wrong?
