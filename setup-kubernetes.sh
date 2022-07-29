#!/bin/bash

DIR="$(dirname "$0")"

if ! [[ -f $DIR/kubernetes/secrets/env.db.secret ]]; then
    read -p "Database Password: " DB_PASSWORD
    printf "DB_PASSWORD='$DB_PASSWORD'\n" > $DIR/kubernetes/secrets/env.db.secret
fi

kubectl apply -k $DIR/kubernetes/secrets

if ! [[ -f $DIR/kubernetes/regcred.secret.yaml ]]; then
    read -p "Docker Username: " DOCKER_USERNAME
    read -p "Docker Email: " DOCKER_EMAIL
    read -p "Docker Access Key: " DOCKER_ACCESS_KEY
    kubectl create secret docker-registry --dry-run=client regcred \
        --docker-email='$DOCKER_EMAIL' \
        --docker-username='$DOCKER_USERNAME' \
        --docker-password='$DOCKER_ACCESS_KEY' \
        -o yaml > $DIR/kubernetes/regcred.secret.yaml
fi

kubectl apply -f $DIR/kubernetes/regcred.secret.yaml

mkdir -p /tmp/db-pv
