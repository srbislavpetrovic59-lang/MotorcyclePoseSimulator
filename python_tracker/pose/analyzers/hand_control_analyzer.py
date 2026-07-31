# hand_control_analyzer.py

from pose.models.frame_analysis import FrameAnalysis



class HandControlAnalyzer:

    def analyze(self, frame_analysis: FrameAnalysis):
        hand_landmarks = frame_analysis.hand_landmarks

        return {}
     