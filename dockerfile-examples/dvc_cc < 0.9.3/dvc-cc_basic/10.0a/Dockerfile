FROM docker.io/nvidia/cuda:10.0-cudnn7-runtime-ubuntu18.04
ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update \
&& apt-get install -y unzip make build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev wget \
curl llvm libncurses5-dev libncursesw5-dev xz-utils tk-dev libffi-dev liblzma-dev python-openssl git sshfs lshw  \
&& useradd -ms /bin/bash cc

RUN apt-get install -y python3 python3-pip

RUN ln -s /usr/bin/python3.6 /usr/local/bin/python
RUN ln -s /usr/bin/pip3 /usr/local/bin/pip

RUN pip install --upgrade --no-cache-dir pip

#RUN chmod 777 -R /usr/local/lib/python3.6/dist-packages/

# switch user
USER cc

# In the new DVC version it is also possible to use python 3.7 with
#  install python via pyenv
#  #ENV PATH /home/cc/.pyenv/bin:/home/cc/.pyenv/shims:${PATH}
#  #
#  #RUN curl https://pyenv.run | bash \
#  #&& pyenv install 3.7.2 \
#  #&& pyenv global 3.7.2
#  #
#  #RUN pip install --upgrade pip
#
# See this file:https://github.com/deep-projects/dvc-cc/blob/6feaae3e3b2ce3bc98cf306fb39fc3d007e8eed3/dockerfile-examples/dvc-cc_basic/10.0/Dockerfile

ENV PATH="${PATH}:/home/cc/.local/bin"

# Some common environmenta variables that Python uses
ENV LANG=C.UTF-8 LC_ALL=C.UTF-8

RUN pip install --user --no-cache-dir red-connector-ssh==1.0
RUN pip install --user --no-cache-dir git+https://github.com/efiop/dvc@2506
RUN pip install --user --no-cache-dir dvc-cc-agent==0.8.9
RUN pip install --user --no-cache-dir dvc-cc-connector==0.8.1

WORKDIR home/cc/
