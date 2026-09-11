from dataclasses import dataclass

from .source_models import SanctionsSourceDefinition


@dataclass(frozen=True)
class SourceResolution:
    """
    Result of resolving one applicable sanctions source.
    """

    source: SanctionsSourceDefinition
    applicable: bool
    implementation_status: str

    @property
    def provider_available(self) -> bool:
        return self.source.provider_implemented