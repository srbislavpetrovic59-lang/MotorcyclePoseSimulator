from pose.models.pose_evaluation import PoseEvaluation


class PoseEvaluator:

    def evaluate(self, metrics):

        score = 100

        feedback = []

        if metrics["left_arm_extended"]:
            score -= 5
            feedback.append(
                "Relax your left arm."
            )

        return PoseEvaluation(
            score=score,
            rider_state="GOOD",
            feedback=feedback,
        )