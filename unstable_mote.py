# standard library
import os

# discord library
import discord
from discord.ext import commands

# redis for storing persistent data about prefixes and saved entries
import redis
r = redis.StrictRedis('localhost', 6379, charset="utf-8",
                      decode_responses=True)

TOKEN = os.getenv('DISCORD_TOKEN')
SHRUG = r'¯\_(ツ)_/¯'

bot = commands.Bot(command_prefix='#')


@ bot.event
async def on_guild_join(guild):
    response = (
        'Joined :white_check_mark:\n'
        '`-` My prefix is: `#`\n'
        '`-` To change prefix: `#prefix <prefix>`\n'

        '*Mote can be used to store plain text like hyperlinks '
        'or emoticons!*\n'

        'Type `#help` for more details.\n'
        f'{SHRUG}'
    )

    general = discord.utils.get(guild.channels, name='general')
    await general.send(response)


save_help_string = (
    'Save text with ID and label. This command is context dependent.\n'
    '`-` if you invoke (type it) the command in a DM, it will save to your '
    'personal library\n'
    '`-` if you invoke it in a server text channel, '
    'it will save to the channel library.'
)

save_channel_help_string = (
    'Save text with ID and label. Visible to everyone on this channel, while on this server.'
)

# have a separator for both of them, first matches in personal library, then matches in channel library
id_help_string = (
    'Display entries based on ID, saved in your personal library and in channel library.'
)

prefix_help_string = (
    'Change the prefix used by the discord bot.'
)


# TODO: reorganize save_to_personal and save_to_channel
# because they are so similar
def save_to_personal(text, ctx, ID, label):
    """
    Saving to personal library is done when user types #save <id> <text> 
    into a DM with the bot. 
    """
    response = (
        f'ID: `{ID}`\n'
        f'Text: `{text}`\n'
        f'Label: `{label}`\n'
        f'Saved to `{ctx.author}` personal :person_standing: library :white_check_mark:'
    )

    key = str(ctx.author.id) + ':' + ID

    # str(label) is necessary because label could be None
    # in which case str(None) = 'None'
    value = text + ':' + str(label)
    r.hset('library', key, value)
    return response


def save_to_channel(text, ctx, ID, label):
    """
    Saving to channel library is done when user types #save <id> <text>
    into a channel on a server that has the bot.
    """

    channel_emoji = ':person_standing:' * 3
    response = (
        f'ID: `{ID}`\n'
        f'Text: `{text}`\n'
        f'Label: `{label}`\n'
        f'Saved to `{ctx.channel}` channel {channel_emoji} '
        f'library on `{ctx.guild}` :white_check_mark:'
    )

    key = str(ctx.channel.id) + ':' + ID

    # str(label) is necessary because label could be None
    # in which case str(None) = 'None'
    value = text + ':' + str(label)
    r.hset('library', key, value)
    return response


@bot.command(name='save', help=save_help_string)
async def save_text(ctx, ID, text, label=None):

    # detect DM
    if isinstance(ctx.channel, discord.channel.DMChannel):
        response = save_to_personal(text, ctx, ID, label)

    else:
        response = save_to_channel(text, ctx, ID, label)

    await ctx.send(response)


@bot.command(name='id', help=id_help_string)
async def get_text_by_id(ctx, ID):

    # detect DM
    if isinstance(ctx.channel, discord.channel.DMChannel):
        key = str(ctx.author.id) + ':' + ID

    else:
        key = str(ctx.channel.id) + ':' + ID

    value = str(r.hget('library', key))
    text = value.split(':')[0]

    await ctx.send(text)


'''
@bot.command(name='prefix', help=prefix_help_string)
async def change_prefix(ctx, prefix):
    old_prefix = bot.command_prefix
    response = f'prefix changed from {old_prefix} to {prefix}'
    bot.command_prefix = prefix
    await ctx.send(response)
'''

bot.run(TOKEN)
