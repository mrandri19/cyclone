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

The serving component handles serving of the ML models.
It receives a trained model from the training component, as a Docker image.
It performs autoscaling and traffic splitting in order to ensure zero downtimes.
Each deployed model will write its inputs and outputs to the storage component

The storage component handles storing of all input/output pairs from the served models.
Additionally it merges the inputs and predictions with their respective ground truths, once they become available.
Finally, it provides data for the visualizaion and training components.

The visualization (and monitoring) component will periodically compute the performance metrics of interest.
If these metrics drop below a certain threshold, it sends an alert to the training component.

The training component, once it receives an alert from the visualization and monitoring component, will retrain a model.
To do so, it loads a recent subset of labelled data from the storage layer, and use it to train a new model.
The trained model will be packaged in a Docker image, which is sent to the serving component.

### Implementation

## Scaling serving using Google Cloud Run (GCR)

## Extensions and future work 

## Lessons learned
