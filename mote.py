# Heroku will run the following command to resolve dependencies
# pip install -r requirements.txt

# if an environment variable has spaces in it, it needs quotes around it
# single quotes '' and "" behave differently only if we have substitutions

import os
import discord

TOKEN = os.getenv('DISCORD_TOKEN')

client = discord.Client()


@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

client.run(TOKEN)
