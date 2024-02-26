from src.constants import (
    ALLOWED_SERVER_IDS,
)
import logging
from src.base import Message
from discord import Message as DiscordMessage
from typing import Optional, List
import discord
from src.constants import MAX_CHARS_PER_REPLY_MSG, INACTIVATE_THREAD_PREFIX

# 获取logger对象
logger = logging.getLogger(__name__)

# 将 Discord 中的消息对象转换为自定义的消息对象
def discord_message_to_message(message: DiscordMessage) -> Optional[Message]:
    if (
        message.type == discord.MessageType.thread_starter_message
        and message.reference.cached_message
        and len(message.reference.cached_message.embeds) > 0
        and len(message.reference.cached_message.embeds[0].fields) > 0
    ):
        # 如果是线程的初始消息，且有引用的消息，且该消息有嵌入内容且至少有一个字段
        field = message.reference.cached_message.embeds[0].fields[0]
        if field.value:
            return Message(user=field.name, text=field.value)
    else:
        # 如果不是线程的初始消息，或者没有引用的消息
        if message.content:
            return Message(user=message.author.name, text=message.content)
    return None

# 将长消息拆分为多条不超过限制长度的消息
def split_into_shorter_messages(message: str) -> List[str]:
    return [
        message[i : i + MAX_CHARS_PER_REPLY_MSG]
        for i in range(0, len(message), MAX_CHARS_PER_REPLY_MSG)
    ]

# 检查上一条消息是否已经过时
def is_last_message_stale(
    interaction_message: DiscordMessage, last_message: DiscordMessage, bot_id: str
) -> bool:
    return (
        last_message
        and last_message.id != interaction_message.id
        and last_message.author
        and last_message.author.id != bot_id
    )

# 关闭线程
async def close_thread(thread: discord.Thread):
    await thread.edit(name=INACTIVATE_THREAD_PREFIX)
    await thread.send(
        embed=discord.Embed(
            description="**Thread closed** - Context limit reached, closing...",
            color=discord.Color.blue(),
        )
    )
    await thread.edit(archived=True, locked=True)

# 检查是否应该阻塞操作
def should_block(guild: Optional[discord.Guild]) -> bool:
    if guild is None:
        # 不支持直接消息
        logger.info(f"DM not supported")
        return True

    if guild.id and guild.id not in ALLOWED_SERVER_IDS:
        # 不允许在该服务器中进行操作
        logger.info(f"Guild {guild} not allowed")
        return True
    return False
