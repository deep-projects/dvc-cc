# Sorry
This tutorial is in work!
![IN WORK](work-2062096_640.jpg)


# DVC-CC-Settings

This site is an extension of the [main tutorial](Get_Started.md). Make sure you read it before you read this site.

## Number of GPUs

Please enter the number of GPUs that you want on the cluster. Hint: In the most Deep Learning scripts, you want to 
use 1 GPU in the docke container.

## RAM in GB
Please enter the RAM that you want on the cluster.

## Docker Image
Please enter the Docker Image in which your script get executed at the cluster. You can choose from the following:

- "tf2", if you want to work with TensorFlow 2.0.
- "tf1", if you want to work with TensorFlow 1.4.
- "torch", if you want to work with PyTorch 1.2.
- "large", if you want to work with PyTorch 1.2 or/and TensorFlow 2.0.
- "basic", if you want install it by yourself via the Requirements.txt.

You can also enter a URL to your own Docker Image.

## Batch concurrency limit
The batch concurrency limit describes how many jobs you can start in parallel.

You can lower the number to 1, if you do not want the jobs from one experiment runs in parallel.

## Engine
The name of the engine you want to use. This describes the cluster that you want to use.
At the HTW we have the engines "dt", "cc" and "cctest".


## DVC server
All large files created by your script and defined as output files by DVC are stored on the DVC server.
At the HTW we have the storage server "dt1" and "avocado01".

## DVC folder
Here you can enter the folder where you want to store the DVC files on the DVC Storage Server.

## Username
The username with that you can access the DVC storage server "avocado01.f4.htw-berlin.de" or "dt1.f4.htw-berlin
.de".