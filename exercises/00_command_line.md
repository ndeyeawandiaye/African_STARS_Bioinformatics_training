---
title: "Exercise 0 — Command line basics"
subtitle: "Bridge talk — module 1"
---

## Goal

Practise the basic Linux commands and, above all, **paths**, on a small project that looks like the one you will use for the pipelines.

**Time**: about 45 minutes. **Rules**: type every command yourself (no copy-paste for parts A to C), and run `pwd` whenever you are unsure where you are. Solutions are hidden below each part: try first, then check.

## Part A — Where am I?

1. Open a terminal. Which command shows your current folder?
2. List the content of your home folder with sizes in a readable format, including hidden files.
3. Go to the root of the system (`/`), list it, then come back to the previous folder in **one** command.
4. Go to your home folder in two different ways.

::: {.callout-note collapse="true"}
## Solution A

```bash
pwd                # 1. e.g. /home/awa
ls -lah            # 2. -l long, -a hidden files, -h readable sizes
cd /               # 3. go to the root
ls
cd -               #    back to the previous folder
cd ~               # 4. way 1
cd                 #    way 2 (no argument = home)
```
:::

## Part B — Build the project

We create the following tree in your home folder:

```
bridge/
├── data/
├── ref/
├── results/
│   └── trimmed/
└── logs/
```

1. Create it with **one** `mkdir` command.
2. Go into `bridge` and check the tree with `ls -R`.
3. Create an empty file `logs/notes.txt` **without leaving** the `bridge` folder.

::: {.callout-note collapse="true"}
## Solution B

```bash
mkdir -p ~/bridge/{data,ref,results/trimmed,logs}   # 1. -p creates parents, {} makes several folders
cd ~/bridge                                         # 2.
ls -R
touch logs/notes.txt                                # 3. relative path from bridge/
```

Expected `ls -R` output (order may vary):

```
.:
data  logs  ref  results

./data:

./logs:

./ref:

./results:
trimmed

./results/trimmed:
```
:::

## Part C — Create small data files

Real FASTQ files are huge, so we create a tiny fake one. The command `cat > file << 'EOF'` writes everything you type, up to the line `EOF`, into the file.

From `~/bridge`, run:

```bash
cat > data/sample1_R1.fastq << 'EOF'
@read1
ACGTACGTAC
+
IIIIHHHHGG
@read2
GGGGCCCCAA
+
IIIIIIIIII
@read3
TTTTAAAACC
+
HHHHHHHHHH
EOF
```

```bash
cat > ref/reference.fasta << 'EOF'
>segment_L
ACGTACGTACGTACGTACGT
>segment_S
TTTTGGGGCCCCAAAATTTT
EOF
```

Now answer, using commands (not by eye):

1. How many lines does `sample1_R1.fastq` have? How many reads is that (4 lines per read)?
2. Display only the first read (first 4 lines).
3. How many sequences are in `reference.fasta`? Display their names only.
4. Create `sample1_R2.fastq` as a copy of `sample1_R1.fastq`, then check with `ls -lh data`.

::: {.callout-note collapse="true"}
## Solution C

```bash
wc -l data/sample1_R1.fastq              # 1. 12 lines -> 12 / 4 = 3 reads
head -n 4 data/sample1_R1.fastq          # 2.
grep -c ">" ref/reference.fasta          # 3. 2 sequences
grep ">" ref/reference.fasta             #    >segment_L and >segment_S
cp data/sample1_R1.fastq data/sample1_R2.fastq   # 4.
ls -lh data
```
:::

## Part D — Paths (the most important part)

1. Go into `results/trimmed` and run `pwd`.
2. From there, copy `sample1_R1.fastq` from `data` into the current folder using a **relative path** (use `..`).
3. Rename the copy to `sample1_R1_trimmed.fastq`.
4. From the same folder (`results/trimmed`), copy `sample1_R2.fastq` into it using an **absolute path** (use `~`).
5. Without leaving the folder, display the first 4 lines of `../../ref/reference.fasta`.
6. Go back to `~/bridge` in one command, using a **relative** path, then in one command using an **absolute** path.

::: {.callout-note collapse="true"}
## Solution D

```bash
cd results/trimmed                                    # 1.
pwd                                                   #    /home/awa/bridge/results/trimmed
cp ../../data/sample1_R1.fastq .                      # 2. ../../ = two levels up, . = here
mv sample1_R1.fastq sample1_R1_trimmed.fastq          # 3.
cp ~/bridge/data/sample1_R2.fastq .                   # 4. absolute path works from anywhere
head -n 4 ../../ref/reference.fasta                   # 5.
cd ../..                                              # 6. relative
cd ~/bridge                                           #    absolute
```

Why `../..`? `results/trimmed` → `..` is `results` → `../..` is `bridge`.
:::

## Part E — Wildcards

1. Create `sample2_R1.fastq` and `sample2_R2.fastq` as copies of the sample1 files (in `data/`).
2. List only the R1 files of `data/`.
3. List `sample1_R1.fastq` and `sample1_R2.fastq` with **one** pattern using `{ }`.
4. List all the files of `data/` whose name starts with `sample` followed by **exactly one** character, then `_R1`.
5. Before deleting anything: list with `ls` the files you would remove with `rm data/sample2*`, then delete them. Explain why you ran `ls` first.

::: {.callout-note collapse="true"}
## Solution E

```bash
cp data/sample1_R1.fastq data/sample2_R1.fastq        # 1.
cp data/sample1_R2.fastq data/sample2_R2.fastq
ls data/*_R1.fastq                                    # 2.
ls data/sample1_R{1,2}.fastq                          # 3.
ls data/sample?_R1.fastq                              # 4.
ls data/sample2*                                      # 5. check what matches...
rm data/sample2*                                      #    ...then delete
```

`rm` is permanent and the `*` may match more files than expected, so `ls` with the same pattern shows exactly what will be deleted.
:::

## Part F — Pipes and redirections

From `~/bridge`:

1. Save the list of files of `data/` in `logs/files.txt`.
2. Add the line `Exercise 0 - part F done` at the end of `logs/notes.txt` (do not erase the file).
3. Count the files of `data/` with a pipe (no file involved).
4. Count how many lines of `data/sample1_R1.fastq` start with `@` using `grep`, and compare with your answer to C1. Why is the result the same here?
5. Run `ls data/does_not_exist 2> logs/errors.txt` and read `logs/errors.txt`. What did `2>` save?

::: {.callout-note collapse="true"}
## Solution F

```bash
ls data > logs/files.txt                      # 1. > replaces the file
echo "Exercise 0 - part F done" >> logs/notes.txt   # 2. >> appends
ls data | wc -l                               # 3. 3 files (sample1_R1, sample1_R2... plus sample2 if not deleted)
grep -c "^@" data/sample1_R1.fastq            # 4. 3
cat logs/errors.txt                           # 5. the error message
```

4. `^@` means "line starting with `@`". It gives 3 here because each read has one header line. Warning: in real files, a **quality line can also start with `@`** (it is a valid quality character), so counting `@` is not a reliable way to count reads. Use `wc -l` divided by 4, or `seqkit stats`.
5. `2>` saves the **error messages** (stream 2), not the normal output.
:::

## Part G — Compressed files

1. Compress `data/sample1_R1.fastq` **keeping the original** (`gzip -k`).
2. Compare the sizes of the two files with `ls -lh`. (With 3 reads the gain is tiny, but with real data it is large.)
3. Display the first 4 lines of the compressed file **without decompressing** it.
4. Compute the number of reads of the `.gz` file in one command line.
5. Use `file` on both files. What do you see?

::: {.callout-note collapse="true"}
## Solution G

```bash
gzip -k data/sample1_R1.fastq                                # 1. creates sample1_R1.fastq.gz
ls -lh data/sample1_R1.fastq*                                # 2.
zcat data/sample1_R1.fastq.gz | head -n 4                    # 3.
echo $(( $(zcat data/sample1_R1.fastq.gz | wc -l) / 4 ))     # 4. 3
file data/sample1_R1.fastq data/sample1_R1.fastq.gz          # 5. "ASCII text" vs "gzip compressed data"
```

If `-k` is not accepted (very old gzip), use `gzip -c data/sample1_R1.fastq > data/sample1_R1.fastq.gz`.
:::

## Part H — A loop and a variable

1. Write a loop that prints, for each `*_R1.fastq` file of `data/`, its name and its number of reads, in the form `data/sample1_R1.fastq: 3 reads`.
2. Redo the loop but save the output in `logs/read_counts.txt`.
3. Use a variable `SAMPLE=sample1` to display `data/sample1_R1.fastq` and `data/sample1_R2.fastq` with `echo`.

::: {.callout-note collapse="true"}
## Solution H

```bash
for f in data/*_R1.fastq        # 1.
do
  echo "$f: $(( $(wc -l < $f) / 4 )) reads"
done

for f in data/*_R1.fastq        # 2. redirect the whole loop
do
  echo "$f: $(( $(wc -l < $f) / 4 )) reads"
done > logs/read_counts.txt
cat logs/read_counts.txt

SAMPLE=sample1                  # 3. no spaces around =
echo "data/${SAMPLE}_R1.fastq"
echo "data/${SAMPLE}_R2.fastq"
```

`wc -l < $f` (with `<`) prints only the number, without the file name.
:::

## Part I — Find the error

Each command fails. Explain why and fix it. Run them from `~/bridge`.

```bash
cd Data                         # 1
ls /data                        # 2
cat data/sample1_r1.fastq       # 3
mkdir my results                # 4  (check with ls what was created!)
echo "#!/bin/bash" > run.sh
echo "echo Hello" >> run.sh
./run.sh                        # 5
```

::: {.callout-note collapse="true"}
## Solution I

| # | Error | Why | Fix |
|---|---|---|---|
| 1 | `No such file or directory` | Linux is case-sensitive: the folder is `data`, not `Data` | `cd data` |
| 2 | `No such file or directory` | `/data` is an **absolute** path (at the root of the system) | `ls data` (relative) or `ls ~/bridge/data` |
| 3 | `No such file or directory` | `sample1_r1` ≠ `sample1_R1` (case) | `cat data/sample1_R1.fastq` (use Tab!) |
| 4 | No error, but **two** folders `my` and `results` are created (or `results` already exists) | the space separates two arguments | `mkdir my_results` or `mkdir "my results"` (avoid spaces) |
| 5 | `Permission denied` | the file is not executable | `chmod +x run.sh` then `./run.sh`, or `bash run.sh` |

Clean up after question 4: `rmdir my` (only works if empty; do not remove `results`!).
:::

## Part J — Final challenge

Without using `cd` at all, from **any** folder (start with `cd /tmp`):

1. Display the first 4 lines of `~/bridge/data/sample1_R1.fastq`.
2. Create the folder `~/bridge/results/qc`.
3. Write the number of reads of `sample1_R1.fastq` in `~/bridge/results/qc/n_reads.txt`.
4. Display the whole project tree with `ls -R ~/bridge`.

::: {.callout-note collapse="true"}
## Solution J

```bash
cd /tmp
head -n 4 ~/bridge/data/sample1_R1.fastq                                   # 1.
mkdir -p ~/bridge/results/qc                                               # 2.
echo $(( $(wc -l < ~/bridge/data/sample1_R1.fastq) / 4 )) > ~/bridge/results/qc/n_reads.txt   # 3.
cat ~/bridge/results/qc/n_reads.txt                                        #    3
ls -R ~/bridge                                                             # 4.
```

Absolute paths (with `~`) work from anywhere, which is why this works from `/tmp`.
:::

## Clean up (optional)

Check **twice** what you delete:

```bash
ls ~/bridge        # is it really the practice folder?
rm -r ~/bridge
```

## Checklist

You are ready for the next exercise if you can:

- [ ] say where you are (`pwd`) and what is around you (`ls`)
- [ ] explain the difference between an absolute and a relative path
- [ ] use `.`, `..`, `~` and `-`
- [ ] create, copy, move and delete files and folders safely
- [ ] read the start of a big or compressed file (`head`, `zcat`)
- [ ] count lines and reads, and use `grep`
- [ ] chain commands with `|` and save results with `>` and `>>`
- [ ] understand `No such file or directory` and `Permission denied`

**Next:** [FASTQ and quality control](01_fastq_and_qc.md).