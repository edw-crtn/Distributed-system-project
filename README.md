# Project Documentation – Flask App on Kubernetes

# 1. Project Overview

This project is a Flask web application deployed on a local Kubernetes cluster (Minikube).
The app allows users to vote between two characters, updating their Elo scores stored in a MongoDB replica set, with Redis used as a cache layer for improved performance.

The application is containerized with Docker, orchestrated by Kubernetes, and continuously deployed through a GitHub Actions CI/CD pipeline.
The full stack (Flask + MongoDB + Redis) runs inside the Kubernetes cluster. There are no external databases or cloud services.

# 2. Cluster Setup (Local Environment)

## Requirements

- Minikube (for local Kubernetes cluster)

- kubectl

- Docker

- nginx-ingress addon for routing traffic to the app

## Steps

Start the cluster:

`minikube start`

Enable the ingress controller:

`minikube addons enable ingress`

Apply Kubernetes configurations:

`kubectl apply -f redis-deployment.yaml`
`kubectl apply -f mongo-statefulset.yaml`
`kubectl apply -f mongo-init-job.yaml`
`kubectl apply -f app_deployment.yaml`
`kubectl apply -f ingress.yaml`

Add host entry (local DNS mapping):
Add this line to your`/etc/hosts` file:

`127.0.0.1 hello.local`

Access the app:
Once all pods are running, visit:

http://hello.local/

# 2. CI/CD Pipeline

The CI/CD process is defined in `.github/workflows/ci-cd.yml` and automates testing, image building, and deployment updates.

## Workflow Steps

1. Triggered: On push to main branch.
2. Install dependencies: Installs Flask, Pytest, PyMongo, and Redis.
3. Run unit tests: Executes the test suite using Pytest.
4. Build Docker image: Tags image with the commit SHA.
5. Push to Docker Hub: Publishes image under edwin765/hello-k8s.
6. Auto-deploy: The cluster continuously runs watch_docker_update.py to detect new images and update the deployment automatically.

## Auto-Update Script (`watch_docker_update.py`)

This script runs in the terminal to automatically detect and deploy new images from Docker Hub.

# 3. Database Setup

## MongoDB (Replica Set)

The MongoDB setup is fully containerized and deployed inside the cluster using a StatefulSet.
It automatically creates three replicas for high availability.

The replica set initialization is handled by `mongo-init-job.yaml`, which waits for the MongoDB pods to be ready and executes the replica setup command.

## Redis Cache

Redis runs as a single-pod deployment defined in `redis-deployment.yaml`.
Redis is used for caching to reduce MongoDB read load and improve API responsiveness.

# 4. Monitoring and Scaling

## Monitoring the Cluster

Use the Minikube Dashboard for real-time monitoring and control of all cluster resources.

`minikube dashboard`

You can:

- Monitor pod and service health.
- Check MongoDB and Redis status.
- View logs and events.

## Scaling the Application

To scale the Flask app horizontally:

`kubectl scale deployment hello-k8s-deployment --replicas=5` or you can do it directly in `minikube dashboard`

To scale MongoDB or Redis, simply edit the replicas field in their respective YAML manifests.

# 5. Onboarding Guide for New Developers

## Setup Steps

Clone the repository

`git clone https://github.com/<your-username>/Distributed-system-project.git`
`cd Distributed-system-project`

Run the app locally

`pip install -r requirements.txt`
`python app.py`

Deploy to Kubernetes

`minikube start`
`minikube tunnel`
`kubectl apply -f redis-deployment.yaml`
`kubectl apply -f mongo-statefulset.yaml`
`kubectl apply -f mongo-init-job.yaml`
`kubectl apply -f app_deployment.yaml`
`kubectl apply -f service.yaml`
`kubectl apply -f ingress.yaml`

Wait until all pods are ready:

`kubectl get pods`

Seed the database

Run the seed script inside the running Flask pod:

`kubectl exec -it $(kubectl get pod -l app=hello-k8s -o jsonpath='{.items[0].metadata.name}') -- python seed_db.py`

Access the site

`http://hello.local`

Push changes for CI/CD
When pushing to the main branch:

Tests will run automatically.

A Docker image will be built and pushed to Docker Hub.

The Kubernetes cluster will auto-update via the watcher script.
