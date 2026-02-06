import os
import random
from typing import List

import discord
from discord import app_commands
from discord.ext import commands

from utils.checks import is_in_voice

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

  @is_in_voice()
  @app_commands.command(
    name="split", description="팀 구성 (미선택 시 랜덤, 선택 시 고정)"
  )
  async def split(self, interaction: discord.Interaction) -> None:
    voice_state = interaction.user.voice

    # 음성 채널에 비접속 시 안내
    if not voice_state or not voice_state.channel:
      await interaction.response.send_message(
        "❌ 음성 채널에 접속한 상태에서만 팀 구성을 할 수 있습니다.",
        ephemeral=True,
      )
      return

    candidates = [m for m in voice_state.channel.members if not m.bot]

    # 음성 채널에 10명 미만일 경우 안내
    # if len(candidates) != 10:
    #   await interaction.response.send_message(
    #     f"❌ 음성 채널에 인원이 부족거나 많습니다. (현재 {len(candidates)}명)",
    #     ephemeral=True,
    #   )
    #   return

    embed = discord.Embed(
      title="🎮 팀 구성 설정",
      description="1. 같은 음성 채널에 접속된 유저들만 팀 구성 대상이 됩니다.\n2. 레드팀/블루팀에 고정할 멤버를 각각 선택하세요.\n3. 아무도 선택하지 않으면 완전 랜덤으로 배정됩니다.",
      color=discord.Color.blue(),
    )
    await interaction.response.send_message(
      embed=embed, view=TeamSetupView(self, candidates), ephemeral=True
    )


# [Step 1] 팀원 선택 및 확인 View
class TeamMemberSelect(discord.ui.Select):
  def __init__(
    self,
    placeholder: str,
    options: List[discord.SelectOption],
    min_values: int = 0,
    max_values: int = 5,
  ) -> None:
    super().__init__(
      placeholder=placeholder,
      min_values=min_values,
      max_values=min(max_values, len(options)),
      options=options,
    )


class TeamSetupView(discord.ui.View):
  def __init__(self, cog: SplitCog, candidates: List[discord.Member]) -> None:
    super().__init__(timeout=300)
    self.cog = cog
    self.fixed_red: List[discord.Member] = []
    self.fixed_blue: List[discord.Member] = []
    self.max_team_size = 5

    self.candidates = candidates
    self.candidates_map = {str(m.id): m for m in candidates}

    self.red_select = TeamMemberSelect(
      placeholder="🔴 레드팀 고정 멤버 (0~5명)",
      options=self._build_options(set(), set()),
      min_values=0,
      max_values=self.max_team_size,
    )
    self.red_select.callback = self.select_red
    self.add_item(self.red_select)

    self.blue_select = TeamMemberSelect(
      placeholder="🔵 블루팀 고정 멤버 (0~5명)",
      options=self._build_options(set(), set()),
      min_values=0,
      max_values=self.max_team_size,
    )
    self.blue_select.callback = self.select_blue
    self.add_item(self.blue_select)

  def _build_options(
    self, exclude_ids: set[str], selected_ids: set[str]
  ) -> List[discord.SelectOption]:
    options = []
    for member in self.candidates:
      member_id = str(member.id)
      if member_id in exclude_ids:
        continue
      options.append(
        discord.SelectOption(
          label=member.display_name,
          value=member_id,
          default=member_id in selected_ids,
        )
      )

    # Discord Select는 최대 25개까지만 표시 가능
    return options[:25]

  def _refresh_selects(self) -> None:
    red_ids = {str(m.id) for m in self.fixed_red}
    blue_ids = {str(m.id) for m in self.fixed_blue}
    red_options = self._build_options(blue_ids, red_ids)
    blue_options = self._build_options(red_ids, blue_ids)

    print(f"Red fixed IDs: {red_ids}")
    print(f"Blue fixed IDs: {blue_ids}")

    if not red_options:
      red_options = [
        discord.SelectOption(label="선택 가능한 인원이 없습니다", value="none")
      ]
      self.red_select.disabled = True
    else:
      self.red_select.disabled = False

    self.red_select.options = red_options
    self.red_select.max_values = min(self.max_team_size, len(red_options))

    if not blue_options:
      blue_options = [
        discord.SelectOption(label="선택 가능한 인원이 없습니다", value="none")
      ]
      self.blue_select.disabled = True
    else:
      self.blue_select.disabled = False

    self.blue_select.options = blue_options
    self.blue_select.max_values = min(self.max_team_size, len(blue_options))

  async def select_red(self, interaction: discord.Interaction) -> None:
    self.fixed_red = [self.candidates_map[v] for v in self.red_select.values]
    self._refresh_selects()
    await interaction.response.edit_message(view=self)

  async def select_blue(self, interaction: discord.Interaction) -> None:
    self.fixed_blue = [self.candidates_map[v] for v in self.blue_select.values]
    self._refresh_selects()
    await interaction.response.edit_message(view=self)

  @discord.ui.button(label="팀 나누기 확정", style=discord.ButtonStyle.success)
  async def confirm(
    self, interaction: discord.Interaction, button: discord.ui.Button
  ) -> None:
    # 중복 선택 검사
    combined = set(self.fixed_red) & set(self.fixed_blue)
    if combined:
      return await interaction.followup.send(
        "❌ 레드팀과 블루팀에 중복된 멤버가 있습니다.", ephemeral=True
      )

    all_candidates = interaction.user.voice.channel.members

    # 랜덤 로직
    fixed_all = set(self.fixed_red + self.fixed_blue)
    random_pool = [m for m in all_candidates if m not in fixed_all]
    random.shuffle(random_pool)

    # 10명을 채우기 위해 랜덤 풀에서 필요한 만큼 가져옴
    final_participants = list(fixed_all) + random_pool[: (10 - len(fixed_all))]
    random_pool_final = [m for m in final_participants if m not in fixed_all]
    random.shuffle(random_pool_final)

    # 최종 팀 배정
    red_team = list(self.fixed_red) + random_pool_final[: (5 - len(self.fixed_red))]
    blue_team = list(self.fixed_blue) + random_pool_final[(5 - len(self.fixed_red)) :]

    embed = discord.Embed(title="⚔️ 팀 배정 완료", color=discord.Color.gold())
    embed.add_field(name="🔴 Red Team", value="\n".join([m.mention for m in red_team]))
    embed.add_field(
      name="🔵 Blue Team", value="\n".join([m.mention for m in blue_team])
    )

    await interaction.response.edit_message(
      content="팀이 확정되었습니다. 시작 버튼을 누르면 이동합니다.",
      embed=embed,
      view=GameControlView(self.cog, red_team, blue_team),
    )


# [Step 2] 시작 및 종료 제어 View
class GameControlView(discord.ui.View):
  def __init__(
    self, cog: SplitCog, red: List[discord.Member], blue: List[discord.Member]
  ) -> None:
    super().__init__(timeout=None)
    self.cog = cog
    self.red = red
    self.blue = blue

  @discord.ui.button(
    label="경기 시작 (이동)", style=discord.ButtonStyle.primary, emoji="🚀"
  )
  async def start(
    self, interaction: discord.Interaction, button: discord.ui.Button
  ) -> None:
    await interaction.response.defer()

    red_role = await self.cog.get_or_create_role(
      interaction.guild, RED_ROLE_NAME, discord.Color.red()
    )
    blue_role = await self.cog.get_or_create_role(
      interaction.guild, BLUE_ROLE_NAME, discord.Color.blue()
    )

    red_ch = interaction.guild.get_channel(RED_VOICE_ID)
    blue_ch = interaction.guild.get_channel(BLUE_VOICE_ID)

    for m in self.red:
      await m.add_roles(red_role)
      if m.voice:
        await m.move_to(red_ch)

    for m in self.blue:
      await m.add_roles(blue_role)
      if m.voice:
        await m.move_to(blue_ch)

    # 시작 버튼을 종료 버튼으로 교체
    button.disabled = True
    await interaction.edit_original_response(view=self)
    await interaction.followup.send(
      "경기가 시작되었습니다! 종료 시 아래 종료 버튼을 눌러주세요.",
      view=GameOverView(self.cog, self.red, self.blue),
    )


# [Step 3] 종료 제어 View
class GameOverView(discord.ui.View):
  def __init__(self, cog: SplitCog, red, blue) -> None:
    super().__init__(timeout=None)
    self.cog = cog
    self.members = red + blue

  @discord.ui.button(
    label="경기 종료 (복귀 및 역할 제거)", style=discord.ButtonStyle.danger, emoji="🏁"
  )
  async def stop_game(
    self, interaction: discord.Interaction, button: discord.ui.Button
  ) -> None:
    await interaction.response.defer()

    red_role = discord.utils.get(interaction.guild.roles, name=RED_ROLE_NAME)
    blue_role = discord.utils.get(interaction.guild.roles, name=BLUE_ROLE_NAME)
    waiting_ch = interaction.guild.get_channel(WAITING_VOICE_ID)

    for m in self.members:
      # 역할 제거
      roles_to_remove = [r for r in [red_role, blue_role] if r in m.roles]
      if roles_to_remove:
        await m.remove_roles(*roles_to_remove)
      # 대기실 이동
      if m.voice:
        await m.move_to(waiting_ch)

    await interaction.followup.send("✅ 모든 인원이 복귀하였고 역할이 제거되었습니다.")
    super().stop()


async def setup(bot: commands.Bot) -> None:
  await bot.add_cog(SplitCog(bot))
