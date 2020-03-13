FROM docker.io/nvidia/cuda:10.1-cudnn7-runtime-ubuntu18.04

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update \
&& apt-get install -y unzip make build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev wget \
curl llvm libncurses5-dev libncursesw5-dev xz-utils tk-dev libffi-dev liblzma-dev python-openssl git sshfs lshw  \
&& useradd -ms /bin/bash cc

# switch user
USER cc

# install python via pyenv
ENV PATH /home/cc/.pyenv/bin:/home/cc/.pyenv/shims:${PATH}

RUN curl https://pyenv.run | bash \
&& pyenv install 3.7.2 \
&& pyenv global 3.7.2

RUN pip install --upgrade pip

# For the direcotry connector
RUN pip install --upgrade red-connector-ssh==0.7

# install tensorflow
RUN pip install tensorflow-gpu==2.0.0-rc0

# Some common environmenta variables that Python uses
ENV LANG=C.UTF-8 LC_ALL=C.UTF-8

# Install a specific version of TensorFlow
# You may also install anything else from pip like this
RUN pip install --no-cache-dir tensorboard

RUN pip install torch===1.2.0 torchvision===0.4.0 -f https://download.pytorch.org/whl/torch_stable.html

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

RUN echo 'INSTALL dvc-cc-agent and the dvc-cc-connector 53!'

RUN pip install dvc-cc-agent
RUN pip install dvc-cc-connector

WORKDIR home/cc/

