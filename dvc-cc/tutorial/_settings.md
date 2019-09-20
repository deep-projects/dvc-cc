# DVC-CC-Settings

This site is an extension of the [main tutorial](Get_Started.md). Make sure you read it before you read this site.

At this site, you find a description of the settings that you need to set.

## Number of GPUs

The number of GPUs that you need to run your script on your cluster. In the most Deep Learning scripts, you want to 
use `1` GPU in the docker container.

## RAM in GB
The **R**andom-**A**ccess **M**emory in GB that you need in the docker container.

## Docker Image
The docker image that you want to use in the docker container. You can choose from the following:

- `tf2`, if you want to work with TensorFlow 2.0.
- `tf1`, if you want to work with TensorFlow 1.4.
- `torch`, if you want to work with PyTorch 1.2.
- `large`, if you want to work with PyTorch 1.2 or/and TensorFlow 2.0.
- `basic`, if you want install it by yourself via the `Requirements.txt`.

You can also enter a URL to your own Docker Image.

If a software is not installed already in this docker image you can use the `Requirements.txt` file that is located
in the main git directory.

## Batch concurrency limit
The batch concurrency limit describes how many jobs you can start in parallel by calling once `dvc-cc run`.

In praxis, you rarely need a low number here. For example, if an SSHFS file can only read by one process, then you 
can set this value to `1`. This number deemed for each `dvc-cc run` separate.


## Engine
The name of the engine you want to use. This describes the cluster that you want to use.
At the HTW-Berlin we have the engines "dt", "cc" and "cctest".


## DVC server
All large files created by your script and defined as output files by DVC are stored on the DVC server.
At the HTW-Berlin we have the storage server "dt1" and "avocado01".

## DVC folder
Here you can enter the folder where you want to store the DVC files on the DVC Storage Server.

## Username
The username with that you can access the DVC storage server "avocado01.f4.htw-berlin.de" or "dt1.f4.htw-berlin
.de".