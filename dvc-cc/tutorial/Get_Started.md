# Get Started

## 1) Create an empty GIT-Repository
Create an empty [GitHub](https://github.com/) or [GitLab](https://gitlab.com/) repository and change the directory to the empty git repository.

## 2) Download source code
Now we need some source code that does some task, i.e. training a Convolutional Neural Network (CNN). For this tutorial, you can call the following lines to get source code that trains a CNN in TensorFlow:

```bash
mkdir source
wget -O source/train.py https://raw.githubusercontent.com/deep-projects/d
vc-cc/master/dvc-cc/tutorial/train.py
```
The following graphic shows the parameters and the outputs of the script.

<img src="get_started_pipeline.png" alt="drawing" width="800"/>

One of the outputs is a metric file. A metric file is a special type of output that can summaries the result of the script. Typically this is a JSON file that includes the necessary numbers to compare different models. I.e., numbers like best train/validation accuracy, the smallest train/validation loss.

## 3) Init DVC-CC
Before you start to work with DVC-CC, you need to configure DVC-CC for this project. You can do this with:
```bash
dvc-cc init
```
If you have access to the deep.TEACHING cluster you can leave everything to the default value, except the number of GPUs,
set this to 1, and the username with that you can access the storage server dt1.

> **Even more**: On [this site](_settings.md), you can find all the information about the settings of DVC-CC.

## 4) Build the DVC-CC hyperopt-file

<blockquote>**Even more**: <details><summary>Why do we need to define a pipeline?</summary>
<p>

**Without DVC-CC**: We would call the script multiple times with different parameters to get multiple results and compare this
Hyperparameters. I.e.:

- call: "python source/train.py --num-of-kernels 32"
- call: "python source/train.py --num-of-kernels 64"
- ...

These proceeds has multiple problems that need to solve:
1. You need to make sure that the output of your script gets not overwritten
    and make the name memorable.
    - How do you make clear which parameters and input files you used?
    - What if you want to run it multiple times?
    - How do you make clear, how the source code looked as the output files was created?
2. This workflow works if you run your script on one computer and start one job at a time. But if you have access to a cluster
    you would like to run the experiments in parallel.
    
These two problems are the reason why DVC-CC exists. DVC-CC is a wrapper that makes it easy to integrate DVC with CC.
**DVC** can handle all problems that are described at the first point by describing the processing pipeline and saving checksums to
each dependency and output file, to make sure that the pipeline is unchanged. **CC** is infrastructure software that
used the RED file for describing a job that can be sent to a cluster where it gets executed.

You can think DVC-CC as a high-level wrapper to make it easy to write every time a reproducible code by using DVC with GIT
and send jobs over the CC interface to the cluster.

</p>
</details>
</blockquote>

In the next step, we define the processing pipeline that describes what needs to be called. For this, we use the DVC-CC syntax,
which has just minor changes to the DVC syntax. These minor changes make it possible to create hyperparameters.

> **Even more**: You can also use pure DVC syntax. For more information, take a look at [this site](_only_dvc.md).


The pipeline that we want to describes consists of multiple stages. We need to define the stages and with the stages
all dependencies and output files. By defining the dependencies and output files, DVC can manage the pipeline independently.

```bash
dvc-cc hyperopt new -d source/train.py \
                    -o tensorboard \
                    -o model.h5 \
                    -m summary.yml \
                    -f train.dvc \
                    "python source/train.py --num_of_kernels {{nk}} --activation_function {{af}}"
```

The last line is the pure command (any command that runs in the bash) that we would also use without DVC-CC, but instead of writing hard-coded values for the
parameters we use variable names in curly brackets, i.e., `{{nk}}`. If we run this command, it will ask use which datatype
this parameter is and create a file in the folder ./dvc/.hyperopt that has all information given by this command.

![You need to set the datatype for the variables nk => int and af => one_of, with the possible value: tanh and relu.](hyperopt_command.png)

The DVC-CC command runs in the background `dvc run --no-exec ...` and the command from above. That means that all parameters
are defined in the DVC documentation of [`dvc run`](https://dvc.org/doc/commands-reference/run). But for an overview, you need
to know that -f is the filename that is used for the new file in the folder ./dvc/.hyperopt. The parameters
-d (dependency), -o (output) and -m (metric) describes the pipeline and if one of them is changed or missing DVC knows that
this stage needs to reproduce. For an overview, take a look in the following table:


| name | <sup>saved in git</sup> | <sup>saved in dvc cache</sup> | <sup>save the checksum</sup> | <sup>description</sup>                                                                                       |
|:----:|:------------:|:------------------:|:-----------------:|---------------------------------------------------------------------------------------------------|
|  -d  |     <sup>False</sup>    |        <sup>False</sup>       |        <sup>True</sup>       | <sup>You use this to define dependencies (inputs) or everything from what this stage depends on.</sup>       |
|  -o  |     <sup>False</sup>    |        <sup>True</sup>        |        <sup>True</sup>       | <sup>Large output files or folders</sup>                                                                                |
|  -O  |     <sup>True</sup>     |        <sup>False</sup>       |        <sup>True</sup>       | <sup>Small output files or folders </sup>                                                                               |
|  -m  |     <sup>True</sup>     |        <sup>True</sup>        |        <sup>True</sup>       | <sup>Metrics are output files but have a special feature that you can use with `dvc metrics show`</sup>  |
|  -M  |     <sup>True</sup>     |        <sup>False</sup>       |        <sup>True</sup>       | <sup>Metrics see above. Find more information about metrics [here](https://dvc.org/doc/commands-reference/metrics-show). </sup>  

> **Even more**: Can you set all the parameters? For help and a solution go to [this site](_set_all_parameters.md).

> **Even more**: Here we only defined one stage. Of course, you could define complex pipelines with this technique. 
See [this site](_complex_pipeline.md) for more information.

## 5) Run the script in the cluster
We have right now our pipeline defined and can run our script in the cloud. For this we need to push everything to git:
```bash
git add -A
git commit -m "build the pipeline for the first test run with DVC-CC"
git push
```
and just run the command:
```bash
dvc-cc run the_name_of_this_experiment
```
This command will ask you how to set your hyperparameters. You can use one value (i.e. `32`) or use multiple values with
a comma-separated (i.e. `32,64`) to run multiple experiments. You can also use grid-search or random-search for finding
the best parameters. Take a look [here] _run_hyper_optimization.md), if you want to find out more about this hyper optimization.

> **Even more**: The DVC-CC run command has a lot of parameters (i.e. to run the same experiments multiple times). If you
want to find out more about this use the command `dvc-cc run --help`.

`dvc-cc run` will take care of your pipeline and creates new branches that start with **cc_**. These new branches are
input branches that will be used to execute your code. This means that you can work continuously on your branch and do
not need to wait that the job has finished. CC will take care to scale your experiment and make sure that the right
hardware is used to run the script in a docker container. After the experiment finished, it will be automatically
created a resulting branch that starts with **rcc_**.

## 6) Check jobs
But before we take a look at the result branch, we will check the job that we started with `dvc-cc status` we get the
last job that was launched, with `dvc-cc status -p 1` we get all jobs that have the ID 1, or
with `dvc-cc status -p 1 -d` we get a detailed view of the jobs with the ID 1.

Use the command `dvc-cc status --help` to get all parameters that you can use with this command and `dvc-cc cancel --all`
to cancel all not finished jobs.

## 7) The result branch
If the job succeeded, a resulting branch is created. Now we take a look at a resulting branch. All result branches start
with **rcc_JobID_TheNameOfThisExperiment** and were created remotely. So we need first do a `git pull` to get the new
branches. And can now check out to one of the result branches with ´git checkout rcc_...´, with ... the name of the
branch. On Linux you can use tab for auto-complete.

Now we need to pull from dvc with `dvc pull` all large files that are not stored in git. Now all output files are
available at this branch and you get all the information that you need to rerun the experiment by an external
persona on the readme.md of this branch.

## 8) Get output files from experiments
To get all output TensorBoard folders (`-f tensorboard`) that was created by the script from the
first experiment (`-p 1`) and rename the files to have the branch name in it (`-r`) you can use the
following command:
```
dvc-cc output-to-tmp --allow-dir -f tensorboard -d -p 1 -r
```

## 9) And more informations
That's it. Now, you should have a feeling about how you can work with DVC-CC. There are a lot of more functions in it.
The `--help` option should be your best friend. If you have any questions or found a bug, you can report it
in the [dvc-cc github issue list](https://github.com/deep-projects/dvc-cc/issues).

- If you would like to work with **jupyter notebook** take a look at [this site](_working_with_jupyter_notebook.md).
- DVC-CC creates a lot of branches. That means that `git branch` is bombarded with the **cc_** and **rcc_** branches
    you can use `dvc-cc git branch` to show only your working branches.
- You can have live access to the output that your models create. Take a look at [this site](_live_output.md).
- You can connect to some data per SSHFS on your branch. The cluster will use the same SSHFS connection, but currently,
    this works only if the `data` folder was used. [Here](_working_with_sshfs.md) you can read more about it.

## Acknowledgements
The DVC-CC software is developed at CBMI (HTW Berlin - University of Applied Sciences). The work is supported by the
German Federal Ministry of Education and Research (project deep.TEACHING, grant number 01IS17056 and project
deep.HEALTH, grant number 13FH770IX6).