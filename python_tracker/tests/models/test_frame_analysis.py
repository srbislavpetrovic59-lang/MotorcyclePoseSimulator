from pose.models.frame_analysis import FrameAnalysis


def test_frame_analysis_stores_landmarks():

    pose_landmarks = object()
    hand_landmarks = object()

    frame_analysis = FrameAnalysis(
        pose_landmarks=pose_landmarks,
        hand_landmarks=hand_landmarks,
    )

    assert frame_analysis.pose_landmarks is pose_landmarks
    assert frame_analysis.hand_landmarks is hand_landmarks