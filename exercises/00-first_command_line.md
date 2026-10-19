---
title: "Command line basics"
subtitle: "Bridge talk — module 1"
---


All the tools in this course (FastQC, bwa, samtools…) are run from the **terminal**, not by clicking.
This section gives you the minimum you need. Type the examples yourself: you learn by doing.

::: {.callout-note}
## Which terminal?
- **Linux / macOS**: open the *Terminal* application.
- **Windows**: use **WSL** (Windows Subsystem for Linux) or Git Bash. Your Windows disk `C:` is then at `/mnt/c/`.
:::

### Reading a command

```bash
ls -l -h /home/awa/data
```

| Part | Name | Role |
|---|---|---|
| `ls` | command | the program to run |
| `-l`, `-h` | options (flags) | change the behaviour; can be combined: `-lh` |
| `/home/awa/data` | argument | what the command works on (file, folder…) |

- The **prompt** (e.g. `awa@pc:~$`) means the terminal is waiting for you. Do not type the `$`.
- Linux is **case-sensitive**: `Sample.fastq` and `sample.fastq` are two different files.
- Lines starting with `#` are comments, ignored by the shell.
- **Tab** auto-completes names (use it all the time, it avoids typos). **↑** brings back the previous command. **Ctrl+C** stops a running command.

### Paths: where are my files?

A **path** is the address of a file or folder. Everything depends on understanding paths.

```
/                          ← root of the whole system
├── home/
│   └── awa/               ← home directory of user "awa" (shortcut: ~)
│       └── project/
│           ├── data/
│           │   ├── sample1_R1.fastq.gz
│           │   └── sample1_R2.fastq.gz
│           ├── ref/
│           │   └── reference.fasta
│           └── results/
│               └── trimmed/
```

| Symbol | Meaning | Example |
|---|---|---|
| `/` | root of the system (and the separator between folders) | `/home/awa` |
| `~` | your home directory | `~/project` = `/home/awa/project` |
| `.` | the current directory | `./script.sh` |
| `..` | the parent directory (one level up) | `cd ..` |
| `-` | the previous directory (with `cd`) | `cd -` |

**Absolute path**: starts with `/` (or `~`). It works from anywhere.

```bash
ls /home/awa/project/data
```

**Relative path**: does *not* start with `/`. It starts from where you are now (the *current directory*).

```bash
# I am in /home/awa/project
ls data                  # = /home/awa/project/data
ls ref/reference.fasta   # = /home/awa/project/ref/reference.fasta

# I am in /home/awa/project/results/trimmed
ls ../..                 # = /home/awa/project   (two levels up)
ls ../../data            # = /home/awa/project/data
```

::: {.callout-tip}
## Rule of thumb
1. "No such file or directory" is almost always a **path problem**: run `pwd` and `ls` to check where you are.
2. Inside scripts and pipelines, prefer **relative paths from the project root** so the project can be moved to another computer.
3. **Avoid spaces** and accents in file names: use `sample_1.fastq`, not `my sample 1.fastq`. If a name contains spaces, put it in quotes: `ls "my folder"`.
:::

### Moving around

**`pwd`** (print working directory): where am I?

```bash
pwd
# /home/awa
```

**`ls`**: list the content of a folder.

```bash
ls                 # current folder
ls data            # a given folder
ls -l              # long format: permissions, owner, size, date
ls -lh             # sizes readable (K, M, G)
ls -a              # also show hidden files (names starting with .)
ls -lht            # sorted by time, newest first
ls data/*.fastq.gz # only the matching files (see wildcards below)
```

**`cd`** (change directory): go to another folder.

```bash
cd project             # relative: go into "project"
cd /home/awa/project   # absolute: works from anywhere
cd ..                  # one level up
cd ../..               # two levels up
cd ~                   # home (same as just: cd)
cd -                   # back to the previous folder
```

### Creating files and folders

**`mkdir`**: create a folder.

```bash
mkdir project
mkdir -p project/results/trimmed   # -p creates all missing parent folders
mkdir -p project/{data,ref,results,logs}   # several folders at once
```

**`touch`**: create an empty file (or update its date).

```bash
touch notes.txt
```

**`nano`**: a simple text editor in the terminal.

```bash
nano notes.txt      # type your text, Ctrl+O then Enter = save, Ctrl+X = quit
```

### Copying, moving, renaming, deleting

**`cp`** (copy):

```bash
cp ref/reference.fasta ref/backup.fasta     # copy a file
cp data/*.fastq.gz /home/awa/backup/        # copy many files into a folder
cp -r data data_copy                        # -r = recursive, needed for folders
```

**`mv`** (move **and** rename):

```bash
mv notes.txt docs/              # move into the folder docs
mv notes.txt notes_v2.txt       # rename
mv sample1.fq data/sample1.fq   # move + keep the name
```

**`rm`** (remove):

```bash
rm notes.txt          # delete a file
rm -i notes.txt       # ask for confirmation first (safer)
rm -r old_folder      # delete a folder and everything inside
rmdir empty_folder    # delete a folder only if it is empty
```

::: {.callout-warning}
## There is no recycle bin
`rm` is **permanent**. Never run `rm -rf` on a path you have not checked with `ls` first.
Be especially careful with `*`: `rm *.fastq` deletes all your reads, so test with `ls *.fastq` first.
:::

### Looking inside files

```bash
cat notes.txt                  # print the whole file (small files only!)
head sample.fastq              # first 10 lines
head -n 4 sample.fastq         # first 4 lines = one FASTQ read
tail -n 20 logfile.txt         # last 20 lines
tail -f logfile.txt            # follow a file as it grows (Ctrl+C to stop)
less reference.fasta           # scroll: space = next page, q = quit, /word = search
wc -l notes.txt                # count lines (-w words, -c bytes)
file sample.fastq.gz           # what type of file is it?
```

::: {.callout-tip}
Never `cat` a FASTQ or BAM file: it can contain millions of lines. Use `head` or `less`.
:::

### Wildcards: select many files at once

| Pattern | Matches | Example |
|---|---|---|
| `*` | any number of characters | `ls *.fastq.gz` |
| `?` | exactly one character | `ls sample?_R1.fastq.gz` (sample1, sample2…) |
| `[12]` | one of the listed characters | `ls sample[12]_R1.fastq.gz` |
| `{a,b}` | list of alternatives | `ls sample1_R{1,2}.fastq.gz` |

```bash
ls data/*_R1.fastq.gz      # all forward reads
ls data/sample1_R{1,2}.fastq.gz
```

### Searching and manipulating text

**`grep`**: find lines containing a pattern.

```bash
grep ">" reference.fasta            # lines with ">" = sequence names
grep -c ">" reference.fasta         # count them
grep -i "error" logfile.txt         # ignore upper/lower case
grep -v "#" variants.vcf            # lines that do NOT contain "#" (remove VCF header)
grep -n "ERROR" logfile.txt         # show line numbers
```

**`cut`, `sort`, `uniq`**: work on columns and tables.

```bash
cut -f1 table.tsv                   # first column of a tab-separated file
cut -d"," -f1,3 table.csv           # columns 1 and 3 of a CSV (-d = separator)
sort names.txt                      # alphabetical order
sort -n numbers.txt                 # numeric order
sort names.txt | uniq               # remove duplicates (input must be sorted)
sort names.txt | uniq -c            # count each distinct value
```

### Pipes and redirections

The **pipe** `|` sends the output of one command to the next.
`>` writes the output to a file (replaces it), `>>` appends to a file.

```bash
ls data | wc -l                         # how many files in data?
grep -v "#" variants.vcf | wc -l        # how many variants?
ls data > file_list.txt                 # save the list in a file
echo "run 1 done" >> logfile.txt        # add a line at the end
command 2> errors.txt                   # save error messages only
command > out.txt 2>&1                  # save output + errors together
```

### Compressed files

Sequencing files are usually compressed (`.gz`) to save space.

```bash
gzip notes.txt                  # compress -> notes.txt.gz
gunzip notes.txt.gz             # decompress
zcat sample.fastq.gz | head -n 8        # read a .gz without decompressing
zcat sample_R1.fastq.gz | wc -l         # number of lines...
echo $(( $(zcat sample_R1.fastq.gz | wc -l) / 4 ))   # ...divided by 4 = number of reads

tar -czvf archive.tar.gz folder/   # create an archive (c=create, z=gzip, v=verbose, f=file)
tar -xzvf archive.tar.gz           # extract it (x=extract)
```

### Finding files and checking space

```bash
find . -name "*.fastq.gz"           # search from the current folder
find /home/awa/project -name "*.bam" -size +1G   # BAM files bigger than 1 GB
du -sh data                         # total size of a folder
du -sh data/*                       # size of each item inside
df -h                               # free space on the disks
```

### Getting help

```bash
fastqc --help          # most bioinformatics tools explain themselves
man ls                 # manual of a Linux command (q to quit)
which samtools         # where is this program installed? (nothing = not installed)
history | tail         # your last commands
```

### Permissions and running scripts

`ls -l` shows permissions such as `-rwxr-xr--` (read, write, execute for owner, group, others).

```bash
chmod +x run_pipeline.sh      # make a script executable
./run_pipeline.sh             # run it (./ = "in the current folder")
bash run_pipeline.sh          # or run it with bash, no chmod needed
```

### Variables and loops (to process many samples)

```bash
# Variables: no spaces around =, use $ to read the value
SAMPLE=sample1
echo $SAMPLE
echo "data/${SAMPLE}_R1.fastq.gz"

# Loop: do the same thing for each file
for f in data/*_R1.fastq.gz
do
  echo "Counting reads in $f"
  echo $(( $(zcat $f | wc -l) / 4 ))
done
```

### Downloading

```bash
wget https://example.org/reference.fasta      # download a file
curl -O https://example.org/reference.fasta   # same with curl
```

### Cheat sheet

| I want to… | Command |
|---|---|
| know where I am | `pwd` |
| list files | `ls -lh` |
| go to a folder | `cd path` |
| go up one level | `cd ..` |
| create folders | `mkdir -p a/b/c` |
| copy / move / delete | `cp`, `mv`, `rm` |
| read the start / end of a file | `head`, `tail` |
| read a compressed file | `zcat file.gz \| head` |
| count lines | `wc -l` |
| search text | `grep` |
| chain commands | `\|` |
| save output to a file | `>` or `>>` |
| get help | `tool --help`, `man tool` |

### Common mistakes

- **`No such file or directory`**: wrong path or typo. Check with `pwd`, `ls`, and Tab completion.
- **`Permission denied`**: the file is not executable (`chmod +x`) or you do not own the folder.
- **`command not found`**: the program is not installed or not in your `PATH` (check with `which`).
- **Spaces in names**: they split the name into two arguments. Rename the file or use quotes.
- **Overwriting by accident**: `>` and `mv`/`cp` replace existing files without asking. Use `cp -i`, `mv -i`.
- **Working in the wrong folder**: start each session with `pwd`.

### Practice

Do this in order and check each result with `ls`:

```bash
cd ~
mkdir -p course/{data,ref,results/trimmed,logs}
cd course
touch data/sample1_R1.fastq data/sample1_R2.fastq
ls -R                                   # show the whole tree
cp data/sample1_R1.fastq results/trimmed/
mv results/trimmed/sample1_R1.fastq results/trimmed/sample1_R1_trimmed.fastq
cd results/trimmed
pwd                                     # where am I?
cd ../../data                           # relative path: two up, then data
ls > ../logs/files.txt
cat ../logs/files.txt
```

To go further, do [Exercise 0: command line basics](../exercises/00_second_command_line.md).