import os
from typing import List

import discord
from discord import app_commands
from discord.ext import commands

from utils.checks import check_user_count
from utils.team_utils import split_teams

RED_ROLE_NAME = "Red"
BLUE_ROLE_NAME = "Blue"
WAITING_VOICE_ID = int(os.getenv("WAITING_VOICE_ID"))
RED_VOICE_ID = int(os.getenv("RED_VOICE_ID"))
BLUE_VOICE_ID = int(os.getenv("BLUE_VOICE_ID"))


class SplitCog(commands.Cog):
  def __init__(self, bot: commands.Bot) -> None:
    pass

  async def get_or_create_role(
    self, guild: discord.Guild, name: str, color: discord.Color
  ) -> discord.Role:
    role = discord.utils.get(guild.roles, name=name)

    if not role:
      role = await guild.create_role(name=name, color=color)
    return role

  @check_user_count(10, ">=")
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
      placeholder=f"{min(10, len(options))}명을 선택하세요.",
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

    # View의 모든 아이템 비활성화
    for item in view.children:
      item.disabled = True
    
    # 원본 메시지 편집하여 비활성화된 View 반영
    await interaction.response.edit_message(view=view)
    
    # 팀 나누기
    red_team, blue_team = split_teams(view.selected_members)
    
    # 결과 메시지 전송
    await interaction.followup.send(
      embed=ResultEmbed(red_team, blue_team),
      view=ResultView(red_team, blue_team),
    )


class TargetMemberView(discord.ui.View):
  def __init__(self, members: List[discord.Member]):
    super().__init__(timeout=300)
    self.selected_members: list[discord.Member] = []
    self.add_item(TargetMemberSelect(members))
    self.add_item(ConfirmButton())


# [Step 2] 팀원 결과 및 Role 부여
class ResultEmbed(discord.Embed):
  def __init__(self, red_team: List[discord.Member], blue_team: List[discord.Member]) -> None:
    super().__init__(
      title="⚔️ 팀 구성 완료",
      color=discord.Color.green(),
    )

    # 필드 추가
    self.add_field(
      name="🔴 Red Team",
      value="\n".join(member.display_name for member in red_team),
      inline=True,
    )
    self.add_field(
      name="🔵 Blue Team",
      value="\n".join(member.display_name for member in blue_team),
      inline=True,
    )

class SetRoleButton(discord.ui.Button):
  def __init__(self) -> None:
    super().__init__(label="각 팀 역할 부여", style=discord.ButtonStyle.secondary)

  async def callback(self, interaction: discord.Interaction) -> None:
    view = self.view

    if not isinstance(view, ResultView):
      return

    guild = interaction.guild
    if not guild:
      await interaction.response.send_message(
        ephemeral=True,
        content="서버에서만 사용할 수 있는 명령어입니다.",
      )
      return

    teams_data = [
      (RED_ROLE_NAME, discord.Color.red(), view.red_team),
      (BLUE_ROLE_NAME, discord.Color.blue(), view.blue_team),
    ]
    
    split_cog = interaction.client.get_cog("SplitCog")

    if not isinstance(split_cog, SplitCog):
      await interaction.response.send_message(
        ephemeral=True,
        content="❌ 역할 생성 기능을 찾지 못했습니다. 봇을 재시작해 주세요.",
      )
      return

    for role_name, color, members in teams_data:
      role = await split_cog.get_or_create_role(guild, role_name, color)
      for member in members:
        await member.add_roles(role)

    # View의 모든 아이템 비활성화
    for item in view.children:
      item.disabled = True

    await interaction.response.edit_message(view=view)
    await interaction.followup.send(
      content="✅ 각 팀 역할이 부여되었습니다.",
    )


class ResultView(discord.ui.View):
  def __init__(self, red_team: List[discord.Member], blue_team: List[discord.Member]) -> None:
    super().__init__(timeout=300)
    self.red_team = red_team
    self.blue_team = blue_team
    self.add_item(SetRoleButton())


async def setup(bot: commands.Bot) -> None:
  await bot.add_cog(SplitCog(bot))
