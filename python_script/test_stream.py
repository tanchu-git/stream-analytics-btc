import json
import pytest
import btc_stream

@pytest.fixture()
def stream_message():
    return ('{"e":"trade","E":1694726183301,"s":"BTCUSDT","t":3212504520,"p":"26596.52000000",'
            '"q":"0.00380000","b":22343123975,"a":22343123438,"T":1694726183301,"m":false,"M":true}')

# Variables and 'pytest_generate_tests' function for parametrization.
first_message = '{"result":null,"id":1694784292276}'
second_message = ('{"e":"trade","E":1694726183301,"s":"BTCUSDT","t":3212504520,"p":"26596.52000000",'
                  '"q":"0.00380000","b":22343123975,"a":22343123438,"T":1694726183301,"m":false,"M":true}')

def pytest_generate_tests(metafunc):
    if "messages" in metafunc.fixturenames:
        metafunc.parametrize("messages", [first_message, second_message])

EXPECTED_ITEMS_COUNT = 11
EXPECTED_DICT = dict
EXPECTED_STR = str

def test_process_message(monkeypatch, stream_message):
    throw_away = ""
    
    def fake_process_message(_, on_message):        
        string_to_dict = json.loads(on_message)
        dict_renamed = btc_stream.rename_keys(btc_stream.new_keys, string_to_dict)        
        return dict_renamed

    monkeypatch.setattr(btc_stream, "process_message", fake_process_message)
    test_dict = btc_stream.process_message(throw_away, stream_message)

    expected_keys = btc_stream.new_keys
    expected_values = str(test_dict.values())

    assert type(stream_message) == EXPECTED_STR
    assert type(test_dict) == EXPECTED_DICT
    assert len(test_dict) == EXPECTED_ITEMS_COUNT
    assert list(test_dict.keys()) == expected_keys
    assert str(test_dict.values()) == expected_values

# Parametrization test with pytest_generate_tests.
def test_process_message_with_parametrization(monkeypatch, messages):
    throw_away = ""

    def fake_process_message(_, on_message):        
        string_to_dict = json.loads(on_message)

        if len(string_to_dict) > 2:
            dict_renamed = btc_stream.rename_keys(btc_stream.new_keys, string_to_dict)      
            return dict_renamed

    monkeypatch.setattr(btc_stream, "process_message", fake_process_message)
    test_dict = btc_stream.process_message(throw_away, messages)

    if test_dict is not None:
        expected_keys = btc_stream.new_keys
        expected_values = str(test_dict.values())

        assert type(messages) == EXPECTED_STR
        assert type(test_dict) == EXPECTED_DICT
        assert len(test_dict) == EXPECTED_ITEMS_COUNT
        assert list(test_dict.keys()) == expected_keys
        assert str(test_dict.values()) == expected_values
    else:
        assert test_dict is None
