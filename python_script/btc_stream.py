import os
import time
import json

from azure.identity import DefaultAzureCredential
from azure.eventhub import EventHubProducerClient, EventData
from binance.websocket.spot.websocket_stream import SpotWebsocketStreamClient

''' 
Making this script asynchronous would be the better choice, so the I/O doesn't get blocked 
when the incoming rate of events is high. But I'm not too concerned with data loss in a demo.
---------------------------------------------------------------------------------------------
Using temporary environment variables to store Service Principal credentials. 
os.environ["AZURE_TENANT_ID"]
os.environ["AZURE_CLIENT_ID"]
os.environ["AZURE_CLIENT_SECRET"]
'''

# Define event hub namespace servicebus and event hub instance to be connected to.
EVENT_HUB_FULLY_QUALIFIED_NAMESPACE = "btc-mini-project.servicebus.windows.net"
EVENT_HUB_NAME = "bitcoin_stream"

# DefaultAzureCredential will look into os.environ for credentials to use.
credential = DefaultAzureCredential()

# Initialize a producer client to send messages to event hub.
# Using stored credentials for authentication.
producer = EventHubProducerClient(
    fully_qualified_namespace = EVENT_HUB_FULLY_QUALIFIED_NAMESPACE,
    eventhub_name = EVENT_HUB_NAME,
    credential = credential
    )

new_keys = ["Type", "Event Time", "Symbol", "Trade ID", "Price", "Quantity",
            "Buyer order ID", "Seller Order ID", "Trade time", "Market Maker", "Ignore"]

# Function to rename dictionary keys. 
# SQL considers uppercase and lowercase letters as duplicates.
def rename_keys(keys, old_dict):
        zipped_dict = dict(zip(keys, old_dict.values()))
        return zipped_dict

# Function to process messages and send them to event hub.
# Convert string message to dictionary. 
def process_message(_, message):
    string_to_dict = json.loads(message)    

    if len(string_to_dict) > 2:
        # Pass dictionary into rename_keys function.
        dict_renamed = rename_keys(new_keys, string_to_dict)        
        event_data_batch = producer.create_batch()
        # Convert dictionary to JSON string. Add to batch and send.
        event_data = EventData(json.dumps(dict_renamed))
        try:
            event_data_batch.add(event_data)
        except ValueError:
            producer.send_batch(event_data_batch)
            event_data_batch = producer.create_batch()
            event_data_batch.add(event_data)
            print("Batch full. FLushed!")
        finally:
            producer.send_batch(event_data_batch)
            print("Data sent.")

# Initialize streaming client and start it. 
def main():
    # Pass message recieved to process_message function.
    stream = SpotWebsocketStreamClient(on_message=process_message) 
    stream.trade(symbol="btcusdt")

    # Leave stream open for * seconds.
    time.sleep(5)

    # Close connections to services.
    stream.stop()
    producer.close()
    credential.close()
    print('Streaming closed.')

if __name__ == "__main__":
     main()
