FROM continuumio/miniconda3:4.10.3
ARG MLFLOW_MODEL_PATH

WORKDIR /opt/mlflow

RUN pip install mlflow

COPY $MLFLOW_MODEL_PATH /opt/ml/model

# TODO(Andrea): if this works, explain why
RUN ln -s /opt/conda/ /miniconda

RUN python -c 'from mlflow.models.container import _install_pyfunc_deps; _install_pyfunc_deps("/opt/ml/model")'

# TODO(Andrea): this is what I need to fix next
ENV MLFLOW_DISABLE_ENV_CREATION="true"
ENV DISABLE_NGINX="true"

# TODO(Andrea): what about MLSERVER??
ENTRYPOINT [ "python", "-c", "from mlflow.models.container import _serve; import os; print(os.environ.get('')); _serve()" ]