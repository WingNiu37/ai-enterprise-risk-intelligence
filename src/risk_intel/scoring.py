from dataclasses import dataclass


@dataclass(frozen=True)
class ScoreComponents:
    severity: int
    breadth: int
    urgency: int

    def validate(self) -> None:
        for name, value in vars(self).items():
            if not isinstance(value, int) or not 1 <= value <= 5:
                raise ValueError(f"{name} must be an integer from 1 to 5")


def calculate_risk_score(severity: int, breadth: int, urgency: int) -> int:
    """Return an explainable 20-100 prioritization score.

    Severity receives the largest weight because consequence matters most.
    Breadth captures how widely the event can spread. Urgency captures how
    quickly an analyst should respond. Model confidence is deliberately kept
    separate because uncertainty is not the same thing as impact.
    """
    components = ScoreComponents(severity, breadth, urgency)
    components.validate()
    weighted_average = 0.5 * severity + 0.3 * breadth + 0.2 * urgency
    return round(20 * weighted_average)
