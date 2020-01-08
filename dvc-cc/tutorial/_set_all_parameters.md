# DVC-CC: use all parameters

This site is an extension of the [main tutorial](Get_Started.md). Make sure you read it before you read this site.

In the main tutorial, we only set some parameters of the script. At this site, it is clarified how the command could
look to set all parameters. But first let's take a look at the script from the main tutorial:

<img src="get_started_pipeline.png" alt="drawing" width="800"/>

## For refreshing your knowledge

- you can use the regular DVC syntax in the `dvc-cc hyperopt new ...` command.  
- The `-d` flag is used to define a dependency of your script, i.e. the source code of the script.
- The `-o` flag is used to define an output file or output folder of your script
- The `-m` flag is used to define a metric file. This is a special case of an output file that summaries the result of
a script. For example, the best validation accuracy saved in a json-file.
- The `-f` flag is used to define a filename for the DVC-file that gets created by this command.
- The last line of the command is the pure command that we would also use at the command line.
- Between the curly brackets `{{` and `}}` you can define a hyperparameter.

In the main tutorial we used the following command:
```bash
dvc-cc hyperopt new -d source/train.py \
                    -o tensorboard \
                    -o model.h5 \
                    -M summary.yml \
                    -f train.dvc \
                    "python source/train.py --num_of_kernels {{nk}} --activation_function {{af}}"
```

## Update the command
To use all parameters of our script, we update the last line and set all parameters with hyperparameters and give them a
short name:

```bash
dvc-cc hyperopt new -d source/train.py \
                    -o tensorboard \
                    -o model.h5 \
                    -M summary.yml \
                    -f train.dvc \
                    "python source/train.py --seed {{seed}} --num_of_hidden_layers {{nh}} --num_of_kernels {{nk}} --dropout_rate {{dr}} --learning_rate {{lr}} --activation_function {{af}} --batch_size {{bs}} --epochs {{e}} --dataset {{d}}"
```

With the command above, we need to define which datatype each hyperparameter is. If we want to include this in the command,
we can add `:DATATYPE` to the hyperparameter definition. The datatype can be *int*, *float* or *file*. If you want to use
one_of as a datatype, you write a list (i.e., `[mnist,fashion_mnist,cifar10,cifar100]`) with the strings in it. If we
update the above command, we get the following command:

```bash
dvc-cc hyperopt new -d source/train.py \
                    -o tensorboard \
                    -o model.h5 \
                    -M summary.yml \
                    -f train.dvc \
                    "python source/train.py --seed {{seed:int}} --num_of_hidden_layers {{nh:int}} --num_of_kernels {{nk:int}} --dropout_rate {{dr:float}} --learning_rate {{lr:float}} --activation_function {{af:[relu,tanh]}} --batch_size {{bs:int}} --epochs {{e:int}} --dataset {{d:[mnist,fashion_mnist,cifar10,cifar100]}}"
```
