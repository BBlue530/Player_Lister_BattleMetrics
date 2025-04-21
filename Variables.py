from dotenv import load_dotenv
import os

load_dotenv(dotenv_path="Token.env")

BOT_TOKEN = os.getenv("BOT_TOKEN")