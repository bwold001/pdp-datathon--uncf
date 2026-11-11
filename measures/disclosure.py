"""Dependency-free, versioned disclosure rules shared by calculation and presentation owners."""

from dataclasses import dataclass
from types import MappingProxyType


@dataclass(frozen=True)
class DisclosureProfile:
    """Name an application-selected policy without accepting request-level threshold overrides."""

    id: str
    version: str = "1"
    minimum: int = 10

    def sample_visible(self, distinct_units):
        """Check the existing minimum sample boundary, including zero-sized populations."""
        return distinct_units >= self.minimum

    def visible_count(self, count):
        """Preserve dashboard zero counts while hiding positive counts below its minimum."""
        return None if count is None or 0 < count < self.minimum else count

    def small_cell(self, count, *, threshold=None):
        """Identify a small positive cell; trusted legacy fixture configuration may set its threshold."""
        return count is not None and 0 < count < (
            self.minimum if threshold is None else threshold
        )

    def dashboard_status(self, measure, status, *, provisional=False):
        """Preserve dashboard gateway nonreporting and explicit provisional coverage semantics."""
        if (
            measure in ("gateway_math", "gateway_english")
            and status == "not_yet_observable"
        ):
            return "not_reported"
        return "provisional" if status == "ok" and provisional else status


DASHBOARD_V1 = DisclosureProfile("dashboard_v1")
LEGACY_ANALYTICS_V1 = DisclosureProfile("legacy_analytics_v1")
EXPLORATION_V1 = DisclosureProfile("exploration_v1")
PROFILES = MappingProxyType(
    {p.id: p for p in (DASHBOARD_V1, LEGACY_ANALYTICS_V1, EXPLORATION_V1)}
)


def profile(id):
    """Resolve only application-registered policies, never a model-authored policy definition."""
    try:
        return PROFILES[id]
    except (KeyError, TypeError) as error:
        raise ValueError("Unsupported disclosure profile") from error
