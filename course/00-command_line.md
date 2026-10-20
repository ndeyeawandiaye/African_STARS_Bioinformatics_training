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

## The prompt: your terminal is waiting for you

When you open the terminal, you see a line ending with a blinking cursor. This line is the **prompt**. It tells you who you are, on which computer, and where you are.

```
awa@pc-awa:~$
```

| Part | Name | Meaning |
|---|---|---|
| `awa` | user name | **who you are** on this computer |
| `@` | separator | "at" |
| `pc-awa` | host name | the **name of the computer** |
| `:` | separator | |
| `~` | current folder | **where you are** (`~` = your home folder, see below) |
| `$` | prompt symbol | "I am ready, type a command" |

- **Do not type the prompt** (`awa@pc-awa:~$`) when you copy a command. In this course, commands are written without it.
- Your prompt will look a little different from the one above (other name, colours, `%` instead of `$` on macOS). The idea is the same.
- If the symbol is `#` instead of `$`, you are the administrator (*root*). Be extra careful: you can break the system.
- A command runs when you press **Enter**. While a command is running, the prompt disappears. It comes back when the command is finished.

### Find out who and where you are

Type these three commands, one at a time, and press Enter after each:

```bash
whoami       # your user name
hostname     # the name of this computer
pwd          # the folder you are in right now (print working directory)
```

Example of what you may see:

```
awa
pc-awa
/home/awa
```

::: {.callout-important}
## Write down your user name
Your user name is the result of `whoami`. In this course, every time you see **`USERNAME`**, replace it with **your** user name.

Example: if `whoami` shows `awa`, then `/home/USERNAME/course` becomes `/home/awa/course`.

You will rarely need to type it, because `~` is a shortcut for `/home/USERNAME` (your *home folder*).

- **Windows (WSL)**: your user name is the Linux name you chose when installing WSL, not your Windows name.
- **macOS**: the home folder is `/Users/USERNAME` instead of `/home/USERNAME`.
:::

## Reading a command

Run this command (replace `USERNAME`):

```bash
ls -l -h /home/USERNAME
```

It lists what is in your home folder. Every command has the same structure:

| Part | Name | Role |
|---|---|---|
| `ls` | command | the program to run ("list") |
| `-l`, `-h` | options (flags) | change the behaviour; can be combined: `-lh` |
| `/home/USERNAME` | argument | what the command works on (file, folder…) |

Example of output (yours will be different, and may even be empty if the folder is new):

```
total 12K
drwxr-xr-x 2 awa awa 4.0K Oct 19 10:02 Documents
drwxr-xr-x 2 awa awa 4.0K Oct 19 10:02 Downloads
-rw-r--r-- 1 awa awa  220 Oct 19 10:02 notes.txt
```

A line starting with `d` is a **folder** (directory), a line starting with `-` is a **file**.

Four rules to remember:

- Linux is **case-sensitive**: `Sample.fastq` and `sample.fastq` are two different files.
- Lines starting with `#` are comments, ignored by the shell. You can type them or not.
- **Tab** auto-completes names (use it all the time, it avoids typos). **↑** brings back the previous command.
- **Ctrl+C** stops a running command. If the terminal seems frozen, try it.

## The file system: a tree of folders

Files are organised in folders, which are inside other folders, and so on. This forms a **tree**. At the top of the tree there is the **root**, written `/`.

Here is a simplified tree that exists on every Linux computer (and WSL):

```
/                          ← root of the whole system
├── home/                  ← the folders of all users
│   └── USERNAME/          ← YOUR home folder (shortcut: ~)
│       └── (your own files and folders)
├── tmp/                   ← temporary files
├── usr/
│   ├── bin/               ← installed programs
│   └── share/
└── etc/                   ← system settings
```

What you have inside your home folder depends on your computer. Later, we will build our own folders there for this course.

## Moving around: `pwd`, `ls`, `cd`

We will practise on folders that exist on every computer.

**`pwd`**: where am I?

```bash
pwd
```

**`ls`**: what is here?

```bash
ls                 # content of the current folder
ls /               # content of the root: you should see home, tmp, usr, etc...
ls /home           # content of /home: you should see your user name
ls -l              # long format: permissions, owner, size, date
ls -lh             # sizes in readable units (K, M, G)
ls -a              # also show hidden files (names starting with .)
ls -lt             # sorted by time, newest first
```

**`cd`** (change directory): go to another folder.

```bash
cd /tmp            # go to /tmp
pwd                # check: /tmp
cd /usr/share      # go to /usr/share
pwd                # check: /usr/share
cd ..              # one level up (back to /usr)
pwd                # check: /usr
cd -               # back to the previous folder (/usr/share)
cd ~               # go to your home folder
cd                 # same thing: no argument = home
```

::: {.callout-tip}
## Watch your prompt
The prompt shows the current folder. Run `cd /tmp` and look: `awa@pc-awa:~$` becomes `awa@pc-awa:/tmp$`. After `cd ~`, it goes back to `~`.
:::

## Paths: where are my files?

A **path** is the address of a file or folder. Almost every error you will see at the beginning comes from a wrong path.

| Symbol | Meaning | Example |
|---|---|---|
| `/` | root of the system (and the separator between folders) | `/home/USERNAME` |
| `~` | your home folder | `~/course` = `/home/USERNAME/course` |
| `.` | the current folder | `./script.sh` |
| `..` | the parent folder (one level up) | `cd ..` |
| `-` | the previous folder (with `cd`) | `cd -` |

**Absolute path**: starts with `/` (or `~`). It gives the full address from the root and works **from anywhere**.

```bash
ls /usr/share
ls /home/USERNAME
ls ~
```

**Relative path**: does *not* start with `/`. It starts from **where you are now**.

```bash
cd /usr             # I am in /usr
ls share            # relative: = /usr/share
ls /usr/share       # absolute: the same result

cd share            # now I am in /usr/share
pwd
ls ..               # content of the parent folder = /usr
ls ../..            # two levels up = the root /
cd ../..            # go to the root
pwd                 # /
```

The same command can give different results depending on where you are, if you use a relative path. With an absolute path it never changes.

::: {.callout-tip}
## Rule of thumb
1. "No such file or directory" is almost always a **path problem**: run `pwd` and `ls` to check where you are.
2. Inside scripts and pipelines, prefer **relative paths from the project folder**, so the project can be moved to another computer.
3. **Avoid spaces** and accents in file names: use `sample_1.fastq`, not `my sample 1.fastq`. If a name contains spaces, put it in quotes: `ls "my folder"`.
:::

## Creating folders and files: your practice project

Now we build our own folders. We create a project called `course` in your home folder.

**`mkdir`** (make directory): create a folder.

```bash
cd ~                                    # start from your home folder
mkdir course                            # create the folder "course"
mkdir -p course/results/trimmed         # -p creates all missing parent folders
mkdir -p course/{data,ref,logs}         # several folders at once
ls course                               # you should see: data logs ref results
cd course                               # go inside
pwd                                     # /home/USERNAME/course
```

You have built this tree:

```
/home/USERNAME/
└── course/
    ├── data/
    ├── ref/
    ├── logs/
    └── results/
        └── trimmed/
```

Check it with `ls -R` (R = recursive: shows the content of all subfolders):

```bash
ls -R
```

::: {.callout-important}
## From now on, work in `~/course`
All the following examples use **relative paths from `~/course`**. If you are lost, type:

```bash
cd ~/course
pwd
```
:::

**`touch`**: create an empty file (or update its date).

```bash
touch logs/notes.txt
ls logs
```

**`nano`**: a simple text editor in the terminal.

```bash
nano logs/notes.txt     # type some text, Ctrl+O then Enter = save, Ctrl+X = quit
```

### Create small practice files

Real sequencing files are huge. We create tiny fake ones to practise. You may copy-paste the two blocks below.
The command `cat > file << 'EOF'` writes everything that follows, up to the line `EOF`, into the file.

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

Check:

```bash
ls -R
```

You should now see `sample1_R1.fastq` in `data`, `reference.fasta` in `ref`, and `notes.txt` in `logs`.

## Copying, moving, renaming, deleting

**`cp`** (copy): `cp source destination`

```bash
cp ref/reference.fasta ref/backup.fasta          # copy a file (new name)
cp data/sample1_R1.fastq data/sample1_R2.fastq   # another copy in the same folder
cp data/sample1_R1.fastq results/trimmed/        # copy into another folder (keeps the name)
cp -r data data_copy                             # -r = recursive, needed to copy a folder
ls -R
```

**`mv`** (move **and** rename): `mv source destination`

```bash
mv results/trimmed/sample1_R1.fastq results/trimmed/sample1_R1_trimmed.fastq   # rename
mv ref/backup.fasta logs/                                                      # move into logs/
ls -R
```

**`rm`** (remove):

```bash
rm logs/backup.fasta       # delete a file
rm -i data_copy/sample1_R2.fastq   # ask for confirmation first (answer y or n)
rm -r data_copy            # delete a folder and everything inside
mkdir empty_test
rmdir empty_test           # delete a folder only if it is empty
```

::: {.callout-warning}
## There is no recycle bin
`rm` is **permanent**. Never run `rm -r` on a path you have not checked with `ls` first.
Be especially careful with `*` (see wildcards below): `rm *.fastq` deletes all matching files, so test with `ls *.fastq` first.
:::

## Looking inside files

```bash
cat data/sample1_R1.fastq              # print the whole file (small files only!)
head data/sample1_R1.fastq             # first 10 lines
head -n 4 data/sample1_R1.fastq        # first 4 lines = one FASTQ read
tail -n 4 data/sample1_R1.fastq        # last 4 lines = the last read
less ref/reference.fasta               # scroll: space = next page, q = quit, /word = search
wc -l data/sample1_R1.fastq            # count lines (-w words, -c bytes)
file data/sample1_R1.fastq             # what type of file is it?
```

::: {.callout-tip}
Never `cat` a real FASTQ or BAM file: it can contain millions of lines. Use `head` or `less`.
:::

## Wildcards: select many files at once

First create more files to select:

```bash
cp data/sample1_R1.fastq data/sample2_R1.fastq
cp data/sample1_R2.fastq data/sample2_R2.fastq
ls data
```

| Pattern | Matches | Example |
|---|---|---|
| `*` | any number of characters | `ls data/*.fastq` |
| `?` | exactly one character | `ls data/sample?_R1.fastq` (sample1, sample2…) |
| `[12]` | one of the listed characters | `ls data/sample[12]_R1.fastq` |
| `{a,b}` | list of alternatives | `ls data/sample1_R{1,2}.fastq` |

```bash
ls data/*_R1.fastq              # all forward reads
ls data/sample1_*               # everything about sample1
ls data/sample1_R{1,2}.fastq    # R1 and R2 of sample1
```

## Searching and manipulating text

**`grep`**: find lines containing a pattern.

```bash
grep ">" ref/reference.fasta           # lines with ">" = sequence names
grep -c ">" ref/reference.fasta        # count them (= number of sequences)
grep -i "SEGMENT" ref/reference.fasta  # ignore upper/lower case
grep -v ">" ref/reference.fasta        # lines that do NOT contain ">" (the sequences only)
grep -n "segment" ref/reference.fasta  # show line numbers
```

**`cut`, `sort`, `uniq`**: work on columns and lists. First create two small files:

```bash
cat > logs/table.csv << 'EOF'
sample,reads,country
sample1,300,Senegal
sample2,120,Mali
sample3,250,Senegal
EOF

cat > logs/names.txt << 'EOF'
sample2
sample1
sample2
sample3
EOF
```

```bash
cut -d"," -f1,3 logs/table.csv      # columns 1 and 3 (-d = separator, -f = fields)
cut -d"," -f2 logs/table.csv        # only column 2
sort logs/names.txt                 # alphabetical order
sort logs/names.txt | uniq          # remove duplicates (input must be sorted)
sort logs/names.txt | uniq -c       # count each distinct value
```

## Pipes and redirections

The **pipe** `|` sends the output of one command to the next.
`>` writes the output to a file (and **replaces** it), `>>` **appends** to a file.

```bash
ls data | wc -l                          # how many files in data?
grep -v ">" ref/reference.fasta | wc -l  # how many sequence lines?
ls data > logs/file_list.txt             # save the list in a file
cat logs/file_list.txt
echo "run 1 done" >> logs/notes.txt      # add a line at the end of notes.txt
cat logs/notes.txt
ls data/does_not_exist 2> logs/errors.txt            # save error messages only
cat logs/errors.txt
ls data data/does_not_exist > logs/all.txt 2>&1      # save output + errors together
```

## Compressed files

Sequencing files are usually compressed (`.gz`) to save space.

```bash
gzip -k data/sample1_R1.fastq              # compress, -k keeps the original -> sample1_R1.fastq.gz
ls -lh data
zcat data/sample1_R1.fastq.gz | head -n 8  # read a .gz without decompressing
zcat data/sample1_R1.fastq.gz | wc -l      # number of lines...
echo $(( $(zcat data/sample1_R1.fastq.gz | wc -l) / 4 ))   # ...divided by 4 = number of reads

gzip data/sample2_R2.fastq                 # without -k, the original disappears
ls data
gunzip data/sample2_R2.fastq.gz            # decompress: back to the original
ls data
```

Archives (several files in one):

```bash
tar -czvf data_backup.tar.gz data/         # create (c=create, z=gzip, v=verbose, f=file name)
mkdir restore
tar -xzvf data_backup.tar.gz -C restore    # extract (x=extract) into the folder "restore"
ls -R restore
rm -r restore data_backup.tar.gz           # clean up
```

## Finding files and checking space

```bash
find . -name "*.fastq"              # search from the current folder (.)
find ~/course -name "*.fasta"       # search from an absolute path
du -sh data                         # total size of a folder
du -sh data/*                       # size of each item inside
df -h                               # free space on the disks
```

## Getting help

```bash
ls --help              # most tools explain themselves (on macOS use: man ls)
man ls                 # manual of a Linux command (q to quit)
which ls               # where is this program installed?
which samtools         # nothing displayed = not installed (yet)
history | tail         # your last commands
```

## Permissions and running scripts

`ls -l` shows permissions such as `-rwxr-xr--` (read, write, execute for the owner, the group, the others).

Create a tiny script:

```bash
echo '#!/bin/bash' > run.sh
echo 'echo "Hello from my first script"' >> run.sh
cat run.sh
./run.sh                 # "Permission denied": the file is not executable yet
ls -l run.sh             # no x in the permissions
chmod +x run.sh          # make it executable
ls -l run.sh             # now there are x
./run.sh                 # works (./ = "the file is in the current folder")
bash run.sh              # or run it with bash, no chmod needed
```

## Variables and loops (to process many samples)

```bash
# Variables: no spaces around =, use $ to read the value
SAMPLE=sample1
echo $SAMPLE
echo "data/${SAMPLE}_R1.fastq"

# Loop: do the same thing for each file
for f in data/*_R1.fastq
do
  echo "Counting reads in $f"
  echo $(( $(wc -l < $f) / 4 ))
done
```

## Downloading

```bash
wget https://example.org/index.html      # download a file
curl -O https://example.org/index.html   # same with curl
ls
rm index.html
```

## Cheat sheet

| I want to… | Command |
|---|---|
| know who I am / where I am | `whoami` / `pwd` |
| list files | `ls -lh` |
| go to a folder | `cd path` |
| go up one level / go home | `cd ..` / `cd ~` |
| create folders | `mkdir -p a/b/c` |
| copy / move / delete | `cp`, `mv`, `rm` |
| read the start / end of a file | `head`, `tail` |
| read a compressed file | `zcat file.gz \| head` |
| count lines | `wc -l` |
| search text | `grep` |
| chain commands | `\|` |
| save output to a file | `>` or `>>` |
| get help | `tool --help`, `man tool` |

## Common mistakes

- **`No such file or directory`**: wrong path or typo. Check with `pwd`, `ls`, and Tab completion.
- **Typing the prompt**: do not copy `awa@pc-awa:~$`, only the command after it.
- **Forgetting to replace `USERNAME`** by your own user name (`whoami`).
- **`Permission denied`**: the file is not executable (`chmod +x`) or you do not own the folder.
- **`command not found`**: typo, or the program is not installed (check with `which`).
- **Spaces in names**: they split the name into two arguments. Rename the file or use quotes.
- **Overwriting by accident**: `>`, `mv` and `cp` replace existing files without asking. Use `cp -i`, `mv -i`.
- **Working in the wrong folder**: start each session with `pwd`.

## Practice

Start from a folder that is **not** your project (`cd /tmp`) and use only absolute paths:

```bash
cd /tmp
ls ~/course                                   # content of the project
head -n 4 ~/course/data/sample1_R1.fastq      # first read
mkdir -p ~/course/results/qc
echo $(( $(wc -l < ~/course/data/sample1_R1.fastq) / 4 )) > ~/course/results/qc/n_reads.txt
cat ~/course/results/qc/n_reads.txt           # 3
cd ~/course                                   # back to the project
pwd
```

To go further, do [Exercise 0: command line basics](../exercises/00-command_line.md).