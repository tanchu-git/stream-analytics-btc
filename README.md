# stream_analytics_btc
Mini project with Azure Event Hubs and Azure Stream Analytics.

## Python script
Binance offers a simple WebSocket API for real-time trading data. I did some light processing on the raw streaming data before sending it to Azure Event Hubs. Detailed comments in the python [script](https://github.com/tanchu-git/stream_analytics_btc/blob/main/btc_stream.py).

With the app registration process in Azure Active Directory, I registered a new application service principal object. The identity (tenant ID, client ID, client secret) of the service principal is then stored as environment variables to be accessed by the python script for authentication with Azure services.

![Screenshot 2023-08-09 183221](https://github.com/tanchu-git/stream_analytics_btc/assets/139019601/3ca9b4b1-74cb-4c58-b519-deb3177603a9)

## Create Event Hubs namespace
Basic tier is sufficient for my purpose.

![Screenshot 2023-08-09 182328](https://github.com/tanchu-git/stream_analytics_btc/assets/139019601/8c4fa629-0498-43e3-9097-2049e2d7286b)

Once the namespace has been created, an event hub instance needs to be created through left hand navigation panel.

![Screenshot 2023-08-09 194056](https://github.com/tanchu-git/stream_analytics_btc/assets/139019601/1c953cdc-b6fa-4b21-b85a-99e37e63be3c)





