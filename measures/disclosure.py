"""Dependency-free, versioned disclosure rules shared by calculation and presentation owners."""

import os
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass
from types import MappingProxyType


MIN_STUDENTS_SETTING = "UNCF_MIN_STUDENTS"
DEFAULT_MIN_STUDENTS = 1
_DISPLAY_MINIMUM: ContextVar[int | None] = ContextVar("display_minimum", default=None)


def min_students() -> int:
    """Use main's server-only display setting; synthetic groups default to one student."""
    selected = _DISPLAY_MINIMUM.get()
    if selected is not None:
        return selected
    raw = os.environ.get(MIN_STUDENTS_SETTING, "").strip()
    if not raw:
        return DEFAULT_MIN_STUDENTS
    if not raw.isdigit() or int(raw) < 1:
        raise ValueError(f"{MIN_STUDENTS_SETTING} must be a whole number of 1 or more, not {raw!r}")
    return int(raw)


@contextmanager
def dashboard_scope():
    """Pin the server's display setting for one execution without accepting a client override."""
    token = _DISPLAY_MINIMUM.set(min_students())
    try:
        yield
    finally:
        _DISPLAY_MINIMUM.reset(token)


@dataclass(frozen=True)
class DisclosureProfile:
    """Name an application-selected policy without accepting request-level threshold overrides."""

    id: str
    version: str = "1"
    minimum_size: int = 10

    @property
    def minimum(self):
        """Keep dashboard settings dynamic while legacy/exploration retain their own fixed minimum."""
        return min_students() if self.id == "dashboard_v1" else self.minimum_size

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


DASHBOARD_V1 = DisclosureProfile("dashboard_v1", version="2")
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
