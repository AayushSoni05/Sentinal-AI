from dataclasses import dataclass, field

from .source_result import SourceScreeningResult


@dataclass
class ScreeningCollection:
    """
    Collection of source-specific sanctions screening results
    for one target.
    """

    results: list[SourceScreeningResult] = field(default_factory=list)

    @property
    def total_sources_evaluated(self) -> int:
        return len(self.results)

    @property
    def sources_with_positive_matches(self) -> int:
        return sum(
            1
            for result in self.results
            if result.positive_matches > 0
        )

    @property
    def positive_results(self) -> list[SourceScreeningResult]:
        return [
            result
            for result in self.results
            if result.positive_matches > 0
        ]