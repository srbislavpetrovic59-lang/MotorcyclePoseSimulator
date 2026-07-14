from pose.models.pose_evaluation import PoseEvaluation
from pose.models.feedback_item import FeedbackItem

MAX_SCORE = 100

ARM_EXTENSION_PENALTY = 5
ARM_SYMMETRY_PENALTY = 10

BODY_ALIGNMENT_PENALTY = 10
SHOULDER_ALIGNMENT_PENALTY = 10

LEG_SYMMETRY_PENALTY = 10

class PoseEvaluator:

    def evaluate(self, metrics) -> PoseEvaluation:
        current_score = MAX_SCORE
        feedback = []

        current_score = self._evaluate_arms(
            metrics,
            current_score,
            feedback,
        )

        current_score = self._evaluate_body(
            metrics,
            current_score,
            feedback,
        )

        current_score = self._evaluate_legs(
            metrics,
            current_score,
            feedback,
        )

        return PoseEvaluation(
           score=max(current_score, 0),
           rider_state=self._determine_state(current_score),
           feedback=feedback,
        )

    def _evaluate_arms(
        self,
        metrics: dict,
        current_score: int,
        feedback: list[str],
    ) -> int:
        if metrics["left_arm_extended"]:
            current_score -= ARM_EXTENSION_PENALTY
            feedback.append(
                FeedbackItem(
                    message="Relax your left arm.",
                    priority=20,
                )
            )

        if metrics["right_arm_extended"]:
            current_score -= ARM_EXTENSION_PENALTY
            feedback.append(
                FeedbackItem(
                    message="Relax your right arm.",
                    priority=20,
                )
            )

        if metrics["arm_symmetry"] < 90.0:
            current_score -= ARM_SYMMETRY_PENALTY
            feedback.append(
                FeedbackItem(
                    message="Keep both elbows equally bent.",
                    priority=35,
                )
            )

        return current_score

    def _evaluate_body(
        self,
        metrics: dict,
        current_score: int,
        feedback: list[str],
    ) -> int:
        if not metrics["torso_upright"]:
            current_score -= BODY_ALIGNMENT_PENALTY
            feedback.append( 
                FeedbackItem(
                    message="Keepyour back upright.",
                    priority=60,
                )
            )

        if not metrics["shoulders_level"]:
            current_score -= SHOULDER_ALIGNMENT_PENALTY
            feedback.append( 
                FeedbackItem(
                    message="Keep your shoulders level.",
                    priority=50,
                )
            )

        return current_score

    def _evaluate_legs(
        self,
        metrics: dict,
        current_score: int,
        feedback: list[str],
    ) -> int:
        if metrics["leg_symmetry"] < 90.0:
            current_score -= LEG_SYMMETRY_PENALTY
            feedback.append( FeedbackItem(
                    message="Keep both knees equally bent.",
                    priority=30,
            )
        )         

        return current_score

    @staticmethod
    def _determine_state(score: int) -> str:
        if score >= 90:
            return "EXCELLENT"

        if score >= 75:
            return "GOOD"

        if score >= 60:
            return "FAIR"

        return "POOR"