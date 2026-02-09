import os
import random
from typing import List

import discord
from discord import app_commands
from discord.ext import commands

from utils.checks import is_in_voice, check_user_count

RED_ROLE_NAME = "Red"
BLUE_ROLE_NAME = "Blue"
WAITING_VOICE_ID = int(os.getenv("WAITING_VOICE_ID"))
RED_VOICE_ID = int(os.getenv("RED_VOICE_ID"))
BLUE_VOICE_ID = int(os.getenv("BLUE_VOICE_ID"))


class SplitCog(commands.Cog):
  def __init__(self, bot: commands.Bot) -> None:
    self.bot = bot

  async def get_or_create_role(
    self, guild: discord.Guild, name: str, color: discord.Color
  ) -> discord.Role:
    role = discord.utils.get(guild.roles, name=name)
    if not role:
      role = await guild.create_role(name=name, color=color)
    return role

  @check_user_count(2, ">=") # fixme: 10명 이상으로 변경
  @app_commands.command(
    name="split", description="팀 구성 (미선택 시 랜덤, 선택 시 고정)"
  )
  async def split(self, interaction: discord.Interaction) -> None:
    return


async def setup(bot: commands.Bot) -> None:
  await bot.add_cog(SplitCog(bot))
