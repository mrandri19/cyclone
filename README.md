# Cyclone: performance monitoring for autonomous ML model retraining

Machine Learning is taking our world by storm.
However, unlike traditional software, maintaining adequate ML model performance is a hard problem praticioners face.
This is due to ML-only issues such as concept and data drift.

Currently, most production ML models are retrained on a periodic basis.
This is not great for several reasons.
First, the data could change faster than the model is retrained.
Second, if the performance is sufficient, retraining is pointless and wastes expensive computational resources.

Cyclone is a software system that performs serving, monitoring, and automatic retraining of ML models.
This is a proof-of-concept implementation of it, created as the final project for Aalto University's CS-E4660: Advanced Topics in Software Systems. 

---

[[_TOC_]]

## Requirements

- Serve one or more machine learning models as user-accessible REST APIs
    - Scale to zero or multiple machines, depending on the usage
    - Deploy any kind of Docker container
    - Zero downtime model updates

- Store all data sent to/from the models
    - Store, in a flexible format, all input features sent to the model
    - Efficiently serve all of input data and associated labels for retraining
    - Join every input requests with its prediction and its true labels
    - Monitor input data distribution shift in real time
    - Monitor predictive performance in real time, using predictions and true labels

- Visualize metrics in real-time in a dashboard 

- Automatically retrain and redeploy models when the performance dips below a threshold

## Architecture

### High level components view

To satisfy the requirements four main components are required:

<img src="./docs/cyclone-high-level-architecture.png" width="500">

The **serving component** handles serving of the ML models.
It receives a trained model from the training component, as a Docker image.
It performs autoscaling and traffic splitting in order to ensure zero downtimes.
Each deployed model will write its inputs and outputs to the storage component

The **storage component** handles storing of all input/output pairs from the served models.
Additionally it merges the inputs and predictions with their respective ground truths, once they become available.
Finally, it provides data for the visualizaion and training components.

The **visualization (and monitoring) component** will periodically compute the performance metrics of interest.
If these metrics drop below a certain threshold, it sends an alert to the training component.

The **training component**, once it receives an alert from the visualization and monitoring component, will retrain a model.
To do so, it loads a recent subset of labelled data from the storage layer, and use it to train a new model.
The trained model will be packaged in a Docker image, which is sent to the serving component.

### Implementation

<img src="./docs/cyclone-implementation-architecture.png" width="900">

The **serving component** uses Google Cloud Run (GCR) to serve Docker images.
GCR is an hosted platform based on Kubernetes and Knative.
It supports out of the box all of the features we need (traffic splitting, scaling to zero, scaling horizontally).
Additionally, it also handles load balancing and HTTPS certificate renewal.
We deploy a service on GCR called `cyclone-gcr-service`.
This service serves the ML model images to users, exposing them via an HTTPS endpoint.

The **storage component** uses Google Cloud SQL to store and serve data.
It is an hosted database product, based on PostgreSQL.
The database uses a table called `prediction` to store our data.
The table's schema is:
```sql
CREATE TABLE prediction (
    id INTEGER PRIMARY KEY,
    input JSONB NOT NULL,
    prediction JSONB NOT NULL,
    model_id TEXT NOT NULL,
    label JSONB,
    created_at TIMESTAMPTZ NOT NULL
)
```

The **visualization (and monitoring) component** uses Grafana hosted on a Google Compute Engine VM Instance to build interactive dashboards.
Additionally, it uses Grafana alerts and webhook notification channels to notify the training components to retraing a model.
The dashboard looks like this:

<img src="./docs/grafana.png" width="900">

The **training component** is a custom Python server, hosted on a Google Compute Engine VM Instance.
Under the hood, it uses mlflow to train, evaluate, and package ML models into Docker containers.
When a model has been trained, it will be pushed to the **image registry component**, which uses Google Cloud's Artifact Registry.
Finally, GCR's Admin API is used to deploy a new revision of the `cyclone-gcr-service`, pulling the latest Docker image from the registry.

## Project structure

```bash
.
├── 01-bike-sharing-demand-drift.ipynb # notebook to show a model's performance drop over time and the positive impact of retraining 
├── 02-test-model-serving.ipynb # notebook to test mlflow's local model serving
├── 03-test-docker-model-serving.ipynb # notebook to test mlflow's dockerized model serving
├── 04-test-docker-training-serving.ipynb # notebook to test mlflow's dockerized model training and serving
├── 05-gcloud.ipynb # notebook to test deploying a model serving image on Google Cloud
├── 06-demo-steps.ipynb # notebooks to run the demo
├── README.md
├── bike-rental-regression # mlflow project to train a model and produce a scikit-learn model artifact
├── brain # Flask app that listens for grafana webhook calls and retrains and redeploys new models on GCR
├── data
├── docs
└── serving-image # Custom Docker image and custom serving app. Replaces mlflow's default serving image
```

## Improvements and future work

TODO(Andrea): write

- Reactive, message-based architecture in order to decouple components. Especially important to decouple serving and storage

- Separate inference storage from data storage. Perhaps even introduce a feature store. How to keep loop latency low though?

- Use DAG scheduler such as Airflow instead of custom application (brain) for retraining and redeploying

- Reduce loop latency by speeding up docker container building or by restricing model families and only updating parameters

- Model, data, inference lineage and observability. See mltrace and DVC.

- Distributed training, distributed image building (Cloud build)

- Declarative deployment (Terraform? Docker swarm? Kubernetes?, Infrastracture as Code)

## Lessons learned

TODO(Andrea): write

- Serverless serving architecture using Google Cloud Run simplifies serving workflow a lot

- Working locally gives fast feedback, but then you have to deploy and face environment differences which are hard to debug

## References

TODO(Andrea): write

- Josh Tobin

- Chip Huyen

- Shreya Shankar

