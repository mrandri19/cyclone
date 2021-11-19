FROM continuumio/miniconda3:4.10.3
ARG MLFLOW_MODEL_PATH

WORKDIR /opt/mlflow

RUN pip install mlflow

COPY $MLFLOW_MODEL_PATH /opt/ml/model

# MLflow's `_install_pyfunc_deps` expects conda (or miniconda) to live in
# `/miniconda`, see [0]. While the base Docker image we are using installs it in
# `/optTODO(Andrea): if this works, explain why/conda`. To fix this we make a
# simlink.
# [0]: https://github.com/mlflow/mlflow/blob/0fa849ad75e5733bf76cc14a4455657c5c32f107/mlflow/models/docker_utils.py#L33
RUN ln -s /opt/conda/ /miniconda

RUN python -c 'from mlflow.models.container import _install_pyfunc_deps; _install_pyfunc_deps("/opt/ml/model")'

# `_serve` wil call `_install_pyfunc_deps` again unless we tell it not to. If
# `_install_pyfunc_deps` is called twice, it will fail because it will try to
# recreate an existing conda environment
ENV MLFLOW_DISABLE_ENV_CREATION="true"
ENV DISABLE_NGINX="true"
# TODO(Andrea): what about MLSERVER??
ENTRYPOINT [ "python", "-c", "from mlflow.models.container import _serve; _serve()" ]