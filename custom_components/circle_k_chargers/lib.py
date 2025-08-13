import dataclasses
from dataclasses import asdict
from enum import StrEnum
from typing import List, Optional, Iterable, Set

import requests

from .models import Charger, PUBLIC_OPERATOR_IDS, Connector

API_DOMAIN = "api.circlek.com"
MARKET = "eu"
API_PATH = "ngrp-tardmap-charger-locator/api/v2"


def get_chargers(
    locale: str,
    lat: float,
    long: float,
    distance: int = 1000,
    operators=None,
    connectors=None,
    excluded_evses: Set[str] = None,
) -> Iterable[Charger]:

    resp = requests.get(
        url=f"https://{API_DOMAIN}/{MARKET}/{API_PATH}/chargers",
        params=GetChargersQueryString(
            countryCode=locale.split("_")[0],
            language=locale.split("_")[1],
            searchLatitude=lat,
            searchLongitude=long,
            maxDistance=distance,
            operators=operators,
            connectorTypes=connectors,
        ).to_dict(),
    )

    resp.raise_for_status()
    for o in resp.json():
        id = o["id"]
        distance = o["distance"]
        resp = requests.get(
            url=f"https://{API_DOMAIN}/{MARKET}/{API_PATH}/chargers/{id}",
            params={"countryCode": locale.split("_")[0], "language": locale.split("_")[1]},
        )
        resp.raise_for_status()
        data = resp.json()
        data["distance"] = distance
        yield Charger.from_api(data, excluded_evses=excluded_evses)


@dataclasses.dataclass(frozen=True, eq=True)
class QueryString:
    def to_dict(self):
        return {k: self._convert(v) for k, v in asdict(self).items() if v is not None}

    @staticmethod
    def _convert(v) -> str:
        if isinstance(v, str):
            return v
        if isinstance(v, list):
            return ",".join([QueryString._convert(x) for x in v])
        if isinstance(v, StrEnum):
            return v.value()
        return v


@dataclasses.dataclass(frozen=True, eq=True)
class GetChargersQueryString(QueryString):
    countryCode: str
    language: str
    searchLatitude: float
    searchLongitude: float
    maxDistance: int
    operators: Optional[List[str]]
    connectorTypes: Optional[List[Connector]]
    fastCharger: Optional[bool] = None
