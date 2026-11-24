"""Shared reason codes and plain language for evidence that cannot provide a number."""

from typing import Literal

EvidenceReason = Literal[
    "empty_population",
    "missing_required_evidence",
    "followup_not_verified",
    "insufficient_followup",
    "no_known_outcomes",
    "completion_program_missing",
]

REASON_MESSAGES = {
    "empty_population": "No students match this selection.",
    "missing_required_evidence": "Information needed to calculate this result is missing.",
    "followup_not_verified": "We haven't verified how long the data follows these students.",
    "insufficient_followup": "These students haven't been followed long enough to report this result.",
    "no_known_outcomes": "The selected students do not have usable outcome information for this calculation.",
    "completion_program_missing": "We cannot tell which program students graduated from because the necessary award information is missing.",
}
