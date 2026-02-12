import os
from typing import Self

import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

class Client(commands.Bot):
  # setup_hook: 봇이 시작될 때 가장 먼저 비동기로 실행됨
  async def setup_hook(self: Self) -> None:
    self.tree.on_error = self.on_app_command_error

    # Cogs 로드
    for filename in os.listdir("./cogs"):
      if filename.endswith(".py") and not filename.startswith("_"):
        try:
          await self.load_extension(f"cogs.{filename[:-3]}")
          print(f"✅ Loaded cog: {filename}")
        except Exception as error:
          print(f"❌ Failed to load {filename}: {error}")

    # 전역 커맨드 동기화
    synced = await self.tree.sync()
    print(f"Synced {len(synced)} commands globally")

  async def on_ready(self: Self) -> None:
    print(f"🚀 Logged in as {self.user} (ID: {self.user.id})")

  async def on_app_command_error(
    self: Self,
    interaction: discord.Interaction,
    error: app_commands.AppCommandError,
  ) -> None:
    if isinstance(error, app_commands.CheckFailure):
      message = str(error) or "❌ 이 명령어를 실행할 수 있는 권한이 없습니다."

      if interaction.response.is_done():
        await interaction.followup.send(message, ephemeral=True)
      else:
        await interaction.response.send_message(message, ephemeral=True)
      return


# Intents 설정 함수
def get_intents() -> discord.Intents:
  intents = discord.Intents.default()
  intents.message_content = True
  intents.members = True  # 팀 나누기 봇에는 필수!
  return intents


# 실행부
if __name__ == "__main__":
  client = Client(
    command_prefix="!",
    intents=get_intents(),
    help_command=None,  # 기본 도움말 커맨드 비활성화 (선택)
  )
  client.run(os.getenv("DISCORD_TOKEN"))
