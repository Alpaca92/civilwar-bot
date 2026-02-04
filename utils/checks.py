# utils/checks.py (공통 모듈)
from discord import app_commands
import discord

# 음성 채널 접속 여부 확인
def is_in_voice():
    async def predicate(interaction: discord.Interaction) -> bool:
        if interaction.user.voice and interaction.user.voice.channel:
            return True
        # 음성 채널에 없으면 에러를 발생시키거나 False 반환
        raise app_commands.CheckFailure("먼저 음성 채널에 접속해야 합니다!")

    return app_commands.check(predicate)