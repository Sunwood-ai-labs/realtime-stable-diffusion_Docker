# FROM ubuntu:22.04
FROM nvcr.io/nvidia/pytorch:23.08-py3


RUN apt-get update && apt-get upgrade -y
RUN apt-get install -y git python3 python3-pip curl aria2

# RUN aria2c -x 5 --dir / --out xformers-0.0.21.dev544-cp310-cp310-manylinux2014_x86_64.whl 'https://github.com/AbdBarho/stable-diffusion-webui-docker/releases/download/6.0.0/xformers-0.0.21.dev544-cp310-cp310-manylinux2014_x86_64-pytorch201.whl'
# RUN pip install /xformers-0.0.21.dev544-cp310-cp310-manylinux2014_x86_64.whl

RUN python3 -m pip install --upgrade pip
RUN pip install numpy matplotlib pandas

COPY . .
# RUN pip install -r requirements.txt
RUN pip install -r requirements_versions.txt
RUN pip uninstall -y transformer-engine

# RUN pip install open-interpreter==0.1.4
# RUN pip install --upgrade open-interpreter

WORKDIR /root