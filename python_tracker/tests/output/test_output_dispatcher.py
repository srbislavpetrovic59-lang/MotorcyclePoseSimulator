from pose.output.output import Output
from pose.output.output_dispatcher import OutputDispatcher
import pytest


class FakeOutput(Output):
    def __init__(self):
        self.messages = []

    def present(self, narration: str) -> None:
        self.messages.append(narration)


def test_dispatch_routes_narration_to_all_outputs():
    fake = FakeOutput()
    dispatcher = OutputDispatcher([fake])

    dispatcher.dispatch("Hello")

    assert fake.messages == ["Hello"]

def test_dispatch_raises_for_none_narration():
    fake = FakeOutput()
    dispatcher = OutputDispatcher([fake])

    with pytest.raises(ValueError):
        dispatcher.dispatch(None)

def test_constructor_raises_for_none_outputs():
    with pytest.raises(ValueError):
        OutputDispatcher(None)


def test_constructor_raises_for_empty_outputs():
    with pytest.raises(ValueError):
        OutputDispatcher([])