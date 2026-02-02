import discord
import os
from dotenv import load_dotenv
from typing import Self
from discord.ext import commands
from discord import app_commands

# .env 파일 로드
load_dotenv()

guild = discord.Object(id=1461751770366869574)

class Client(commands.Bot):
  async def on_ready(self: Self) -> None:
    print(f'Logged in as {self.user} (ID: {self.user.id})')

    try:
      synced = await self.tree.sync(guild=guild)
      print(f'Synced {len(synced)} commands to guild {guild.id}')
    except Exception as error:
      print(f'Error syncing commands: {error}')
  
  async def setup_hook(self: Self) -> None:
    # cogs 폴더의 모든 파일을 로드
    for filename in os.listdir('./cogs'):
      if filename.endswith('.py') and not filename.startswith('_'):
        try:
          await self.load_extension(f'cogs.{filename[:-3]}')
          print(f'✅ Loaded cog: {filename}')
        except Exception as error:
          print(f'❌ Failed to load {filename}: {error}')

# Intents는 Discord 봇이 어떤 이벤트를 받을 것인지 지정하는 설정
def get_intents():
  intents: discord.Intents = discord.Intents.default()
  intents.message_content = True
  intents.reactions = True
  intents.guilds = True
  intents.members = True
  
  return intents

# Client 인스턴스를 생성할 때 Intents를 전달
client: Client = Client(intents=get_intents(), command_prefix='!')

# 클라이언트 실행
client.run(os.getenv('DISCORD_TOKEN'))