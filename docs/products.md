# Products

These are the products contained within SMUG and SNOB

```eval_rst
.. blockdiag::

    blockdiag {
      queues [label="Task Queues"];
      handlers [label="Message handlers"];
      importers [label="Importers"];
      api [label="Web API"];
      frontend [label="ReactJS dashboard"];
      database [label="Database"];
      twitter [label="Twitter Direct"];
      twinl [label="TwinL"];
    
      group {
        label="SNOB";
        color="green";
        api <-> frontend;
        frontend;
        api
      }
    
      group {
        color="yellow";
        label="SMUG";
    
       importers -> queues;
       queues -> database;
       queues <-> handlers;
      }
    
      group {
       label="Data";
       color="red";
       twitter;
       twinl;
      }
    
      database <-> api;
    
      twitter -> importers;
      twinl -> importers;  
    }
```