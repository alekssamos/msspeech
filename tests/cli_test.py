from click.testing import CliRunner
from msspeech.__main__ import main
from mock import AsyncMock
import pytest


def test_help():
    runner = CliRunner()
    result = runner.invoke(main, ['--help'])
    for x in ["Usage:", "-100", "+100", "0.1", "1.0"]:
        assert x in result.output
    assert result.exit_code == 0

def test_error():
    runner = CliRunner()
    result = runner.invoke(main, ['error'])
    assert result.exit_code != 0
    result = runner.invoke(main, ['--pitch', '4', 'error'])
    assert result.exit_code != 0
    result = runner.invoke(main, ['--pitch', '5', 'unknown voice', 'error'])
    assert result.exit_code != 0


@pytest.mark.parametrize("r", [-111, 222, 3, -3])
@pytest.mark.parametrize("p", [-444, 555, 4, -4])
@pytest.mark.parametrize("v", [-777.3, 888.9, 0.1, 0.4, 0.9, 1.0])
def test_call_synthesize_clamp(monkeypatch, r, p, v):
    am = AsyncMock()
    monkeypatch.setattr("msspeech.__main__.a_main", am)
    runner = CliRunner()
    filename = 'test.mp3'
    voice_name = 'Guy'
    text = 'hi!'
    result = runner.invoke(main, ['--filename', filename, '--volume', v, '--rate', r, '--pitch', p, voice_name, text])
    assert result.exit_code == 0
    am.assert_called_once()
    args, kwargs = am.call_args_list[0]
    assert abs(kwargs["rate"]) <= 100
    assert abs(kwargs["pitch"]) <= 100
    assert kwargs["volume"] >= 0.1 <= 1.0
    assert kwargs["voice_name"] == voice_name
    assert kwargs["text"] == text

