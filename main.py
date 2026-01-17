import discord
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

class Client(discord.Client):
  async def on_ready(self: 'Client') -> None:
    print(f'Logged in as {self.user} (ID: {self.user.id})')

  async def on_message(self: 'Client', message: discord.Message) -> None:
    # 봇이 자신의 메시지에 반응하지 않도록 설정
    if message.author.id == self.user.id:
      return

    # 메시지 내용이 "ping"인 경우 "pong"으로 응답
    if message.content == 'ping':
      await message.channel.send('pong')

# Intents는 Discord 봇이 어떤 이벤트를 받을 것인지 지정하는 설정
intents: discord.Intents = discord.Intents.default()
intents.message_content = True

# Client 인스턴스를 생성할 때 Intents를 전달
client: Client = Client(intents=intents)
client.run(os.getenv('DISCORD_TOKEN'))