# ============================================================
# EXTERNAL SCREENING PROVIDER BASE
# ============================================================

from typing import Protocol


class ExternalScreeningProvider(Protocol):

    def screen(
        self,
        name: str,
        screening_type: str
    ):
        ...