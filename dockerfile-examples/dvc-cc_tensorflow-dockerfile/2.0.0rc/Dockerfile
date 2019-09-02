FROM docker.io/deepprojects/dvc-cc_basic-dockerfile:dev

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
RUN pip install tensorflow-gpu==2.0.0-rc0
RUN pip install --no-cache-dir tensorboard
