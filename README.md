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

## Architecture

### Scaling serving using Google Cloud Run (GCR)

## Extensions and future work 

## Lessons learned
