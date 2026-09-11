from dataclasses import dataclass


@dataclass(frozen=True)
class SanctionsSourceDefinition:
    """
    Defines an official sanctions source and the jurisdiction that
    issued or maintains the list.
    """

    source_name: str
    issuing_country: str
    source_type: str = "SANCTIONS"
    global_scope: bool = False
    enabled: bool = True

    provider_name: str | None = None
    provider_implemented: bool = False

    @property
    def implementation_status(self) -> str:
        """
        Indicates whether Sentinel AI currently has a provider
        implementation for this source.
        """

        if self.provider_implemented:
            return "IMPLEMENTED"

        return "NOT_IMPLEMENTED"