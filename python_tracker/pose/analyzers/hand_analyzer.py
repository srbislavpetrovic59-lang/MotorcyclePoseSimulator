from pose.geometry import Geometry
from pose.hand_landmarks import HandLandmark


class HandAnalyzer:

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

        print(
            f"Index ratio: "
            #f"2D={bend_2d}, "
            #f"3D={bend_3d}, "
            f"ratio={index_tip_to_mcp_ratio}"
        )

        return {
            "left_index_finger_bend": bend_2d,
            "left_index_finger_bend_3d": bend_3d,
            "left_index_tip_to_mcp_ratio":
                index_tip_to_mcp_ratio,
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
   