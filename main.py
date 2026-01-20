import discord
import os
from dotenv import load_dotenv
from typing import Self

# .env 파일 로드
load_dotenv()

# test server id

class Client(discord.Client):
  async def on_ready(self: Self) -> None:
    print(f'Logged in as {self.user} (ID: {self.user.id})')

    try:
      guild = discord.Object(id=1461751770366869574)
      synced = await self.tree.sync(guild=guild)

      print(f'Synced {len(synced)} commands to guild {guild.id}')
    except Exception as error:
      print(f'Error syncing commands: {error}')

  async def on_message(self: Self, message: discord.Message) -> None:
    # 봇이 자신의 메시지에 반응하지 않도록 설정
    if message.author.id == self.user.id:
      return

    if message.content.startswith('hello'):
      await message.channel.send(f'Hello! {message.author}')

  async def on_reaction_add(self: Self, reaction: discord.Reaction, user: discord.User) -> None:
    if user.id == self.user.id:
      return

    if str(reaction.emoji) == '👍':
      await reaction.message.channel.send(f'Thanks for the thumbs up, {user.name}!')

# Intents는 Discord 봇이 어떤 이벤트를 받을 것인지 지정하는 설정
intents: discord.Intents = discord.Intents.default()
intents.message_content = True

# Client 인스턴스를 생성할 때 Intents를 전달
client: Client = Client(intents=intents)

# command 추가
@client.tree.command(name="hello", description="say Hello !", guild=1461751770366869574)
async def sayHello(interaction: discord.Interaction):
  await interaction.response.send_message("Hi there !")

# 클라이언트 실행
client.run(os.getenv('DISCORD_TOKEN')) 