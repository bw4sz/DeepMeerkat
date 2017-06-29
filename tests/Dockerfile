FROM google/cloud-sdk
MAINTAINER Ben Weinstein

RUN apt-get update
RUN apt-get install -y build-essential apt-utils

RUN apt-get install -y git

RUN apt-get update && apt-get install -y python-dev python-numpy libtbb2 libtbb-dev \
  libjpeg-dev libjasper-dev libdc1394-22-dev

RUN apt-get install -y python-pip wget
RUN pip install --upgrade pip

RUN pip install --upgrade google-cloud google-api-python-client apache_beam google-cloud-dataflow parse
