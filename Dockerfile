FROM python:3.9-slim-buster

RUN apt update && apt install -y git gcc
RUN git config --global credential.helper cache

# COPY ./ ./
# 

COPY ./setup.py ./setup.py

COPY ./sdm_modbus ./sdm_modbus

COPY ./smdmeter2ppmpconnector ./smdmeter2ppmpconnector

# Enable Virtual Environment
ENV VIRTUAL_ENV /virtualenv
ENV PATH /virtualenv/bin:$PATH

RUN pip install Cython

# RUN pip install setup.py
# RUN python3 setup.py install

RUN pip install git+https://github.com/srw2ho/iothub2ppmpconnector.git

# RUN pip install git+https://github.com/srw2ho/smdmeter2ppmpconnector.git



ENTRYPOINT tail -f /dev/null
