FROM docker.io/tensorflow/tensorflow:2.2.0rc2-gpu-py3
ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update \
&& apt-get install -y unzip make build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev wget \
curl llvm libncurses5-dev libncursesw5-dev xz-utils tk-dev libffi-dev liblzma-dev python-openssl git sshfs lshw  \
&& useradd -ms /bin/bash cc

# switch user
USER cc

ENV PATH="${PATH}:/home/cc/.local/bin"

# Some common environmenta variables that Python uses
ENV LANG=C.UTF-8 LC_ALL=C.UTF-8

RUN pip install --user --no-cache-dir \
    Pillow \
    h5py \
    keras_preprocessing \
    matplotlib \
    numpy \
    scipy \
    sklearn \
    pandas \
    tensorflow-probability \
    seaborn \
    torch \
    torchvision \
    papermill \
    jupyter \
    black

RUN echo 'INSTALL dvc-cc-agent and the dvc-cc-connector!'

RUN pip install --user --no-cache-dir red-connector-ssh==1.2
RUN pip install --user --no-cache-dir dvc==0.93.0
RUN pip install --user --no-cache-dir dvc-cc-agent==0.9.24
RUN pip install --user --no-cache-dir dvc-cc-connector==0.8.1

WORKDIR home/cc/
