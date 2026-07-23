from abc import ABC, abstractmethod


class Output(ABC):
    @abstractmethod
    def present(self, narration: str) -> None:
        """Present narration to the user."""
        raise NotImplementedError