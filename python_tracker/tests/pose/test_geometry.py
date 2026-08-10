from types import SimpleNamespace

from pose.geometry import Geometry
from pose.analyzers.hand_analyzer import HandAnalyzer



def test_angle_3d_returns_90_degrees():
    a = SimpleNamespace(x=1.0, y=0.0, z=0.0)
    b = SimpleNamespace(x=0.0, y=0.0, z=0.0)
    c = SimpleNamespace(x=0.0, y=1.0, z=0.0)

    angle = Geometry.angle_3d(a, b, c)

    assert angle == 90.0

def test_angle_3d_returns_zero_for_zero_length_vector():
    a = SimpleNamespace(x=0.0, y=0.0, z=0.0)
    b = SimpleNamespace(x=0.0, y=0.0, z=0.0)
    c = SimpleNamespace(x=1.0, y=0.0, z=0.0)

    angle = Geometry.angle_3d(a, b, c)

    assert angle == 0

def test_index_finger_bend_3d_returns_none_without_hand():
    analyzer = HandAnalyzer()

    assert analyzer._index_finger_bend_3d(None) is None
    