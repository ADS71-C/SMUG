#!/usr/bin/env bash
echo "Starting RabbitMQ and MongoDB..."
docker-compose up -d rabbitmq mongodb

echo "Waiting for them to finish starting up..."

until curl localhost:15672 &>/dev/null; do
    sleep 1
done

export RABBITMQ_URL=localhost
export MONGO_URI=mongodb://localhost:27017/smug
export PYTHONPATH=$PWD

echo "Initializing RabbitMQ and MongoDB"

python3 smug/initializers/initializer.py

cat <<EOF
Now you can start your services using docker-compose up -d --no-recreate [services...]
No services for all services
If you want some services to run multiple times, start them with the following arguments after --no-recreate:
    --scale [servicename]=[count]
e.g.
docker-compose up -d --no-recreate --scale processor_wordvec=2
EOF
