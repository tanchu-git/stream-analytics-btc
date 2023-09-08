import time
import json
import pytest

# pip install binance-connector
from binance.websocket.spot.websocket_stream import SpotWebsocketStreamClient

# Storing event messages (formatted) in lists to test
MESSAGES = []

def process_message(_, message):
    MESSAGES.append(json.loads(message))

@pytest.fixture(scope="module")
def start_stream():
    """
    Return a connection to websocket stream
    """
    stream = SpotWebsocketStreamClient(on_message=process_message)
    stream.trade(symbol="btcusdt")
    time.sleep(2)

    yield stream

    stream.stop()

@pytest.fixture()
def new_keys():
    """
    Return new key names for dictionary
    """
    return [
        "Type",
        "Event Time",
        "Symbol",
        "Trade ID",
        "Price",
        "Quantity",
        "Buyer order ID",
        "Seller Order ID",
        "Trade time",
        "Market Maker",
        "Ignore",
    ]

def test_first_message(start_stream):
    assert type(MESSAGES[0]) == dict
    assert len(MESSAGES[0]) == 2
    assert MESSAGES[0]["result"] is None

def test_second_message(start_stream):
    for msg in MESSAGES[1:]:
        assert type(MESSAGES[1]) == dict
        assert len(MESSAGES[1]) == 11

def test_rename_keys(new_keys, start_stream):
    zipped_dict = dict(zip(new_keys, MESSAGES[1].values()))
    assert len(zipped_dict) == 11
    assert list(zipped_dict.keys()) == new_keys
    assert str(zipped_dict.values()) == str(MESSAGES[1].values())

# Test the first message unformatted
def test_raw_message():
    def msg(_, message):
        global raw_message
        raw_message = message

    stream = SpotWebsocketStreamClient(on_message=msg)
    stream.trade(symbol="btcusdt")
    stream.stop()
    assert len(raw_message) > 11
    assert type(raw_message) == str
