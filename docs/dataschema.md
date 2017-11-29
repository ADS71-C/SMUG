# Data Schema

This documents the different data schema's employed by SMUG to save and read processed data.

## smug_reports

The reports collection holds the large scale configurations for the reports. These apply to a broad set of tweets and will contain data specific for a report.

Example
```json
{ 
    "_id" : { 
        "$oid" : "5a1580d5c58878fd9524e954" 
    }, 
    "name" : "Word vectoring", 
    "enabled" : true, 
    "parameters" : [ "ziek", "griep", "verkouden", "verkoudheid", "koorts", "hoofdpijn" ] 
}
```

## smug_messages

This collection holds data to a single specific message. It has 2 main fields

### Metadata

Tracks data related to a tweet such as 

- Source
- Dataset
- Language
- rated words
- Links

### Reports

Tracks the result of analyses on the dataset. This is an array of reports. These fields are not certain as report properties can be toggled at the report level. Thus a report can be vector-scored by not location analysed. All items in this dataset have a reference to the report id.

```json
{ 
  "_id" : { 
    "$oid" : "5a1580dac58878fd9524e96b" 
  }, 
  "metadata" : { 
    "date" : { 
      "$date" : "2017-01-01T16:00:00.090+0000" 
    }, 
    "url" : { 
      "$numberLong" : "815573292006379520" 
     }, 
     "type" : "post", 
     "source" : "twitter", 
     "source_import" : "twinl", 
     "lang" : "nl_NL.UTF-8", 
     "message_words" : [ "oeps", "kleine", "wereld" ] 
   }, 
   "author" : "8077b14c8aa0c80f6d9bb615", 
   "message" : "@b89221b0706cf91a3e6d7532 oeps kleine wereld...", 
   "reports" : [ 
    { "id" : "5a1580d5c58878fd9524e954", "score" : 0.12757538982134464, "scored_words" : [ "oeps", "kleine", "wereld" ] } 
   ] 
  }

```