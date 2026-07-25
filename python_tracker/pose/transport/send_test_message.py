import json
from pose.transport.websocket_server import WebSocketServer

message = {
    "left_elbow": 90.0,
    "right_elbow": 95.0,
    "left_knee": 108.0,
    "right_knee": 110.0,
    "torso_angle": 88.5,
    "pose_confidence": 0.98,
}

server = WebSocketServer()
server.start()
server.send(json.dumps(message))