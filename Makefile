
docker-base:
	docker build . --file=docker/python-base/Dockerfile -t smug-python-base 

docker-source:
	docker build . --file=docker/source-base/Dockerfile -t smug-source-base 
	docker-compose build
