# fileutils.py
Fileutils contains some functions that I found helpful when dealing with files.
In particular this library is being developed to remedy several annoyances I face
with existing python libraries responsible for copying files.

A quick search for file copy methods within Python will lead to several mentions
of the shutils library and in particular the methods shutils.copy2() as well as
shutils.copytree(). There are some issues with each of these that I found annoying
or difficult to work with:
    
### shutils.copy2(src, dst):
on it's own, copy2 is great. It lets you copy a file, src, to a destination,
dst. Simple right? Well it turns out there are some rather cryptic error
messages by design that result from, in my opinion, failing to fully do
its job. Take for example the following structure of src:

    src:
        SubdirA/
            file1.txt
            file2.c
            file3.py
        SubdirB/
            file4.cpp
            file5.md
        README.md
        file6.c
        file7.rtf

As a short breakdown, src is a directory containing several subdirectories.
Now copy2 not only does not allow src to be a directory, but also runs into
an issue where, while dst can be a directory, it must exist at ALL levels.

Let's say I wanted to copy src/SubdirA/file1.txt to dst/SubdirA/file1.txt.
I would require several steps for each copy of this type:
- Ensure dst EXISTS
  Simple and easy, just annoying:

    ```python
    if not os.path.isdir(dst):
        os.mkdir(dst)
    ```
- Ensure every single subdir you intend to copy exists in dst
  Depending on how many you intend to copy, and how exact this
  should mirror src, this gets _much_ more annoying:

    ```python
    unique_src = set()
    unique_dst = set()

    # Get the unique subdirs in src
    for dirpath, subdirs, files in os.walk(src):
        if subdirs:
            for subdir in subdirs:
                full_subdir_path = os.path.join(dirpath, subdir)
                rela_subdir_path = full_subdir_path.replace(src,'')
                if rela_subdir_path.startwith('/'):
                    rela_subdir_path = rela_subdir_path.lstrip('/')
                unique_src.add(rela_subdir_path)

    # Do the same thing as above for dst (replace src above with dst)
    # such that now unique_dst AND unique_src are populated.
    
    # With both populated, you now need to find out if dst is missing
    # any of the subdirs that are in A and intended to be copied:
    missing = unique_src - unique_dst

    # Finally, you have to iterate over the missing subdirs, and their
    # relative paths, creating each within dst.
    for subdir in missing:
        full_path = os.path.join(dst, subdir)
        if not os.path.isdir(full_path):
            os.mkdir(full_path)

    # NOW you can begin the code to copy
    ```

I remedied this problem by creating a `copy_dir` function that does
these steps automatically to prevent errors and frustration.

### copytree:
The annoying part about copytree is that the destination directory
CANNOT exist. If you wanted to copy every file in src to dst, keeping
the directory tree in tact. You would need to delete dst if it exists,
potentially losing extra files you care about.

My goal is to provide a method that can automatically copy the tree, keeping
the structure, without the annoyance and issues of needing a completely new
directory.
