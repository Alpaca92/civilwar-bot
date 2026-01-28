import discord
import os
from dotenv import load_dotenv
from typing import Self
from discord.ext import commands
from discord import app_commands

# .env 파일 로드
load_dotenv()

class Client(commands.Bot):
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
client: Client = Client(intents=intents, command_prefix='!')

# command 추가
@client.tree.command(name="hello", description="say Hello !", guild=discord.Object(id=1461751770366869574))
async def sayHello(interaction: discord.Interaction):
  await interaction.response.send_message("Hi there !")

@client.tree.command(name="embed", description="send embed message", guild=discord.Object(id=1461751770366869574))
async def sendEmbed(interaction: discord.Interaction):
  embed = discord.Embed(title="Sample Embed", description="This is an example of an embedded message.", color=0x00ff00)
  embed.add_field(name="Field 1", value="This is the value for field 1", inline=False)
  embed.add_field(name="Field 2", value="This is the value for field 2", inline=False)
  embed.add_field(name="Field 3", value="This is the value for field 3", inline=False)
  
  await interaction.response.send_message(embed=embed)

class View(discord.ui.View):
  @discord.ui.button(label="Click me!", style=discord.ButtonStyle.red, emoji="👍")
  async def button_callback(self: Self, button, interaction: discord.Interaction):
    await button.response.send_message("you have clicked the button !")

@client.tree.command(name="button", description="displaying a button", guild=discord.Object(id=1461751770366869574))
async def on_button_click(interaction: discord.Interaction):
  await interaction.response.send_message(view=View())

class Menu(discord.ui.Select):
  def __init__(self: Self):
    options = [
      discord.SelectOption(label="Red", description="Choose Red color", emoji="🟥"),
      discord.SelectOption(label="Green", description="Choose Green color", emoji="🟩"),
      discord.SelectOption(label="Blue", description="Choose Blue color", emoji="🟦"),
    ]
    super().__init__(placeholder="Choose a color...", min_values=1, max_values=2, options=options)

  async def callback(self: Self, interaction: discord.Interaction):
    await interaction.response.send_message(f'You selected: {", ".join(self.values)}')

class MenuView(discord.ui.View):
  def __init__(self: Self, *args):
    super().__init__(*args)
    self.add_item(Menu())

@client.tree.command(name="menu", description="displaying a menu", guild=discord.Object(id=1461751770366869574))
async def on_menu(interaction: discord.Interaction):
  await interaction.response.send_message(view=MenuView())

# 클라이언트 실행
client.run(os.getenv('DISCORD_TOKEN'))