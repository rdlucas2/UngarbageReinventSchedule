# pull official base image
FROM python:3.9.5-slim-buster as base

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy project 
#COPY ./src . # commented out for now - instead going to mount the working directory #

FROM base as web
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--reload"]
