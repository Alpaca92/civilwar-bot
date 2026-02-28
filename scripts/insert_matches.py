import argparse

from dotenv import load_dotenv

from database import get_supabase_client
from utils.validators import normalize_team_side, parse_created_at


def parse_args() -> argparse.Namespace:
  parser = argparse.ArgumentParser(description="Insert one row into matches table")
  parser.add_argument(
    "--winner",
    required=True,
    help="Final winner team side (RED or BLUE)",
  )
  parser.add_argument(
    "--created-at",
    help="Optional created_at in ISO-8601 format (e.g. 2026-02-26T15:00:00+09:00)",
  )
  parser.add_argument("--table", default="matches", help="Target table name")
  return parser.parse_args()


def insert_match(table_name: str, winner: str, created_at: str | None) -> dict:
  client = get_supabase_client()
  payload: dict[str, str] = {"final_winner": winner}

  if created_at:
    payload["created_at"] = created_at

  response = client.table(table_name).insert(payload).execute()
  if not response.data:
    raise RuntimeError("Insert succeeded but no row was returned")

  return response.data[0]


def main() -> None:
  load_dotenv(override=False)
  args = parse_args()

  winner = normalize_team_side(args.winner)
  created_at = parse_created_at(args.created_at) if args.created_at else None

  inserted = insert_match(
    table_name=args.table,
    winner=winner,
    created_at=created_at,
  )
  print(
    f"Inserted match id={inserted['id']} winner={inserted['final_winner']} "
    f"created_at={inserted['created_at']}"
  )


if __name__ == "__main__":
  main()
