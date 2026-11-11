"""Dependency-free, versioned disclosure rules shared by calculation and presentation owners."""

from dataclasses import dataclass
from types import MappingProxyType


@dataclass(frozen=True)
class DisclosureProfile:
    """Name an application-selected policy without accepting request-level threshold overrides."""

    id: str
    version: str = "2"
    minimum: int = 1

    def sample_visible(self, distinct_units):
        """Require a nonempty population without a minimum-size suppression rule."""
        return distinct_units >= self.minimum

    def visible_count(self, count):
        """Preserve every known dashboard count, including zero."""
        return count

    def small_cell(self, count, *, threshold=None):
        """Retain the compatibility predicate without hiding small cells or honoring old thresholds."""
        return False

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
