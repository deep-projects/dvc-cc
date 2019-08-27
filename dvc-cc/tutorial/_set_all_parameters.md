# Sorry
This tutorial is in work!
![IN WORK](work-2062096_640.jpg)

```
dvc-cc hyperopt new -d source/train.py \
                    -o tensorboard \
                    -o model.h5 \
                    -m summary.yml \
                    -f train.dvc \
                    "python source/train.py --seed {{seed:int}} --num_of_hidden_layers {{nh:int}} --num_of_kernels {{nk:int}} --dropout_rate {{dr:float}} --learning_rate {{lr:float}} --activation_function {{af:[relu,tanh]}} --batch_size {{bs:int}} --epochs {{e:int}} --dataset {{d:[mnist,fashion_mnist,cifar10,cifar100]}}"
```