import time
import json
import pytest
import btc_stream
    
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
    time.sleep(2)
    stream.stop()

    return messages, raw_messages

EXPECTED_ITEMS_COUNT = 11
EXPECTED_DICT = dict
EXPECTED_STR = str

def test_rename_keys(stream_messages):
    messages, _ = stream_messages
    expected_keys = btc_stream.new_keys

    # Skip first message.
    for msg in messages[1:]:
        expected_values = str(msg.values())
        renamed = btc_stream.rename_keys(btc_stream.new_keys, msg)

        assert type(renamed) == EXPECTED_DICT
        assert len(renamed) == EXPECTED_ITEMS_COUNT
        assert list(renamed.keys()) == expected_keys
        assert str(renamed.values()) == expected_values

def test_first_message(stream_messages):
    messages, _ = stream_messages
    first_message = messages[0]    
    assert type(first_message) == EXPECTED_DICT
    assert len(first_message) == 2

def test_remaining_messages(stream_messages):
    messages, _ = stream_messages
    assert len(messages) > 1

    # Skip first message.
    for msg in messages[1:]:
        assert type(msg) == EXPECTED_DICT
        assert len(msg) == EXPECTED_ITEMS_COUNT

def test_raw_message(stream_messages):
    _, raw_messages = stream_messages
    for msg in raw_messages:
        assert type(msg) == EXPECTED_STR
