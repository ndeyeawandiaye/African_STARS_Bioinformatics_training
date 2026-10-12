# Instructor answers — modules 2–5 (publish AFTER the session)

True lineages: `solutions/outbreak_truth.tsv`. Lineage definitions: `data/outbreak/lineage_definitions.tsv`.

## Dataset design

| Lineage | Genomes | Region / period | Role |
|---|---|---|---|
| TV.1 | 3 | Regions B, D, Jan–Feb | background, root-like |
| TV.3 | 5 | Region B, Feb–Mar | separate older lineage, **not** descended from TV.2 |
| TV.2 | 4 (+ S01) | Region A, 1–5 Mar (3); Region C, 12 Mar (1) | early outbreak genotype |
| TV.2.1 | 8 | Region A, 20 Mar–20 Apr (7); Region C, 2 Apr (1) | expansion in A, one case in C |
| TV.2.2 | 7 | Region C, 25 Mar–28 Apr | local expansion in C |
| low quality | OB24 (TV.2.2) | ~23 % N | to exclude (> 10 % N) |

## Expected answers

1. **Region C vs Region A.** The Region C genomes belong to TV.2 / TV.2.2, which descend from the TV.2 genotype first seen in
   Region A (1–5 March, S01 on 2 March). The first TV.2 case in Region C (12 March) precedes the TV.2.2 expansion.
   → *consistent with* an introduction from A to C followed by local transmission. The tree alone cannot prove direction;
   TV.2.1 in C (2 April) suggests a second link or movement between regions.
2. **Region B.** TV.3 is 6 SNPs from the root and does not share the TV.2 SNPs → **not part of the same chain**; older, separate lineage.
3. **Confidence and next steps.** Moderate: very few SNPs (1–3 per branch), small sample. Sequence more cases from C and
   the days between A's first cases and C's, collect travel/contact data, resequence S02/S03 if still needed.

## Teaching points

- Exclude OB24 (and say why) — its masked defining SNP still allows a TV.2.2 call but its tree position is unreliable.
- S01 is nested with TV.2 genomes from Region A; its distance to them is 2–3 SNPs, mostly its private SNPs.
- Dated metadata + tree = hypothesis, not proof. Reward careful certainty wording.
- The plan-B tree is neighbour-joining; an IQ-TREE ML tree should give the same topology for the lineages, with bootstrap support to read.
