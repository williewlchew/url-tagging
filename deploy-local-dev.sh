#!/bin/sh
#
# This script is used to launch the Redis, MySQL, and RabbitMQ on components using Kubernetes.
# A separate script is provided for forwarding their connections to your local computer.

kubectl apply -f redis/redis-deployment.yaml
kubectl apply -f redis/redis-service.yaml
kubectl apply -f rabbitmq/rabbitmq-deployment.yaml
kubectl apply -f rabbitmq/rabbitmq-service.yaml
kubectl apply -f mysql/mysql-deployment.yaml
kubectl apply -f mysql/mysql-service.yaml
kubectl apply -f mysql/mysql-volume.yaml
