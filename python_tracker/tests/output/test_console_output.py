import pytest

from pose.output.console_output import ConsoleOutput


def test_present_prints_narration(capsys):
    output = ConsoleOutput()

    output.present("Hello")

    captured = capsys.readouterr()

    assert captured.out == "Hello\n"


def test_present_raises_for_none():
    output = ConsoleOutput()

    with pytest.raises(ValueError):
        output.present(None)


def test_present_accepts_empty_string(capsys):
    output = ConsoleOutput()

    output.present("")

    captured = capsys.readouterr()

    assert captured.out == "\n"