import operator
from typing import Literal

import discord
from discord import app_commands


# 음성 채널 접속 여부 확인
def is_in_voice():
  async def predicate(interaction: discord.Interaction) -> bool:
    if interaction.user.voice and interaction.user.voice.channel:
      return True
    # 음성 채널에 없으면 에러를 발생시키거나 False 반환
    raise app_commands.CheckFailure(
      "❌ 음성 채널에 접속한 상태에서만 팀 구성을 할 수 있습니다."
    )

  return app_commands.check(predicate)


# 사용할 수 있는 비교 연산자 정의 (타입 힌트용)
CompareType = Literal[">", "<", ">=", "<=", "=="]


# 채널 유저 인원 체크
def check_user_count(count: int, op: CompareType = ">="):
  # 문자열로 된 연산자를 실제 파이썬 비교 함수로 매핑
  ops = {
    ">": operator.gt,
    "<": operator.lt,
    ">=": operator.ge,
    "<=": operator.le,
    "==": operator.eq,
  }
  operation = ops.get(op)

  async def predicate(interaction: discord.Interaction) -> bool:
    channel = interaction.channel
    members = None

    if channel and hasattr(channel, "members"):
      members = channel.members
    elif interaction.user.voice and interaction.user.voice.channel:
      members = interaction.user.voice.channel.members
    else:
      members = []

    current_members = len(members)

    # 설정한 연산자에 따라 비교 실행 (예: current_members >= count)
    if not operation(current_members, count):
      # 에러 메시지를 연산자에 맞춰 한국어로 변환
      msg_map = {
        ">=": f"최소 {count}명 이상",
        "==": f"정확히 {count}명",
        ">": f"{count}명 초과",
        "<=": f"최대 {count}명 이하",
        "<": f"{count}명 미만",
      }

      raise app_commands.CheckFailure(
        f"❌ 인원수 조건이 맞지 않습니다. (현재 {current_members}명, 조건: {msg_map.get(op)})"
      )

    return True

  return app_commands.check(predicate)
