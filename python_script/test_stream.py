import time
import json
import pytest

# pip install binance-connector
from binance.websocket.spot.websocket_stream import SpotWebsocketStreamClient

@pytest.fixture(scope="session")
def stream_messages():
    """
    Start a connection to websocket stream.
    Return stream messages (formatted and raw) in lists to test.
    """
    messages = []
    raw_messages = []
    def process_message(_, message):
        raw_messages.append(message)
        messages.append(json.loads(message))

    stream = SpotWebsocketStreamClient(on_message=process_message)
    stream.trade(symbol="btcusdt")
    time.sleep(1.5)
    stream.stop()
    return messages, raw_messages

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
        "Ignore"
    ]

EXPECTED_ITEMS_COUNT = 11
EXPECTED_DICT = dict
EXPECTED_STR = str

def test_first_message(stream_messages):
    messages, _ = stream_messages
    assert type(messages[0]) == EXPECTED_DICT
    assert len(messages[0]) == 2

def test_remaining_messages(stream_messages):
    messages, _ = stream_messages
    assert len(messages) > 1

    for msg in messages[1:]:
        assert type(msg) == EXPECTED_DICT
        assert len(msg) == EXPECTED_ITEMS_COUNT

def test_renaming_keys(new_keys, stream_messages):
    messages, _ = stream_messages
    expected_keys = new_keys
    assert len(messages) > 1

    # Excluding the first one, it is irrelevant.
    for msg in messages[1:]:
        expected_values = str(msg.values())
        zipped_dict = dict(zip(new_keys, msg.values()))

        assert len(zipped_dict) == EXPECTED_ITEMS_COUNT
        assert list(zipped_dict.keys()) == expected_keys
        assert str(zipped_dict.values()) == expected_values

def test_raw_message(stream_messages):
    _, raw_messages = stream_messages
    for msg in raw_messages:
        assert type(msg) == EXPECTED_STR
