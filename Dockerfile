FROM python:3.8.3-buster

RUN apt-get update && apt-get install -y \
  binutils \
  gdal-bin \
  python3-gdal \
  libgdal-dev \
  libproj-dev

WORKDIR /app
COPY . .
RUN pip3 install -r requirements.txt
