FROM python:3.8.11-buster
LABEL org.opencontainers.image.source=https://github.com/dtpstat/dtp-stat
ENV PYTHONDONTWRITEBYTECODE 1

RUN apt-get update && apt-get install -y --no-install-recommends \
  binutils \
  gdal-bin \
  libproj-dev \
  locales \
  && sed -i -e 's/# ru_RU.UTF-8 UTF-8/ru_RU.UTF-8 UTF-8/' /etc/locale.gen \
  && dpkg-reconfigure --frontend=noninteractive locales \
  && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && apt-get clean -y \
  && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

WORKDIR /app
COPY Pipfile Pipfile
COPY Pipfile.lock Pipfile.lock
RUN pip3 install pipenv --no-cache-dir \
    && pipenv install --deploy --system --ignore-pipfile \
    && pipenv --clear && rm -rf $(pip cache dir)
COPY . .

EXPOSE 5000
CMD ["gunicorn", "--bind", ":5000", "dtpstat.wsgi"]
