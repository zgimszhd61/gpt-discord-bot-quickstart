# 导入所需模块和库
from typing import Optional, Tuple
import discord
from openai import OpenAI
from src.constants import (
    SERVER_TO_MODERATION_CHANNEL,
    MODERATION_VALUES_FOR_BLOCKED,
    MODERATION_VALUES_FOR_FLAGGED,
)
from src.utils import logger
from openai._compat import model_dump

# 创建OpenAI客户端
client = OpenAI()


def moderate_message(
    message: str, user: str
) -> Tuple[str, str]:  # [flagged_str, blocked_str]
    # 调用OpenAI的moderations.create方法进行内容审查
    moderation_response = client.moderations.create(
        input=message, model="text-moderation-latest"
    )
    # 提取审查结果中的分类分数
    category_scores = moderation_response.results[0].category_scores or {}
    # 转换分类分数为字典格式
    category_score_items = model_dump(category_scores)

    # 初始化违规内容和被屏蔽内容的字符串
    blocked_str = ""
    flagged_str = ""
    # 遍历分类分数字典
    for category, score in category_score_items.items():
        # 若分数超过被屏蔽阈值
        if score > MODERATION_VALUES_FOR_BLOCKED.get(category, 1.0):
            # 添加到被屏蔽内容字符串
            blocked_str += f"({category}: {score})"
            # 记录日志
            logger.info(f"blocked {user} {category} {score}")
            break
        # 若分数超过被标记阈值
        if score > MODERATION_VALUES_FOR_FLAGGED.get(category, 1.0):
            # 添加到被标记内容字符串
            flagged_str += f"({category}: {score})"
            # 记录日志
            logger.info(f"flagged {user} {category} {score}")
    # 返回被标记内容和被屏蔽内容的字符串元组
    return (flagged_str, blocked_str)


async def fetch_moderation_channel(
    guild: Optional[discord.Guild],
) -> Optional[discord.abc.GuildChannel]:
    # 若未提供服务器或服务器ID，则返回空
    if not guild or not guild.id:
        return None
    # 获取服务器对应的审查频道
    moderation_channel = SERVER_TO_MODERATION_CHANNEL.get(guild.id, None)
    # 若存在审查频道，则获取该频道对象并返回
    if moderation_channel:
        channel = await guild.fetch_channel(moderation_channel)
        return channel
    return None


async def send_moderation_flagged_message(
    guild: Optional[discord.Guild],
    user: str,
    flagged_str: Optional[str],
    message: Optional[str],
    url: Optional[str],
):
    # 若提供了服务器、被标记内容和被标记消息
    if guild and flagged_str and len(flagged_str) > 0:
        # 获取审查频道对象
        moderation_channel = await fetch_moderation_channel(guild=guild)
        # 若审查频道存在
        if moderation_channel:
            # 截取消息内容前100个字符（如果存在）
            message = message[:100] if message else None
            # 发送被标记消息到审查频道
            await moderation_channel.send(
                f"⚠️ {user} - {flagged_str} - {message} - {url}"
            )


async def send_moderation_blocked_message(
    guild: Optional[discord.Guild],
    user: str,
    blocked_str: Optional[str],
    message: Optional[str],
):
    # 若提供了服务器、被屏蔽内容和被屏蔽消息
    if guild and blocked_str and len(blocked_str) > 0:
        # 获取审查频道对象
        moderation_channel = await fetch_moderation_channel(guild=guild)
        # 若审查频道存在
        if moderation_channel:
            # 截取消息内容前500个字符（如果存在）
            message = message[:500] if message else None
            # 发送被屏蔽消息到审查频道
            await moderation_channel.send(f"❌ {user} - {blocked_str} - {message}")
