import time
import json
import pytest

# pip install binance-connector
from binance.websocket.spot.websocket_stream import SpotWebsocketStreamClient

# Storing stream messages (formatted) in lists to test.
MESSAGES = []

def process_message(_, message):
    MESSAGES.append(json.loads(message))

@pytest.fixture(scope="module")
def start_stream():
    """
    Return a connection to websocket stream.
    """
    stream = SpotWebsocketStreamClient(on_message=process_message)
    stream.trade(symbol="btcusdt")
    time.sleep(2)

    yield stream

    stream.stop()

@pytest.fixture()
def new_keys():
    """
    Return new key names for dictionary.
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

def test_remaining_messages(start_stream):
    for msg in MESSAGES[1:]:
        assert type(msg) == dict
        assert len(msg) == 11

def test_renaming_keys(new_keys, start_stream):
    # Excluding the first one, it is irrelevant.
    for msg in MESSAGES[1:]:
        zipped_dict = dict(zip(new_keys, msg.values()))
        assert len(zipped_dict) == 11
        assert list(zipped_dict.keys()) == new_keys
        assert str(zipped_dict.values()) == str(msg.values())

# Test the first message unformatted.
def test_raw_message():
    def msg(_, message):
        global raw_message
        raw_message = message

    stream = SpotWebsocketStreamClient(on_message=msg)
    stream.trade(symbol="btcusdt")
    stream.stop()
    assert len(raw_message) > 11
    assert type(raw_message) == str
