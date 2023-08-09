# stream_analytics_btc
Mini project with Azure Event Hubs and Azure Stream Analytics.

## Python script
Binance offers a simple WebSocket API for real-time trading data. I did some light processing on the raw streaming data before sending it to Azure Event Hubs. Detailed comments in [python_script](https://github.com/tanchu-git/stream_analytics_btc/blob/main/python_script/btc_stream.py).

With the app registration process in Azure Active Directory, I registered a new application service principal object. The identity (tenant ID, client ID, client secret) of the service principal is then stored as environment variables to be accessed by the python script for authentication with Azure services.

![Screenshot 2023-08-09 183221](https://github.com/tanchu-git/stream_analytics_btc/assets/139019601/921b116a-cbc0-4234-bb3b-fa5fc353c6e5)

## Create Event Hubs namespace
Basic tier is sufficient for my purpose.

![Screenshot 2023-08-09 182328](https://github.com/tanchu-git/stream_analytics_btc/assets/139019601/8c4fa629-0498-43e3-9097-2049e2d7286b)

Once the namespace has been created, a Event Hubs instance needs to be created through the left hand navigation panel.

![Screenshot 2023-08-09 194056](https://github.com/tanchu-git/stream_analytics_btc/assets/139019601/1c953cdc-b6fa-4b21-b85a-99e37e63be3c)

## Create Stream Analytics job
Create a Stream Analytics job through Azure portal. Streaming Units (SU) refers to the compute (CPU and memory), minimum amount for me. 

![Screenshot 2023-08-09 202445](https://github.com/tanchu-git/stream_analytics_btc/assets/139019601/f292e78e-5c42-4e13-b21b-91796ee4f471)

## Configuring our setup
Managed identities from Azure Active Directory allows the different services to connect. Azure role-based access is the authorization system to manage access to Azure resources to a particular scope.

#### Assigning python_app as 'Azure Event Hubs Data Sender' in Event Hubs namespace.

![Screenshot 2023-08-09 183543](https://github.com/tanchu-git/stream_analytics_btc/assets/139019601/c521339e-02d6-4a18-b4f7-0c65bea65e8b)

My python script can now stream data into any Event Hubs instances created within the namespace. I can limit the scope to specific Event Hub instances.

#### Assigning my Stream Analytics job event_hub_stream as 'Azure Event Hubs Data Receiver' in the specific Event Hub instance

![Screenshot 2023-08-09 184145](https://github.com/tanchu-git/stream_analytics_btc/assets/139019601/a719a059-2187-47b7-b851-47f9009b8bf0)

My Stream Analytics job can now receive the streaming data. The flow of the data: Binance WebSocket API --> python script --> Event Hub instance --> Stream Analytics job

## Configuring Stream Analytics job
1. Add Input - streaming data from Event Hub instance
2. Define Query - processing of data stream with Stream Analytics Query Language, a subset of T-SQL syntax
3. Add Output - where the processed data goes
4. Grant the necessary access as you add input/outputs. Start Stream Analytics Job

![Screenshot 2023-08-09 233103](https://github.com/tanchu-git/stream_analytics_btc/assets/139019601/5b8619eb-c195-43e7-92b8-201c882b1f23)

Main focus for the [query](https://github.com/tanchu-git/stream_analytics_btc/blob/main/stream_query/query.sql) is 'AnomalyDetection_SpikeAndDip'. As the name suggest, it detects temporary anomalies in a time series event. The underlying machine learning model uses the adaptive kernel density estimation algorithm. It supports unsupervised learning and real time scoring, whereby it will learn from the data. More details is in [stream_query](https://github.com/tanchu-git/stream_analytics_btc/blob/main/stream_query/query.sql).

Let's go through the query results part by part-

#### Raw stream data from python_app
![Screenshot 2023-08-09 231218](https://github.com/tanchu-git/stream_analytics_btc/assets/139019601/66a1c5bd-762b-4328-a56b-8b779813069e)

#### CTE with TUMBLINGWINDOW of 1 second
![Screenshot 2023-08-09 231312](https://github.com/tanchu-git/stream_analytics_btc/assets/139019601/893a7733-ddec-40f2-ab7e-4136db0f0013)

#### CTE with machine learning model applied
![Screenshot 2023-08-09 231454](https://github.com/tanchu-git/stream_analytics_btc/assets/139019601/47160e9c-ffff-4e6d-ae50-c2c9afe4a088)

#### CTE with flattened nested record
![Screenshot 2023-08-09 231542](https://github.com/tanchu-git/stream_analytics_btc/assets/139019601/512e3d4b-b551-4c16-8ed0-f714f49ad373)

#### Final result
![Screenshot 2023-08-09 232834](https://github.com/tanchu-git/stream_analytics_btc/assets/139019601/e578c38e-fd09-4162-8b99-bbc0b46d60e5)

As fun as the query was to write, it's utterly useless. Let's just blame it on bitcoin being too stable.
