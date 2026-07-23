from pose.output.output import Output


class ConsoleOutput(Output):
    def present(self, narration: str) -> None:
        if narration is None:
            raise ValueError("narration must not be None")

        print(narration)