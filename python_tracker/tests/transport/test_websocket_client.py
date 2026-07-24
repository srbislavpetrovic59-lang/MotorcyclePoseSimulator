import pytest
from unittest.mock import MagicMock

from pose.transport.websocket_client import WebSocketClient


def test_send_raises_when_client_is_not_connected() -> None:
    client = WebSocketClient(
        host="localhost",
        port=8765,
    )

    with pytest.raises(
        RuntimeError,
        match="WebSocket client is not connected.",
    ):
        client.send("Hello")


def test_send_forwards_message_to_connection() -> None:
    client = WebSocketClient(
        host="localhost",
        port=8765,
    )
    connection = MagicMock()
    client._connection = connection

    client.send("Hello")

    connection.send.assert_called_once_with("Hello")