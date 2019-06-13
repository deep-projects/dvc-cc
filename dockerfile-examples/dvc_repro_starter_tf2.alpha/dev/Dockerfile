FROM docker.io/nvidia/cuda:10.0-cudnn7-runtime-ubuntu18.04

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
RUN pip install tensorflow-gpu==2.0.0-alpha0


# Some common environmenta variables that Python uses
ENV LANG=C.UTF-8 LC_ALL=C.UTF-8

# Install lower level dependencies
#RUN apt-get update --fix-missing -y && apt-get upgrade -y && \
#    apt-get install -y curl python3 python3-pip && \
#    update-alternatives --install /usr/bin/python python /usr/bin/python3 10 && \
#    update-alternatives --install /usr/bin/pip pip /usr/bin/pip3 10 && \
#    apt-get clean && \
#    apt-get autoremove 

# Install a specific version of TensorFlow
# You may also install anything else from pip like this
RUN pip install --no-cache-dir tensorboard

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
        paramiko

#RUN apt-get install git  -y

# switch user
#RUN useradd -ms /bin/bash cc

#RUN mkdir /home/cc/.local

RUN echo 'START HERE 5'

RUN pip install https://github.com/mastaer/dvc-cc/releases/download/cc-connector-variable-to-file-0.1.0/cc_connector_variable_to_file-0.1.0-py3-none-any.whl

RUN pip install https://github.com/mastaer/dvc-cc/releases/download/dvc-cc-server-0.1.0/dvc_cc_server-0.1.0-py3-none-any.whl

WORKDIR home/cc/
