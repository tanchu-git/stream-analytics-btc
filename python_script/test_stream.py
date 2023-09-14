import time
import json
import pytest
import btc_stream

@pytest.fixture(scope="session")
def stream_message():
    return ('{"e":"trade","E":1694726183301,"s":"BTCUSDT","t":3212504520,"p":"26596.52000000",'
            '"q":"0.00380000","b":22343123975,"a":22343123438,"T":1694726183301,"m":false,"M":true}')

EXPECTED_ITEMS_COUNT = 11
EXPECTED_DICT = dict
EXPECTED_STR = str

def test_process_message(monkeypatch, stream_message):
    expected_keys = btc_stream.new_keys

    def fake_process_message(on_message):        
        string_to_dict = json.loads(on_message)
        dict_renamed = btc_stream.rename_keys(btc_stream.new_keys, string_to_dict)        
        return dict_renamed

    monkeypatch.setattr(btc_stream, "process_message", fake_process_message)
    test_dict = btc_stream.process_message(stream_message)
    expected_values = str(test_dict.values())

    assert type(stream_message) == EXPECTED_STR
    assert type(test_dict) == EXPECTED_DICT
    assert len(test_dict) == EXPECTED_ITEMS_COUNT
    assert list(test_dict.keys()) == expected_keys
    assert str(test_dict.values()) == expected_values
