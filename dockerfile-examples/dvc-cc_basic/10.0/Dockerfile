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

# Some common environmenta variables that Python uses
ENV LANG=C.UTF-8 LC_ALL=C.UTF-8

RUN pip install dvc-cc-agent==0.8.5
RUN pip install dvc-cc-connector

WORKDIR home/cc/

