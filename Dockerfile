ARG PYTHON_VERSION="3.11-bookworm"

FROM python:$PYTHON_VERSION

RUN apt update && apt install -y git gcc
RUN git config --global credential.helper cache

# COPY ./ ./
# 

COPY ./setup.py ./setup.py
COPY ./daikin_residential ./daikin_residential
COPY ./growatt ./growatt
COPY ./helpers ./helpers
COPY ./kebakeycontactP30 ./kebakeycontactP30
COPY ./mqttservice ./mqttservice
COPY ./sdm_modbus ./sdm_modbus
COPY ./smdmeter2ppmpconnector ./smdmeter2ppmpconnector

# Enable Virtual Environment
ENV VIRTUAL_ENV=/opt/venv
RUN python -m venv $VIRTUAL_ENV
RUN . $VIRTUAL_ENV/bin/activate

RUN pip install --upgrade pip

RUN pip install Cython

# RUN pip install setup.py
# RUN python3 setup.py install

RUN pip install git+https://github.com/srw2ho/smdmeter2ppmpconnector.git


RUN pip install  pip-licenses
RUN pip-licenses --with-system --with-urls --order=license > ./python_dependencies.txt

RUN pip uninstall -y Cython pip-licenses 

ENTRYPOINT tail -f /dev/null
