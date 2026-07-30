import numpy as np
from pose.hand_detector import HandDetector


def test_hand_detector_can_be_created_and_closed():

    detector = HandDetector()
    
    try:

        assert detector._hands is not None

    finally:
        
        detector.close()


def test_detect_returns_none_for_empty_frame():

    detector = HandDetector()

    frame = np.zeros((480, 640, 3), dtype=np.uint8)

    result = detector.detect(frame)

    try: 
        assert result is None

    finally:
        
        detector.close()