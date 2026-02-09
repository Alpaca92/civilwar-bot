import os
from typing import List

import discord
from discord import app_commands
from discord.ext import commands

from utils.checks import check_user_count

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

  @check_user_count(2, ">=")  # fixme: 10명 이상으로 변경
  @app_commands.command(name="split", description="랜덤 팀 짜기")
  async def split(self, interaction: discord.Interaction) -> None:
    embed = discord.Embed(
      title="🎮 팀 구성 대상 선택",
      description="내전 대상 10명을 선택해 주세요.",
      color=discord.Color.blue(),
    )

    members = [member for member in interaction.channel.members if not member.bot]

    await interaction.response.send_message(
      ephemeral=True,
      embed=embed,
      view=TargetMemberView(members),
    )


# [Step 1] 팀원 선택 및 확인 View
class TargetMemberSelect(discord.ui.Select):
  def __init__(self, members: List[discord.Member]):
    options = [
      discord.SelectOption(label=member.display_name, value=str(member.id))
      for member in members
    ]

    super().__init__(
      placeholder="10명을 선택하세요.",
      min_values=min(10, len(options)),
      max_values=min(10, len(options)),
      options=options[:25],  # Discord Select 최대 25개 제한
    )

  async def callback(self, interaction: discord.Interaction) -> None:
    selected_member_ids = [int(value) for value in self.values]
    selected_members = [
      interaction.guild.get_member(member_id) for member_id in selected_member_ids
    ]

    # 부모 View에 저장
    self.view.selected_members = selected_members

    await interaction.response.defer()


class ConfirmButton(discord.ui.Button):
  def __init__(self) -> None:
    super().__init__(label="확인", style=discord.ButtonStyle.primary)

  async def callback(self, interaction: discord.Interaction) -> None:
    view = self.view
    if not isinstance(view, TargetMemberView):
      return

    if not view.selected_members:
      await interaction.response.send_message(
        ephemeral=True,
        content="먼저 10명을 선택해 주세요.",
      )
      return

    member_mentions = [member.mention for member in view.selected_members if member]
    embed = discord.Embed(
      title="✅ 팀 구성 대상 확정",
      description="\n".join(member_mentions),
      color=discord.Color.green(),
    )

    self.disabled = True
    await interaction.response.send_message(embed=embed)

    # 팀 나누기 및 역할 할당 로직 View 밖으로 분리 예정


class TargetMemberView(discord.ui.View):
  def __init__(self, members: List[discord.Member]):
    super().__init__(timeout=300)
    self.selected_members: list[discord.Member] = []
    self.add_item(TargetMemberSelect(members))
    self.add_item(ConfirmButton())


async def setup(bot: commands.Bot) -> None:
  await bot.add_cog(SplitCog(bot))
