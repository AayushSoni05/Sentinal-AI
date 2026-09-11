from dataclasses import dataclass


@dataclass(frozen=True)
class CRIComponent:
    """
    One source contribution to the Consensus Risk Index.

    score must be normalized to 0.0-1.0.
    weight must be normalized to 0.0-1.0.
    """

    source_name: str
    score: float
    weight: float


def calculate_cri(
    components: list[CRIComponent],
) -> float:
    """
    Calculate the Consensus Risk Index using:

        CRI = [1 - Π(1 - (S_i × W_i))] × 100
    """

    validate_cri_components(components)

    if not components:
        return 0.0

    probability_of_no_signal = 1.0

    for component in components:
        probability_of_no_signal *= (
            1.0 - (component.score * component.weight)
        )

    cri = (1.0 - probability_of_no_signal) * 100.0

    return round(cri, 6)
def validate_cri_components(
    components: list[CRIComponent],
) -> None:
    """
    Validate CRI inputs before calculation.
    """

    source_names = [
        component.source_name
        for component in components
    ]

    if len(source_names) != len(set(source_names)):
        raise ValueError(
            "Duplicate source names are not allowed in CRI components."
        )

    for component in components:
        if not component.source_name.strip():
            raise ValueError(
                "CRI component source_name cannot be empty."
            )

        if not 0.0 <= component.score <= 1.0:
            raise ValueError(
                f"CRI score for {component.source_name} "
                "must be between 0.0 and 1.0."
            )

        if not 0.0 <= component.weight <= 1.0:
            raise ValueError(
                f"CRI weight for {component.source_name} "
                "must be between 0.0 and 1.0."
            )