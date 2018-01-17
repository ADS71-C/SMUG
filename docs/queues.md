# Queues
Under the hood smug is essentially a series of queues. These queues perform various tasks. In this document the use of each queue will be documented.

```eval_rst
.. blockdiag::

   blockdiag {
       clean [label = "Clean"];
       preprocessing [label = "Preprocess"];
       processing [label = "Process"];
       save [label = "Save"];
       
        clean -> preprocessing -> processing -> save;
   }
```

These are the basic types of queues that SMUG is made of. Below each queue category will be explained and an example will be given of the funtionality of each queue.
## Queue types
### Clean
This queue is responsible for making sure that only tweets that are relevant to our analysis get into SMUG.
This means that for example retweets get filtered. These tweets don't say something about the person retweeting the tweet. 
Analysing these tweets could also cause inconsistency in our data. Thus retweets get dropped.

##### Example
```eval_rst
    +-------------------------------------------------------+----------------+
    | Message                                               | Action         |
    +============+==========================================+================+
    | Hello World                                           | Passed through |
    +-------------------------------------------------------+----------------+
    | RT@SAMPLE_USER: Hello World                           | **Dropped**    |
    +-------------------------------------------------------+----------------+
    | SAMPLE TWEET                                          | Passed through |
    +-------------------------------------------------------+----------------+
    | The weather is nice, isn't it? https://theweather.com | Passed through |
    +-------------------------------------------------------+----------------+
```
### Preprocess
This step prepares data for processing. By doing this as a separate step no duplicate computations are done. This step outputs a list of separated preprocessed words along side the original message. The original message is still human readable. The separated lists makes further processing easier.
 
The preprocessing step does several things:
* Split tweets into separate words. This is later used in the processing steps. 
* Lower case all text. This is for ensuring consistency between data.
* Remove punctuations. These are not relevant for the analysis.
* Remove links from messages. Links do not add anything to our analysis thus they are filtered out.

##### Example
```eval_rst
    +-------------------------------------------------------+------------------+
    | Message                                               | Action           |
    +============+==========================================+==================+
    | Hello World                                           | - hello          |
    |                                                       | - world          |
    +-------------------------------------------------------+------------------+
    | SAMPLE TWEET                                          | - sample         |
    |                                                       | - tweet          |
    +-------------------------------------------------------+------------------+
    | The weather is nice, isn't it? https://theweather.com | - the            |
    |                                                       | - weather        |
    |                                                       | - is             |
    |                                                       | - nice           |
    |                                                       | - isn't          |
    |                                                       | - it             |
    +-------------------------------------------------------+------------------+
```
### Process

In this step actual analysis is done. This is essentially the bread and butter of SMUG. All the other steps are there to support this step. The results of this step are what actually provide value to the system. 

This queue sends messages to multiple different analysis workers. This is done through a process exchange. This exchange routes messages to each of the enabled workers. By enabling routes in the exchange different analysis will be conducted.

There are several use cases for this type of queue below are a few examples.

* [Word vectoring](https://en.wikipedia.org/wiki/Word_embedding)
* [Location prediction](https://gab41.lab41.org/2-highly-effective-ways-to-estimate-user-location-in-social-media-65eb1e2d8482)
* [Age prediction](https://www.linkedin.com/pulse/machine-learning-based-age-gender-predictions-image-erandi-ganepola/)
* [Sentiment analysis](https://en.wikipedia.org/wiki/Sentiment_analysis)

### Save
In this step the data is saved to an external provider. In the case of SMUG this is a mongoDB database. In this database all finished analysis are stored. Multiple queues can send a message to this queue. Multiple analysis of the same message are combined and saved into a single database record. 

## Real world usage

```eval_rst
.. blockdiag::

   blockdiag {
        twitter_data [label = "Streaming\nTwitter data", style = "dashed", shape = "flowchart.input"];
        clean [label = "Clean"];
        preprocessing [label = "Preprocess"];
        processing_exchange [label = "Process Exchange", shape = "roundedbox"];
        word_vectoring [label = "Word Vectoring\n(Process)"];
        location_prediction [label = "Location Prediction\n(Process)"];
        age_prediction [label = "Age Prediction\n(Process)"];
        save [label = "Save"];
        mongo_db [label = "MongoDB", style = "dashed", shape = "flowchart.database"];
       
        twitter_data -> clean -> preprocessing -> processing_exchange -> word_vectoring -> save -> mongo_db;
        processing_exchange -> location_prediction -> save;
        processing_exchange -> age_prediction -> save;
        
        group {
            processing_exchange; word_vectoring; location_prediction; age_prediction;
            label = "Process"
            color = "#FF0000";
            shape = line;
            style = dotted;
        }
   }
```

In the above example data is inserted from a twitter data stream into SMUG. The data is then inserted into SMUG. The predictions run through the process to various workers. After the predictions are done they can be sent to the save queue. This queue saves analysis to a mongoDB database.