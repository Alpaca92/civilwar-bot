from datetime import datetime

from utils.constants import TEAM_SIDES


def normalize_team_side(value: str) -> str:
  team_side = value.strip().upper()
  if team_side not in TEAM_SIDES:
    raise ValueError(f"winner must be one of: {', '.join(TEAM_SIDES)}")
  return team_side


def parse_created_at(value: str) -> str:
  try:
    parsed = datetime.fromisoformat(value)
  except ValueError as exc:
    raise ValueError("created-at must be a valid ISO-8601 datetime") from exc
  return parsed.isoformat()
