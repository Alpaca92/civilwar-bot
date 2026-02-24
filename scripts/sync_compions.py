import argparse
import json
import sys
from pathlib import Path
from typing import Iterable
from urllib.error import URLError
from urllib.request import urlopen

from dotenv import load_dotenv

from database import get_supabase_client

ROOT_DIR = Path(__file__).resolve().parents[1]

if str(ROOT_DIR) not in sys.path:
  sys.path.insert(0, str(ROOT_DIR))


VERSIONS_URL = "https://ddragon.leagueoflegends.com/api/versions.json"
CHAMPION_URL = (
  "https://ddragon.leagueoflegends.com/cdn/{version}/data/{locale}/champion.json"
)


def fetch_json(url: str) -> dict | list:
  with urlopen(url) as response:
    return json.loads(response.read().decode("utf-8"))


def get_latest_version() -> str:
  versions = fetch_json(VERSIONS_URL)
  if not versions:
    raise RuntimeError("Could not fetch Riot versions")
  return versions[0]


def fetch_champion_names(locale: str) -> list[str]:
  version = get_latest_version()
  payload = fetch_json(CHAMPION_URL.format(version=version, locale=locale))
  champions = payload.get("data", {})
  return [champion["name"] for champion in champions.values()]


def batched(rows: list[dict], size: int) -> Iterable[list[dict]]:
  for index in range(0, len(rows), size):
    yield rows[index : index + size]


def upsert_champions(
  table_name: str, column_name: str, names: list[str], batch_size: int
) -> int:
  client = get_supabase_client()
  rows = [{column_name: name} for name in names]

  inserted = 0
  for batch in batched(rows, batch_size):
    client.table(table_name).upsert(batch, on_conflict=column_name).execute()
    inserted += len(batch)
  return inserted


def parse_args() -> argparse.Namespace:
  parser = argparse.ArgumentParser(
    description="Sync Riot champions into Supabase table"
  )
  parser.add_argument("--table", default="compions", help="Target table name")
  parser.add_argument("--column", default="name", help="Target column name")
  parser.add_argument(
    "--locale", default="ko_KR", help="Riot locale, e.g. ko_KR or en_US"
  )
  parser.add_argument(
    "--batch-size", type=int, default=100, help="Batch size for upsert"
  )
  parser.add_argument(
    "--dry-run", action="store_true", help="Only print champion names"
  )
  return parser.parse_args()


def main() -> None:
  load_dotenv(override=False)
  args = parse_args()

  if args.batch_size <= 0:
    raise ValueError("batch-size must be greater than 0")

  try:
    champion_names = fetch_champion_names(args.locale)
  except URLError as exc:
    raise RuntimeError(f"Failed to call Riot API: {exc}") from exc

  if not champion_names:
    raise RuntimeError("No champions found from Riot API")

  if args.dry_run:
    print(f"Fetched {len(champion_names)} champions")
    for name in sorted(champion_names):
      print(name)
    return

  inserted_count = upsert_champions(
    table_name=args.table,
    column_name=args.column,
    names=champion_names,
    batch_size=args.batch_size,
  )
  print(f"Upserted {inserted_count} rows into {args.table}.{args.column}")


if __name__ == "__main__":
  main()
