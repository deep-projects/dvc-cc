# RUN ONE - NOW WITH DATA IN CACHE
dvc run --no-exec -d data/camelyonpatch_level_2_split_train_x.h5 -d data/camelyonpatch_level_2_split_train_y.h5 -d data/camelyonpatch_level_2_split_valid_x.h5 -d data/camelyonpatch_level_2_split_valid_y.h5 -o tf_models/tf_model.h5 -o tensorboards/tb/* -o outputs/all-history.json -o outputs/history-summary.json -f dvc/train_network.dvc --overwrite-dvcfile python code/train.py -lr 0.2

git add dvc/train_network.dvc

dvc-cc run -r 100 -nb 'try_learning_rate_0.2'



# RUN TWO: Only the parameter changed !

dvc run --no-exec -d data/camelyonpatch_level_2_split_train_x.h5 -d data/camelyonpatch_level_2_split_train_y.h5 -d data/camelyonpatch_level_2_split_valid_x.h5 -d data/camelyonpatch_level_2_split_valid_y.h5 -o tf_models/tf_model.h5 -o tensorboards/tb/* -o outputs/all-history.json -o outputs/history-summary.json -f dvc/train_network.dvc --overwrite-dvcfile python code/train.py -lr 0.5

git add dvc/train_network.dvc

dvc-cc run -r 100 -nb 'try_learning_rate_0.5'



# RUN THREE: Only the parameter changed !

dvc run --no-exec -d data/camelyonpatch_level_2_split_train_x.h5 -d data/camelyonpatch_level_2_split_train_y.h5 -d data/camelyonpatch_level_2_split_valid_x.h5 -d data/camelyonpatch_level_2_split_valid_y.h5 -o tf_models/tf_model.h5 -o tensorboards/tb/* -o outputs/all-history.json -o outputs/history-summary.json -f dvc/train_network.dvc --overwrite-dvcfile python code/train.py -lr 0.1

git add dvc/train_network.dvc

dvc-cc run -r 100 -nb 'try_learning_rate_0.1'





# RUN FOUR: Only the parameter changed !

dvc run --no-exec -d data/camelyonpatch_level_2_split_train_x.h5 -d data/camelyonpatch_level_2_split_train_y.h5 -d data/camelyonpatch_level_2_split_valid_x.h5 -d data/camelyonpatch_level_2_split_valid_y.h5 -o tf_models/tf_model.h5 -o tensorboards/tb/* -o outputs/all-history.json -o outputs/history-summary.json -f dvc/train_network.dvc --overwrite-dvcfile python code/train.py -lr 0.05

git add dvc/train_network.dvc

dvc-cc run -r 100 -nb 'try_learning_rate_0.05'





# RUN FIVE: Only the parameter changed !

dvc run --no-exec -d data/camelyonpatch_level_2_split_train_x.h5 -d data/camelyonpatch_level_2_split_train_y.h5 -d data/camelyonpatch_level_2_split_valid_x.h5 -d data/camelyonpatch_level_2_split_valid_y.h5 -o tf_models/tf_model.h5 -o tensorboards/tb/* -o outputs/all-history.json -o outputs/history-summary.json -f dvc/train_network.dvc --overwrite-dvcfile python code/train.py -lr 0.01

git add dvc/train_network.dvc


dvc-cc run -r 100 -nb 'try_learning_rate_0.01'



dvc-cc cancel --all



# get the experiment ID! of the failed batch (this is not the batch id!)
dvc-cc status -f -id



