from flask import Flask, request, abort, jsonify
from multiprocessing import Process
import subprocess
import re
import shutil

app = Flask(__name__)


def make_mlflow_run() -> str:
    mlflow_path = shutil.which('mlflow')
    if mlflow_path is None:
        raise RuntimeError("Couldn't find mlflow binary")

    command = [mlflow_path, 'run', 'bike-rental-regression',
               '-P', 'num_train=400', '-P', 'num_test=100']
    env = {
        'DB_USER': 'postgres',
        'DB_PASS': 'tBFeoxc3HhI8p9ox',
        'DB_HOST': 'host.docker.internal',
        'DB_NAME': 'predictions',
        'DB_PORT': '5432',
    }
    app.logger.debug('Running mlflow run')
    result = subprocess.run(command, capture_output=True, text=True, env=env)
    result.check_returncode()

    app.logger.debug("Parsing command's output")
    last_line = result.stderr.strip().split('\n')[-1]
    matches = re.findall(
        r"=== Run \(ID '([a-z0-9]+)'\) succeeded ===", last_line)

    if not matches:
        app.logger.error(result)
        raise RuntimeError("Couldn't parse Docker output")

    mlflow_run_id = matches[0]

    return mlflow_run_id


def make_serving_image_from_mlflow_run(mlflow_run_id):
    app.logger.debug('Running docker build')
    build_command = ['docker', 'build',
                     '-t', 'my-serving-image:latest',
                     '-f', 'serving-image/Dockerfile',
                     '--build-arg', f'MLFLOW_MODEL_PATH=mlruns/0/{mlflow_run_id}/artifacts/model',
                     '--build-arg', 'CUSTOM_SCORING_SERVER_PATH=serving-image/scoring_server',
                     '.']
    subprocess.run(build_command, capture_output=True,
                   text=True).check_returncode()


def tag_and_push_image():
    app.logger.debug('Tagging image')
    tag_command = ['docker', 'tag', 'my-serving-image:latest',
                   'europe-north1-docker.pkg.dev/aalto-atss/cyclone-docker-repo/my-serving-image:latest']
    subprocess.run(tag_command, capture_output=True,
                   text=True).check_returncode()

    app.logger.debug('Pushing image')
    push_command = ['docker', 'push',
                    'europe-north1-docker.pkg.dev/aalto-atss/cyclone-docker-repo/my-serving-image:latest']
    subprocess.run(push_command, capture_output=True,
                   text=True).check_returncode()


def deploy_new_GCR_revision():
    app.logger.debug('Deploying revision')
    deploy_command = ['gcloud', 'run', 'deploy', 'my-serving-image',
                      '--image', 'europe-north1-docker.pkg.dev/aalto-atss/cyclone-docker-repo/my-serving-image:latest',
                      '--region=europe-north1']
    subprocess.run(deploy_command, capture_output=True,
                   text=True).check_returncode()


def retrain():
    app.logger.info('Retraining')

    mlflow_run_id = make_mlflow_run()
    app.logger.info('Created run %s', mlflow_run_id)

    make_serving_image_from_mlflow_run(mlflow_run_id)
    app.logger.info('Built serving image')

    tag_and_push_image()
    app.logger.info('Tagged and pushed image')

    deploy_new_GCR_revision()
    app.logger.info('Deployed new GCR revision')


@app.route("/route", methods=["POST"])
def route():
    if not request.is_json:
        abort(400)

    if request.json.get('state') == "alerting":
        app.logger.info("Triggering retraining")
        Process(target=retrain).start()

    return jsonify("OK")


if __name__ == "__main__":
    app.run()
