import json
from unittest.mock import MagicMock

from pose.output.unreal_output import UnrealOutput


def test_present_sends_pose_feedback_message() -> None:
    client = MagicMock()
    output = UnrealOutput(client)

    output.present("Relax your shoulders")

    client.send.assert_called_once()

    sent_message = client.send.call_args.args[0]

    assert json.loads(sent_message) == {
        "type": "pose_feedback",
        "message": "Relax your shoulders",
        "severity": "normal",
    }