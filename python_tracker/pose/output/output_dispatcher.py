from collections.abc import Iterable

from pose.output.output import Output


class OutputDispatcher:
    def __init__(self, outputs: Iterable[Output]) -> None:
        if outputs is None:
            raise ValueError("outputs must not be None")

        self._outputs = tuple(outputs)
        if not self._outputs:
            raise ValueError("outputs must not be empty")


    def dispatch(self, narration: str) -> None:
        if narration is None:
            raise ValueError("narration must not be None")

        for output in self._outputs:
            output.present(narration)
    
    