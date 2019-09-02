# DVC-CC: Creating a DVC-Pipeline

This site is an extension of the [main tutorial](Get_Started.md). Make sure you read it before you read this site.

If you are familiar with DVC you could be interested to use DVC directly to define your pipeline. First lets take a 
look at the script from the main tutorial:

<img src="get_started_pipeline.png" alt="drawing" width="800"/>

If we know what we want do, we can set all parameters directly and could run the following command: 
```bash
dvc run --no-exec -d source/train.py \
                  -o tensorboard \
                  -o model.h5 \
                  -m summary.yml \
                  -f train.dvc \
                  "python source/train.py --seed 100 --num_of_hidden_layers 3 --num_of_kernels 128 --dropout_rate 0.1 --learning_rate 0.01 --activation_function relu --batch_size 512 --epochs 1000 --dataset mnist"
```

The `dvc run --no-exec ...` command is the same as `dvc-cc hyperopt new ...` without using any hyperparameters, with
the only exception that DVC-CC will always save the DVC-files in the *dvc* folder. To try new parameters your can
just overwrite the DVC file by using the same command with different values.

All DVC files created directly with DVC or with DVC-CC can be run on a cluster with CC.