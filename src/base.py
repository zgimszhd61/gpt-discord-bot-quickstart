from dataclasses import dataclass
from typing import Optional, List

# 分隔符标记
SEPARATOR_TOKEN = ""

# 消息类，用于表示对话中的消息
@dataclass(frozen=True)
class Message:
    user: str  # 用户名
    text: Optional[str] = None  # 文本内容，默认为空

    # 渲染消息
    def render(self):
        result = self.user + ":"
        if self.text is not None:
            result += " " + self.text
        return result

# 对话类，包含一系列消息
@dataclass
class Conversation:
    messages: List[Message]  # 消息列表

    # 在对话前插入消息
    def prepend(self, message: Message):
        self.messages.insert(0, message)
        return self

    # 渲染对话
    def render(self):
        return f"\n{SEPARATOR_TOKEN}".join(
            [message.render() for message in self.messages]
        )

# 配置类，包含对话系统的配置信息
@dataclass(frozen=True)
class Config:
    name: str  # 名称
    instructions: str  # 指示
    example_conversations: List[Conversation]  # 示例对话列表

# 线程配置类，包含模型相关的配置信息
@dataclass(frozen=True)
class ThreadConfig:
    model: str  # 模型名称
    max_tokens: int  # 最大标记数
    temperature: float  # 温度

# 提示类，用于呈现对话系统提示
@dataclass(frozen=True)
class Prompt:
    header: Message  # 头部消息
    examples: List[Conversation]  # 示例对话列表
    convo: Conversation  # 当前对话

    # 渲染完整提示信息
    def full_render(self, bot_name):
        messages = [
            {
                "role": "system",
                "content": self.render_system_prompt(),
            }
        ]
        for message in self.render_messages(bot_name):
            messages.append(message)
        return messages

    # 渲染系统提示信息
    def render_system_prompt(self):
        return f"\n{SEPARATOR_TOKEN}".join(
            [self.header.render()]
            + [Message("System", "示例对话:").render()]
            + [conversation.render() for conversation in self.examples]
            + [
                Message(
                    "System", "现在，您将使用当前的实际对话。"
                ).render()
            ]
        )

    # 渲染消息
    def render_messages(self, bot_name):
        for message in self.convo.messages:
            if not bot_name in message.user:
                yield {
                    "role": "user",
                    "name": message.user,
                    "content": message.text,
                }
            else:
                yield {
                    "role": "assistant",
                    "name": bot_name,
                    "content": message.text,
                }
