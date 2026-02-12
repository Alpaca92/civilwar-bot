import discord
from discord import app_commands
from discord.ext import commands

class DestoryCog(commands.Cog):
  def __init__(self, bot: commands.Bot) -> None:
    pass

  @app_commands.command(name="destroy", description="모든 유저의 역할 제거")
  async def destroy(self, interaction: discord.Interaction) -> None:
    guild = interaction.guild

    if guild is None:
      await interaction.response.send_message("❌ 이 명령어는 서버에서만 사용할 수 있습니다.", ephemeral=True)
      return

    await interaction.response.send_message("⚠️ 모든 유저의 역할을 제거하는 중입니다...")

    for member in guild.members:
      if not member.bot:
        try:
          await member.edit(roles=[])
        except Exception as e:
          print(f"❌ {member.display_name}의 역할 제거 실패: {e}")

    await interaction.followup.send("✅ 모든 유저의 역할이 성공적으로 제거되었습니다.")


async def setup(bot: commands.Bot) -> None:
  await bot.add_cog(DestoryCog(bot))
