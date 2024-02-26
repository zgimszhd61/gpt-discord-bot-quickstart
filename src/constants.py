from dotenv import load_dotenv
import os
import dacite
import yaml
from typing import Dict, List, Literal

from src.base import Config

load_dotenv()

# 加载 config.yaml
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
CONFIG: Config = dacite.from_dict(
    Config, yaml.safe_load(open(os.path.join(SCRIPT_DIR, "config.yaml"), "r"))
)

BOT_NAME = CONFIG.name  # 机器人名称
BOT_INSTRUCTIONS = CONFIG.instructions  # 机器人指示
EXAMPLE_CONVOS = CONFIG.example_conversations  # 示例对话

DISCORD_BOT_TOKEN = os.environ["DISCORD_BOT_TOKEN"]
DISCORD_CLIENT_ID = os.environ["DISCORD_CLIENT_ID"]
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
DEFAULT_MODEL = os.environ["DEFAULT_MODEL"]

ALLOWED_SERVER_IDS: List[int] = []
server_ids = os.environ["ALLOWED_SERVER_IDS"].split(",")
for s in server_ids:
    ALLOWED_SERVER_IDS.append(int(s))

SERVER_TO_MODERATION_CHANNEL: Dict[int, int] = {}
server_channels = os.environ.get("SERVER_TO_MODERATION_CHANNEL", "").split(",")
for s in server_channels:
    values = s.split(":")
    SERVER_TO_MODERATION_CHANNEL[int(values[0])] = int(values[1])

# 发送消息，创建公共线程，发送线程消息，管理消息，管理线程，读取消息历史记录，使用斜线命令
BOT_INVITE_URL = f"https://discord.com/api/oauth2/authorize?client_id={DISCORD_CLIENT_ID}&permissions=328565073920&scope=bot"

MODERATION_VALUES_FOR_BLOCKED = {
    "harassment": 0.5,
    "harassment/threatening": 0.1,
    "hate": 0.5,
    "hate/threatening": 0.1,
    "self-harm": 0.2,
    "self-harm/instructions": 0.5,
    "self-harm/intent": 0.7,
    "sexual": 0.5,
    "sexual/minors": 0.2,
    "violence": 0.7,
    "violence/graphic": 0.8,
}

MODERATION_VALUES_FOR_FLAGGED = {
    "harassment": 0.5,
    "harassment/threatening": 0.1,
    "hate": 0.4,
    "hate/threatening": 0.05,
    "self-harm": 0.1,
    "self-harm/instructions": 0.5,
    "self-harm/intent": 0.7,
    "sexual": 0.3,
    "sexual/minors": 0.1,
    "violence": 0.1,
    "violence/graphic": 0.1,
}

SECONDS_DELAY_RECEIVING_MSG = (
    3  # 给机器人一个响应的延迟，以便它能够捕获多个消息
)
MAX_THREAD_MESSAGES = 200
ACTIVATE_THREAD_PREFX = "💬✅"
INACTIVATE_THREAD_PREFIX = "💬❌"
MAX_CHARS_PER_REPLY_MSG = (
    1500  # Discord 有 2k 限制，我们只分为 1.5k 消息
)

AVAILABLE_MODELS = Literal[
    "gpt-3.5-turbo", "gpt-4", "gpt-4-1106-preview", "gpt-4-32k"
]  # 可用模型
