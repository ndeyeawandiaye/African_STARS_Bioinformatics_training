---
title: "Mapping"
subtitle: "30 min"
---

1. Map the trimmed reads to the reference:
   ```bash
   bash scripts/03_map.sh       # results/bam/S0X.bam + flagstat
   ```
2. Read each `flagstat` file. Fill in the answer sheet: total reads, % mapped, % properly paired.
3. Which sample has a low % mapped? What could the unmapped reads be?
4. Which samples have almost no reads? What does the NTC (S05) contain, and is that acceptable?
5. Open `results/bam/S01.bam` in IGV (reference: `data/reference/TOYV1.fasta`). Zoom on a position where
   many reads differ from the reference. Is it a sequencing error or a real variant? How can you tell?

**Question:** why do we sort and index a BAM file?
