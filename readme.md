Social Media User Grouper (SMUG)

SMUG is a profiler which allows you to group social media users using big data.
SMUG provides extra insight into tweets by running various kinds of analytics on it. 

For example it can give a propibility about if a giving tweet is about someone being sick.
This is accomplished by analysing the words in the tweet using deep learning.
# Dependencies
In order to use the project the following dependencies have to be satisfied
* Docker
* Docker-Compose
* Python3

# Installation
1 run `pip install -r requirements.txt`

# Usage instructions
This project uses docker-compose thus to run the project you need to issue the command `docker-compose up`. 
This will pull all the required images and runs all the containers. 
There are several things needed to run the project correctly:

* `.env` file. See `resources/.env.example` for the needed parameters
* trained `word2vec` model.
* csv files containing data. In our case this will be twitter data from our provider.

# Technical information 
## Local development
While developing you can opt to run the python files locally on your system. This can be done by running the individual python files.
A `run.py` is also  which allows you to start multiple workers at once. 
`run.py` start all the workers necessary for basic processing.
Now all you need is data. 
This can be done by running `importers/csv_importer.py` which will prompt you for a csv file. 
This csv file is then put into SMUG.
This csv file should be located somewhere in the `resources` folder
## Command ordering
In order to ensure the docker environment contains the correct settings and queues it is important that the `initializer.py` file is ran every time the docker environment is restarted.
After running the initializer the order of execution is not important. 
When using `run.py` this is done automatically for you.
