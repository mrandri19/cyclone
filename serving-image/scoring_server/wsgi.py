import os
from . import init, _SERVER_MODEL_PATH
from mlflow.pyfunc import load_model


app = init(load_model(os.environ[_SERVER_MODEL_PATH]))
