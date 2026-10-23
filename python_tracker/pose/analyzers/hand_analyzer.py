from pose.geometry import Geometry
from pose.hand_landmarks import HandLandmark
from pose.analyzers.index_angle_filter import IndexAngleFilter


class HandAnalyzer:

    def __init__(self):
        self._left_index_angle_filter = IndexAngleFilter(window_size=5)
    
    def analyze(
        self,
        hands,
    ) -> dict:
        left_hand = hands.get("Left")

        bend_2d = self._index_finger_bend(left_hand)
        bend_3d = self._index_finger_bend_3d(left_hand)
        
        index_tip_to_mcp_ratio = (
            self._index_tip_to_mcp_ratio(
                left_hand,
            )
        )
        right_hand = hands.get("Right")
        right_index_finger_bend = self._index_finger_bend(
            right_hand
        )

        ratio_3d = self._index_tip_to_mcp_ratio_3d(left_hand)
        index_depth = self._index_tip_relative_depth(left_hand)
        '''print(
            f"INDEX: "
            f"2D={bend_2d} | "
            f"3D={bend_3d} | "
            f"RATIO_2D={index_tip_to_mcp_ratio} | "
            f"RATIO_3D={ratio_3d}"
            f"DEPTH={index_depth}"
        )'''
 
        filtered_bend_2d = self._left_index_angle_filter.update(
            bend_2d
        )

        return {
            "left_index_finger_bend": filtered_bend_2d,
            "left_index_finger_bend_3d": bend_3d,
            "left_index_tip_to_mcp_ratio":
                index_tip_to_mcp_ratio,
            "right_index_finger_bend":
                right_index_finger_bend,
        }
       

    def _index_finger_bend(
        self,
        hand,
    ) -> float | None:
        index_mcp = self._get_landmark(
            hand,
            HandLandmark.INDEX_FINGER_MCP,
        )

        index_pip = self._get_landmark(
            hand,
            HandLandmark.INDEX_FINGER_PIP,
        )

        index_tip = self._get_landmark(
            hand,
            HandLandmark.INDEX_FINGER_TIP,
        )

        if (
            index_mcp is None
            or index_pip is None
            or index_tip is None
        ):
            return None

        return Geometry.angle(
            index_mcp,
            index_pip,
            index_tip,
        )   

    def _get_landmark(
        self,
        hand,
        landmark,
    ):
        if hand is None:
            return None

        return hand.landmark[landmark]

    def _index_finger_bend_3d(
        self,
        hand,
    ) -> float | None:
            index_mcp = self._get_landmark(
                hand,
                HandLandmark.INDEX_FINGER_MCP,
            )

            index_pip = self._get_landmark(
                hand,
                HandLandmark.INDEX_FINGER_PIP,
            )

            index_tip = self._get_landmark(
                hand,
                HandLandmark.INDEX_FINGER_TIP,
            )

            if (
                index_mcp is None
                or index_pip is None
                or index_tip is None
            ):
                return None

            return Geometry.angle_3d(
                index_mcp,
                index_pip,
                index_tip,
            )

    def _index_tip_to_mcp_ratio(
        self,
        hand,
    ) -> float | None:
        index_tip = self._get_landmark(
            hand,
            HandLandmark.INDEX_FINGER_TIP,
        )

        index_mcp = self._get_landmark(
            hand,
            HandLandmark.INDEX_FINGER_MCP,
        )

        wrist = self._get_landmark(
            hand,
            HandLandmark.WRIST,
        )

        middle_mcp = self._get_landmark(
            hand,
            HandLandmark.MIDDLE_FINGER_MCP,
        )

        if (
            index_tip is None
            or index_mcp is None
            or wrist is None
            or middle_mcp is None
        ):
            return None

        finger_distance = Geometry.distance(
            index_tip,
            index_mcp,
        )

        hand_scale = Geometry.distance(
            wrist,
            middle_mcp,
        )

        if hand_scale == 0:
            return None

        return finger_distance / hand_scale

    def _right_index_finger_bend(
        self,
        hand,
    ) -> float | None:
        return self._index_finger_bend(
            hand
        )

    def _index_tip_to_mcp_ratio_3d(
        self,
        hand,
    ) -> float | None:
        index_tip = self._get_landmark(
            hand,
            HandLandmark.INDEX_FINGER_TIP,
        )
        index_mcp = self._get_landmark(
            hand,
            HandLandmark.INDEX_FINGER_MCP,
        )
        wrist = self._get_landmark(
            hand,
            HandLandmark.WRIST,
        )
        middle_mcp = self._get_landmark(
            hand,
            HandLandmark.MIDDLE_FINGER_MCP,
        )

        if any(
            point is None
            for point in (
                index_tip,
                index_mcp,
                wrist,
                middle_mcp,
            )
        ):
            return None

        finger_distance = Geometry.distance_3d(
            index_tip,
            index_mcp,
        )
        hand_scale = Geometry.distance_3d(
            wrist,
            middle_mcp,
        )

        if hand_scale <= 1e-6:
            return None

        return finger_distance / hand_scale

    def _index_tip_relative_depth(self, hand) -> float | None:
        index_tip = self._get_landmark(
            hand, HandLandmark.INDEX_FINGER_TIP
        )
        index_mcp = self._get_landmark(
            hand, HandLandmark.INDEX_FINGER_MCP
        )

        if index_tip is None or index_mcp is None:
            return None

        return index_tip.z - index_mcp.z
   