import os
from functools import lru_cache

from supabase import Client, create_client


class SupabaseConfigError(RuntimeError):
  pass


@lru_cache(maxsize=1)
def get_supabase_client() -> Client:
  url = os.getenv("SUPABASE_URL")
  key = os.getenv("SUPABASE_KEY")

  if not url:
    raise SupabaseConfigError("SUPABASE_URL is not set")

  if not key:
    raise SupabaseConfigError("SUPABASE_KEY is not set")

  return create_client(url, key)
