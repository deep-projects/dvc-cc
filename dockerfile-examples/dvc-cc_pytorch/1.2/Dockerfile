FROM docker.io/deepprojects/dvc-cc_basic:dev

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

# install pytorch
RUN pip install torch===1.2.0 torchvision===0.4.0 -f https://download.pytorch.org/whl/torch_stable.html

