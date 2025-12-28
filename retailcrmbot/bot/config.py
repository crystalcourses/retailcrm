from dataclasses import dataclass
from os import getenv
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    bot_token: str
    api_url: str


def load_config() -> Config:
    return Config(
        bot_token=getenv("BOT_TOKEN"),
        api_url=getenv("API_URL")
    )


config = load_config()