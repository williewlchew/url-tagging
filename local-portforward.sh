#!/bin/sh
#
kubectl port-forward --address 0.0.0.0 service/rabbitmq 5672:5672 &
kubectl port-forward --address 0.0.0.0 service/redis 6379:6379 &
kubectl port-forward --address 0.0.0.0 service/mysql 3306:3306 &