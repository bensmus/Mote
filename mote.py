import os
from discord.ext import commands

TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='!mote ')

SHRUG = r'¯\\\_(ツ)\_/¯'

save_help_string = (
    'intent: save text to your library of texts and give it an id and a label\n'
    'usage: !mote save <id> <text> <label (optional)>\n'
    f'example: !mote save shrug {SHRUG} emoticon'
)

id_help_string = (
    'intent: display text saved in your library based on id\n'
    'usage: !mote id <id>\n'
    f'example: !mote id shrug --> displays {SHRUG}'
)


@bot.command(name='save', help=save_help_string)
async def save(ctx):
    response = 'save command detected'
    await ctx.send(response)


@bot.command(name='id', help=id_help_string)
async def save(ctx):
    response = 'id command detected'
    await ctx.send(response)

bot.run(TOKEN)
