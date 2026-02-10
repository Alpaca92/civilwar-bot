from random import shuffle
from typing import List

import discord


def split_teams(
  members: List[discord.Member],
) -> tuple[list[discord.Member], list[discord.Member]]:
  """멤버 리스트를 랜덤하게 두 팀으로 나눕니다.

  Args:
      members: 팀으로 나눌 멤버 리스트

  Returns:
      (red_team, blue_team) 튜플
  """
  random_members = members.copy()
  shuffle(random_members)
  mid_index = len(random_members) // 2
  red_team = random_members[:mid_index]
  blue_team = random_members[mid_index:]
  return red_team, blue_team
