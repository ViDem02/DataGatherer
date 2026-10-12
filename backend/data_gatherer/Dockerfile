# pull official base image
FROM python:3.11-slim-bookworm

# set work directory
WORKDIR /srv/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV ANNOY_COMPILER_ARGS=-DNO_MANUAL_VECTORIZATION

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt .

RUN apt-get update && apt-get install -y \
  gcc \
  netcat-openbsd \
  libpq-dev \
  postgresql-client \
  g++ \
  && apt-get clean

ENV PYHTONUNBUFFERED=1
RUN apt-get update \
  && apt-get -y install tesseract-ocr \
  && apt-get -y install ffmpeg libsm6 libxext6 # required for opencv & pytesseract



# install temp dependencies for build of pyscopg2 etc
RUN pip install -r requirements.txt

# copy entrypoint.sh
COPY ./entrypoint.sh .

# copy project
COPY . .

RUN sed -i -e 's/\r$//' entrypoint.sh
# run entrypoint.sh
ENTRYPOINT ["/srv/app/entrypoint.sh"]