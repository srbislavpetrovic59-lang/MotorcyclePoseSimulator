import json

from pose.output.output import Output
from pose.transport.websocket_client import WebSocketClient


class UnrealOutput(Output):
    """Presents narration through the Unreal communication channel."""

    def __init__(
        self,
        client: WebSocketClient,
    ) -> None:
        self._client = client

    def present(
        self,
        narration: str,
    ) -> None:
        message = self._build_message(narration)
        self._client.send(message)

    @staticmethod
    def _build_message(
        narration: str,
    ) -> str:
        payload = {
            "type": "pose_feedback",
            "message": narration,
            "severity": "normal",
        }

        return json.dumps(payload)