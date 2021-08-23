FROM python:3.8.11-buster
LABEL org.opencontainers.image.source=https://github.com/dtpstat/dtp-stat

RUN apt-get update && apt-get install -y \
  binutils \
  gdal-bin \
  libproj-dev

WORKDIR /app
COPY requirements/app.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY . .

EXPOSE 5000
ENTRYPOINT ["gunicorn", "--bind", ":5000", "dtpstat.wsgi"]