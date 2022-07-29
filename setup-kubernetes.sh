#!/bin/bash

DIR="$(dirname "$0")"

if ! [[ -f $DIR/kubernetes/.env.db.secret ]]; then
    read -p "Database Password: " DB_PASSWORD
    printf "DB_PASSWORD=$DB_PASSWORD\n" > $DIR/kubernetes/.env.db.secret
fi
