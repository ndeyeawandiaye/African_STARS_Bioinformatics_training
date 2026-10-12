# 04 — Is this genome good enough? (30 min)

1. Build the summary table:
   ```bash
   python3 scripts/07_summary.py       # results/qc_summary.tsv
   ```
2. For each sample decide: **use for phylogenetics (Day 4)**, **review / re-sequence**, or **discard**.
   Justify with the metrics: % mapped, mean depth, % ≥ 10x, % N, longest N run, negative control.
3. Fill in `exercises/answer_sheet.tsv` and share your decisions with the group.
4. Discussion:
   - Which sample would you re-sequence, and what would you change?
   - What do you report about the negative control?
   - Which thresholds would you set for your own laboratory?
