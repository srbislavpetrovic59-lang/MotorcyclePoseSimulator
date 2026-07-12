# geometry.py
from mediapipe.tasks.python.components.containers import NormalizedLandmark
import math


class Geometry:
    @staticmethod
    def angle(a, b, c):

        ab = (a.x - b.x, a.y - b.y)
        cb = (c.x - b.x, c.y - b.y)

        dot = ab[0]*cb[0] + ab[1]*cb[1]

        mag1 = math.hypot(*ab)
        mag2 = math.hypot(*cb)

        if mag1 == 0 or mag2 == 0:
            return 0

        cos_angle = dot / (mag1 * mag2)

        cos_angle = max(-1, min(1, cos_angle))

        return math.degrees(math.acos(cos_angle))

    @staticmethod
    def distance(p1, p2):
        return math.hypot(
            p2.x - p1.x,
            p2.y - p1.y
        )

    @staticmethod
    def midpoint(p1, p2):
        return (
            (p1.x + p2.x) / 2,
            (p1.y + p2.y) / 2
        )

    @staticmethod
    def vector(p1, p2):
        return (
            p2.x - p1.x,
            p2.y - p1.y
        )

    @staticmethod
    def length(v):
        return math.hypot(v[0], v[1])