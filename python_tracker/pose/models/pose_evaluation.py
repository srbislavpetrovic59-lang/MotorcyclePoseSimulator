from dataclasses import dataclass


@dataclass
class PoseEvaluation:

    score: int

    rider_state: str

    feedback: list[str]