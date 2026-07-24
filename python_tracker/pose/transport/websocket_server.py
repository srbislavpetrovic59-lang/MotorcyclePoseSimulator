from __future__ import annotations

from threading import Event, Lock, Thread
from typing import Optional

from websockets.exceptions import ConnectionClosed
from websockets.sync.server import ServerConnection, serve


class WebSocketServer:
    def __init__(
        self,
        host: str = "localhost",
        port: int = 8765,
    ) -> None:
        self._host = host
        self._port = port

        self._connection: Optional[ServerConnection] = None
        self._server = None
        self._thread: Optional[Thread] = None

        self._connection_lock = Lock()
        self._client_connected = Event()

    def start(self) -> None:
        if self._thread is not None and self._thread.is_alive():
            return

        self._thread = Thread(
            target=self._run_server,
            name="WebSocketServer",
            daemon=True,
        )
        self._thread.start()

    def stop(self) -> None:
        with self._connection_lock:
            if self._connection is not None:
                self._connection.close()
                self._connection = None

        if self._server is not None:
            self._server.shutdown()
            self._server = None

        self._client_connected.clear()

        if self._thread is not None:
            self._thread.join(timeout=2.0)
            self._thread = None

    def send(self, message: str) -> None:
        with self._connection_lock:
            connection = self._connection

        if connection is None:
            raise RuntimeError(
                "No WebSocket client is connected."
            )

        try:
            connection.send(message)
        except ConnectionClosed as error:
            self._remove_connection(connection)
            raise RuntimeError(
                "WebSocket client connection is closed."
            ) from error

    def wait_for_client(
        self,
        timeout: float | None = None,
    ) -> bool:
        return self._client_connected.wait(timeout)

    @property
    def is_client_connected(self) -> bool:
        return self._client_connected.is_set()

    def _run_server(self) -> None:
        with serve(
            self._handle_client,
            self._host,
            self._port,
        ) as server:
            self._server = server
            print(
                f"WebSocket server listening on "
                f"ws://{self._host}:{self._port}"
            )
            server.serve_forever()

    def _handle_client(
        self,
        connection: ServerConnection,
    ) -> None:
        with self._connection_lock:
            self._connection = connection
            self._client_connected.set()

        print("WebSocket client connected.")

        try:
            for message in connection:
                print(f"Received from client: {message}")
        except ConnectionClosed:
            pass
        finally:
            self._remove_connection(connection)
            print("WebSocket client disconnected.")

    def _remove_connection(
        self,
        connection: ServerConnection,
    ) -> None:
        with self._connection_lock:
            if self._connection is connection:
                self._connection = None
                self._client_connected.clear()