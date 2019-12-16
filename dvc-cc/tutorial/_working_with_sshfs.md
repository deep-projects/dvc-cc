# DVC-CC: Using of SSHFS

This site is an extension of the [main tutorial](Get_Started.md). Make sure you read it before you read this site.

To work with large datasets, you can use SSHFS. First, you need the URL for your dataset. Then you can run the following
 in the git-main-directory:

```
mkdir data
sshfs URL_TO_YOUR_DATASET data
```

You have right now a data folder that includes your data. You can read from this data folder as it would be located 
on your hard disk. `dvc-cc run` detect that the data folder uses SSHFS and use SSHFS in the docker container.

To unmount the data folder use the following command:

```
fusermount -u data
```

You need to add the "data" folder to your ".gitignore" to make sure that the files get not pushed to git.