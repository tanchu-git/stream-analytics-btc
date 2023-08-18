# Mini Project with Azure Stream Analytics
Exploring and learning Azure Event Hubs and Azure Stream Analytics. Where I try to use Stream Analytics to analyze Bitcoin trading stream from Binance in real-time for anomalies.

## Python script
Binance offers a simple WebSocket API for real-time trading data. I did some light processing on the raw streaming data before sending it to Azure Event Hubs. Detailed comments in [```python_script```](https://github.com/tanchu-git/stream_analytics_btc/blob/main/python_script/btc_stream.py).

With the app registration process in Azure Active Directory, I registered a new application service principal object. The identity (```tenant ID```, ```client ID``` and ```client secret```) of the ```Service Principal``` is then stored as environment variables to be accessed by the python script for authentication with Azure services.

![Screenshot 2023-08-09 183221](https://github.com/tanchu-git/stream_analytics_btc/assets/139019601/921b116a-cbc0-4234-bb3b-fa5fc353c6e5)

## Create Event Hubs namespace
I will ingest events from the python script into Azure Event Hubs. Basic tier is sufficient for my purpose.

![Screenshot 2023-08-09 182328](https://github.com/tanchu-git/stream_analytics_btc/assets/139019601/8c4fa629-0498-43e3-9097-2049e2d7286b)

Once the namespace has been created, a Event Hubs instance needs to be created through the left hand navigation panel.

![Screenshot 2023-08-09 194056](https://github.com/tanchu-git/stream_analytics_btc/assets/139019601/1c953cdc-b6fa-4b21-b85a-99e37e63be3c)

## Create Stream Analytics job
Stream Analytics job will be processing the data. Streaming Units (SU) refers to the compute (CPU and memory), minimum amount for me. 

![Screenshot 2023-08-09 202445](https://github.com/tanchu-git/stream_analytics_btc/assets/139019601/f292e78e-5c42-4e13-b21b-91796ee4f471)

## Configuring our setup
Managed identities from Azure Active Directory allows the different services to connect. Azure role-based access is the authorization system to manage access to Azure resources to a particular scope.

Assigning ```python_app``` as ```Azure Event Hubs Data Sender``` in Event Hubs namespace.

![Screenshot 2023-08-09 183543](https://github.com/tanchu-git/stream_analytics_btc/assets/139019601/c521339e-02d6-4a18-b4f7-0c65bea65e8b)

My python script can now stream data into any Event Hubs instances created within the namespace. I can limit the scope to specific Event Hub instances.

Assigning my Stream Analytics job ```event_hub_stream``` as ```Azure Event Hubs Data Receiver``` in the specific Event Hub instance

![Screenshot 2023-08-09 184145](https://github.com/tanchu-git/stream_analytics_btc/assets/139019601/a719a059-2187-47b7-b851-47f9009b8bf0)

My Stream Analytics job can now receive the streaming data from my Event Hub instance. The flow of the data:

```python script --> Event Hubs instance --> Stream Analytics job --> output```

## Configuring Stream Analytics job
1. Add Input - streaming data from Event Hub instance
2. Define Query - processing of data stream with Stream Analytics Query Language, a subset of T-SQL syntax
3. Add Output - where the processed data goes
4. Grant the necessary access as you add input/outputs. Start Stream Analytics Job

![Screenshot 2023-08-09 233103](https://github.com/tanchu-git/stream_analytics_btc/assets/139019601/5b8619eb-c195-43e7-92b8-201c882b1f23)

Main focus for the [query](https://github.com/tanchu-git/stream_analytics_btc/blob/main/stream_query/query.sql) is ```AnomalyDetection_SpikeAndDip```. As the name suggest, it detects temporary anomalies in a time series event. The underlying machine learning model uses the adaptive kernel density estimation algorithm. It supports unsupervised learning and real time scoring, whereby it will learn from the data. More details is in [```stream_query```](https://github.com/tanchu-git/stream_analytics_btc/blob/main/stream_query/query.sql).

### Let's go through the different CTEs in the query -

#### Raw stream data from python_app
![Screenshot 2023-08-09 231218](https://github.com/tanchu-git/stream_analytics_btc/assets/139019601/66a1c5bd-762b-4328-a56b-8b779813069e)

#### CTE with ```TUMBLINGWINDOW``` of 1 second
![Screenshot 2023-08-11 135757](https://github.com/tanchu-git/stream_analytics_btc/assets/139019601/cea2c3c8-728c-4530-bcf8-167ea491316a)
![Screenshot 2023-08-09 231312](https://github.com/tanchu-git/stream_analytics_btc/assets/139019601/a68e5498-20bb-4ee3-a885-4a2a825ff772)

#### CTE with machine learning model applied
![Screenshot 2023-08-11 135825](https://github.com/tanchu-git/stream_analytics_btc/assets/139019601/7bcbc5cc-67f0-4d4b-8921-7558139a931c)
![Screenshot 2023-08-09 231454](https://github.com/tanchu-git/stream_analytics_btc/assets/139019601/f22dbb13-6e45-44b6-9a60-92bbc7345141)

#### CTE with flattened nested record
![Screenshot 2023-08-11 135837](https://github.com/tanchu-git/stream_analytics_btc/assets/139019601/497ff9de-494c-4f44-a97b-efce53435852)
![Screenshot 2023-08-09 231542](https://github.com/tanchu-git/stream_analytics_btc/assets/139019601/6bbcc052-564f-4e51-bbe4-8581428f8bd7)

#### Final ```SELECT``` with ```MATCH_RECOGNIZE``` clause
![Screenshot 2023-08-09 232834](https://github.com/tanchu-git/stream_analytics_btc/assets/139019601/e578c38e-fd09-4162-8b99-bbc0b46d60e5)

As fun as the whole [query](https://github.com/tanchu-git/stream_analytics_btc/blob/main/stream_query/query.sql) was to write, ```AnomalyDetection_SpikeAndDip``` is clearly not suitable for analyzing trading price movements.

## Azure Data Factory
As the raw stream data goes directly into a specified Azure SQL Database, I should at least make something useful out of it. Like a daily historical trading table using Data Factory.

I will need to extract and transform one day's worth of data from the raw stream. First is a pipeline with a ```COPY``` activity and the necessary linked service and source/sink datasets. Then, two parameters (```windowStart``` and ```windowEnd```). The parameters will define the boundaries of a time window, in this case, 24 hours. With this window matched against the source table's ```DATETIME``` column ```EventEnqueuedUtcTime```, only records within the time window will be copied over to a staging storage.

![Screenshot 2023-08-16 182958](https://github.com/tanchu-git/stream_analytics_btc/assets/139019601/eabd67bb-8ce1-4c08-a4d9-ddaed9e2bb09)

Manual input of the time values into the parameters is inefficient, so I will make use of a Scheduled Trigger and pass the scheduled time as the value for the parameters. By scheduling the pipeline to run every day at 23:59 - ```windowEnd``` will use this scheduled time as its value, and ```windowStart``` will get its value by substracting 24 hours from the scheduled time.

![Screenshot 2023-08-16 182608](https://github.com/tanchu-git/stream_analytics_btc/assets/139019601/c4d31e67-8185-4c36-aaa9-687e20d3cfe5)

With the incremental load done, I can now design the Data Flow. 

![Screenshot 2023-08-16 203900](https://github.com/tanchu-git/stream_analytics_btc/assets/139019601/696a4068-eb7c-40dc-93a2-ff4140cd0853)

Everyday at midnight, a new row will be added to the historical table.

![Screenshot 2023-08-16 202835](https://github.com/tanchu-git/stream_analytics_btc/assets/139019601/1bfce196-f728-42e4-8f07-cb489f835a91)

P.S. Query result above isn't fully representative of the trading data (streaming data for 24 hours and more is quite expensive). :blush:
