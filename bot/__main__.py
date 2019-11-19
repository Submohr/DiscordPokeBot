import bot
from config import Config

client = bot.PokeBot.get_client()
DISCORD_TOKEN = Config.DISCORD_TOKEN
client.run(DISCORD_TOKEN)
