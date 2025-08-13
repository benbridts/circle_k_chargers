import dataclasses
import enum
from dataclasses import asdict
from typing import Optional, List, Mapping, Any, Set

_PUBLIC_OPERATORS = {
    "BE": {
        "VIA": {"ENGIE Vianeo"},
        "ALL": {"Allego"},
        "D24": {"DATS 24"},
        "TCB": {"TotalEnergies"},
        "BCA": {"Blue Corner"},
        "FAS": {"Fastned"},
    }
}
PUBLIC_OPERATOR_IDS = {
    f"{country}*{operator}" for country, operators in _PUBLIC_OPERATORS.items() for operator in operators
}
# PUBLIC_OPERATOR_NAMES = {name.lower(): f"{country}*{operator}" for country, operators in PUBLIC_OPERATORS.items() for operator, names in operators.items() for name in names}


class Connector(enum.StrEnum):
    TYPE_1 = "IEC_62196_T1"
    TYPE_1_COMBO = "IEC_62196_T1_COMBO"
    TYPE_2 = "IEC_62196_T2"
    TYPE_2_COMBO = "IEC_62196_T2_COMBO"
    TYPE_3A = "IEC_62196_T3A"
    TYPE_3C = "IEC_62196_T3C"
    DOMESTIC_E = "DOMESTIC_E"
    DOMESTIC_F = "DOMESTIC_F"
    CHADEMO = "CHADEMO"


class Status(enum.StrEnum):
    CHARGING = "Charging"
    AVAILABLE = "Available"
    INOPERATIVE = "Inoperative"
    OUT_OF_ORDER = "OutOfOrder"
    UNKNOWN = "Unknown"


@dataclasses.dataclass
class Evse:
    id: str
    status: Status


@dataclasses.dataclass
class Charger:
    id: str
    name: str
    address: str
    city: str
    evses: List[Evse]
    distance: int

    @classmethod
    def from_api(cls, o: Mapping[str, Any], excluded_evses: Optional[Set[str]] = None):
        if excluded_evses is None:
            excluded_evses = {}
        return cls(
            id=o["id"],
            name=o["name"],
            address=o["address"],
            city=o["city"],
            evses=[
                Evse(id=e["id"], status=Status[e.get("status", "Unknown").upper()])
                for e in o.get("evses", [])
                if e["id"] not in excluded_evses
            ],
            distance=o["distance"],
        )

    def _total_eves(self, status: Optional[Status] = None):
        if status is None:
            return len(self.evses)
        return len([x for x in self.evses if x.status == status])

    @property
    def num_charging(self):
        return self._total_eves(Status.CHARGING)

    @property
    def num_available(self):
        return self._total_eves(Status.AVAILABLE)

    @property
    def num_broken(self):
        return self.num_total - self.num_charging - self.num_available

    @property
    def num_total(self):
        return self._total_eves()

    def evse_status_map(self) -> Mapping[str, Status]:
        return {x.id: x.status for x in self.evses}

    def evse_status(self, id: str) -> Status:
        return self.evse_status_map()[id]

    def to_dict(self):
        return asdict(self)

    def __str__(self):
        return f"{self.name} ({self.address}, {self.city}): {self.num_available}/{self.num_total} ({self.num_broken} broken)"
