FROM docker.io/deepprojects/dvc-cc_basic:10.0

# Often used libraries
RUN pip --no-cache-dir install \
        Pillow \
        h5py \
        ipykernel \
        jupyter \
        keras_applications \
        keras_preprocessing \
        matplotlib \
        mock \
        numpy \
        scipy \
        sklearn \
        pandas \
        dvc \
        paramiko \
        pyyaml \
        seaborn \
        pandas

# install tensorflow
RUN pip install tensorflow-gpu
RUN pip install --no-cache-dir tensorboard

# install pytorch
RUN pip install torch torchvision

