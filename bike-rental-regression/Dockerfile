FROM continuumio/miniconda3:4.10.3

RUN apt-get update
RUN apt-get install libpq-dev build-essential -y
RUN pip install --prefer-binary mlflow pandas scikit-learn sqlalchemy psycopg2
RUN pip install mlflow pandas scikit-learn sqlalchemy psycopg2
