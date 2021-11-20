FROM continuumio/miniconda3:4.10.3
ARG MLFLOW_MODEL_PATH
ARG CUSTOM_SCORING_SERVER_PATH

WORKDIR /opt/mlflow

RUN pip install mlflow

COPY ${MLFLOW_MODEL_PATH} /opt/ml/model

# MLflow's `_install_pyfunc_deps` expects conda (or miniconda) to live in
# `/miniconda`, see [0]. While the base Docker image we are using installs it in
# `/optTODO(Andrea): if this works, explain why/conda`. To fix this we make a
# simlink.
# [0]: https://github.com/mlflow/mlflow/blob/0fa849ad75e5733bf76cc14a4455657c5c32f107/mlflow/models/docker_utils.py#L33
RUN ln -s /opt/conda/ /miniconda

RUN python -c 'from mlflow.models.container import _install_pyfunc_deps; _install_pyfunc_deps("/opt/ml/model")'

# Taken from https://pythonspeed.com/articles/activate-conda-dockerfile/
SHELL ["conda", "run", "-n", "custom_env", "/bin/bash", "-c"]

# TODO(Andrea)
RUN conda install -n custom_env -c conda-forge flask-sqlalchemy
RUN conda install -n custom_env -c anaconda psycopg2

# https://github.com/mlflow/mlflow/blob/9faf3b04c9f6b3766a64d7433dd3e85bcdf27fff/mlflow/pyfunc/scoring_server/__init__.py#L382
ENV __pyfunc_model_path__='file:/opt/ml/model'

COPY ${CUSTOM_SCORING_SERVER_PATH} /opt/mlflow/scoring_server

EXPOSE 8000
ENTRYPOINT ["conda", "run", "--no-capture-output", "-n", "custom_env", "gunicorn", "--bind", "0.0.0.0", "--workers",  "1", "--threads", "8", "--timeout", "0", "scoring_server.wsgi:app"]