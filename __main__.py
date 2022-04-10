from client import Dispy
from constants import config

client = Dispy()
client.run(config.bot.token)
