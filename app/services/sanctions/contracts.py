from dataclasses import dataclass, field

from .source_resolution import SourceResolution


@dataclass
class SanctionsResolution:
    """
    Complete source-resolution result for one screening context.
    """

    applicable_sources: list[SourceResolution] = field(default_factory=list)

    @property
    def implemented_sources(self) -> list[SourceResolution]:
        return [
            item
            for item in self.applicable_sources
            if item.provider_available
        ]

    @property
    def unavailable_sources(self) -> list[SourceResolution]:
        return [
            item
            for item in self.applicable_sources
            if not item.provider_available
        ]