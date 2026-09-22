from abc import ABC, abstractmethod

from app.services.sanctions.sources import (
    SanctionsSourceDefinition,
    get_all_sources,
)
import requests
from urllib.parse import urljoin

class SanctionsSourceDiscovery(ABC):

    @abstractmethod
    def discover_sources(self) -> list[SanctionsSourceDefinition]:
        pass


class CatalogueSanctionsSourceDiscovery(
    SanctionsSourceDiscovery
):

    def discover_sources(
        self,
    ) -> list[SanctionsSourceDefinition]:

        return get_all_sources()

def resolve_data_source_url(
    data_source_url: str | None,
    timeout: int = 5,
) -> str | None:
    if not data_source_url:
        return None

    try:
        response = requests.get(
            data_source_url,
            timeout=(3, 5),
        )
        response.raise_for_status()

        content_type = (
            response.headers.get("content-type", "")
            .lower()
        )

        if "text/csv" in content_type:
            return data_source_url

        if "text/html" not in content_type:
            return data_source_url

        from bs4 import BeautifulSoup

        soup = BeautifulSoup(
            response.text,
            "html.parser",
        )

        for link in soup.find_all("a", href=True):
            href = link["href"]

            if ".csv" in href.lower():
                return urljoin(
                    data_source_url,
                    href,
                )

        return data_source_url

    except requests.RequestException:
        return data_source_url
    except Exception:
        return data_source_url

class HttpSanctionsSourceDiscovery(
    SanctionsSourceDiscovery
):

    def __init__(
        self,
        discovery_url: str,
        timeout: int = 5,
    ):
        self.discovery_url = discovery_url
        self.timeout = timeout

    def discover_sources(
        self,
    ) -> list[SanctionsSourceDefinition]:

        response = requests.get(
            self.discovery_url,
            timeout=self.timeout,
        )

        response.raise_for_status()

        data = response.json()
        datasets = data.get("datasets", [])

        data = [
            item
            for item in datasets
            if isinstance(item, dict)
        ]

        sources = []

        for item in data:
            tags = item.get("tags") or []

            if (
                "list.sanction" not in tags
            ):
                continue
            if item.get("deprecated"):
                continue

            publisher = item.get("publisher") or {}
            resources = item.get("resources") or []

            official_resource = next(
                (
                    resource
                    for resource in resources
                    if resource.get("url")
                ),
                None,
            )

            if official_resource is None:
                continue

            data_config = item.get("data") or {}
            # if item.get("name") == "my_moha_sanctions":
            #     print("DISCOVERY DATA:", repr(data_config))

            connector_type = (
                str(data_config.get("format", "UNKNOWN")).upper()
            )

            sources.append(
                SanctionsSourceDefinition(
                    source_id=item["name"],
                    source_name=item.get(
                        "title",
                        item["name"],
                    ),
                    source_list_name=item.get(
                        "title",
                        item["name"],
                    ),
                    issuing_authority=publisher.get(
                        "name",
                        "UNKNOWN",
                    ),
                    issuing_country=(
                        publisher.get("country")
                        or "UNKNOWN"
                    ),
                    region="GLOBAL",
                    source_scope="GLOBAL",
                    source_type="SANCTIONS",
                    official_source_url=(
                        item.get("url")
                        or publisher.get("url")
                        or official_resource["url"]
                    ),
                    catalogue_resource_url=official_resource["url"],
                    data_source_url=data_config.get("url"),
                    connector_type=connector_type,
                    implementation_status="DISCOVERED",
                )
            )

        return sources

def discover_sanctions_sources(
) -> list[SanctionsSourceDefinition]:

    discovery = CatalogueSanctionsSourceDiscovery()

    return discovery.discover_sources()