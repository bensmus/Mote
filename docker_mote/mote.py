# standard library
import os

# discord library
import discord
from discord.ext import commands

# redis for storing persistent data about prefixes and saved entries
import redis

# for finding the edit distance between two words
# Did you mean the _____ command?
import nltk

TOKEN = os.getenv('DISCORD_TOKEN')
SHRUG = r'¯\_(ツ)_/¯'
DEFAULT_PREFIX = '#'

# redis url consists of ip, port, password
# could also have username in general but I don't think redis has usernames...
# (url scheme)
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")

# This does not work. Container has it's own IP. When you say localhost you're reffering to containers own port.
# REDIS_URL = "redis://:" + REDIS_PASSWORD + "@localhost:6379"

# https://stackoverflow.com/questions/38731998/do-docker-container-ips-change-on-restart
# https://stackoverflow.com/questions/41768157/how-to-link-container-in-docker
r = redis.Redis(host='redis_container',
                password=REDIS_PASSWORD,
                decode_responses=True)


def get_close_word(string, words):
    for word in words:
        if nltk.edit_distance(string, word) <= 2:
            return word


async def determine_prefix(bot, message):
    guild = message.guild
    if guild:

        # try to get prefix, if the bot has been on the server before
        prefix = r.hget('prefix', guild.id)

        # ok, we haven't visited server
        # set prefix to default
        if not prefix:
            r.hset('prefix', guild.id, DEFAULT_PREFIX)
            # r.save()  # forced save does not work on Heroku Redis for some reason
            return DEFAULT_PREFIX

        return prefix

    return DEFAULT_PREFIX


# discord bot command_prefix can be linked to a callable
# callable occurs every message
bot = commands.Bot(command_prefix=determine_prefix)


@bot.event
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


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CommandNotFound):
        string = ctx.message.content[1:]
        words = {str(command) for command in bot.commands}
        close_word = get_close_word(string, words)

        response = ':x:  ' + str(error)
        if close_word:
            response += f", did you mean \"{close_word}\"?  :eyes:"

        await ctx.send(response)

    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f':x:  ' + str(error))


save_help_string = (
    'Save text with ID and label.\n'
    '- if you invoke (type it) the command in a DM, it will save to your '
    'personal library.\n'
    '- if you invoke it in a server text channel, '
    'it will save to the channel library.'
)

get_help_string = 'Display entries based on ID.'
delete_help_string = 'Deletes entries based on ID.'
dump_help_string = 'Displays all your entries.'
prefix_help_string = 'Change the prefix used by the discord bot.'


@bot.command(name='save', help=save_help_string)
async def save(ctx, text_id, text):

    # detect DM
    if isinstance(ctx.channel, discord.channel.DMChannel):
        savetype = ctx.author
        emoji = ':person_standing:'

    else:
        emoji = ':person_standing:' * 3
        savetype = ctx.channel

    response = (
        f'ID: `{text_id}`\n'
        f'Text: `{text}`\n'
        f'Saved to `{savetype}` {emoji} library  :white_check_mark:'
    )

    # redis store (text_id, text) @ library
    key = str(savetype.id) + ':' + text_id
    r.hset('library', key, text)

    # redis store text_ids that belong to user or channel
    r.sadd(savetype.id, text_id)

    await ctx.send(response)


@bot.command(name='get', help=get_help_string)
async def get(ctx, text_id):

    # detect DM
    if isinstance(ctx.channel, discord.channel.DMChannel):
        key = str(ctx.author.id) + ':' + text_id

    else:
        key = str(ctx.channel.id) + ':' + text_id

    value = r.hget('library', key)

    if value == None:
        await ctx.send('Nonexistent ID  :robot:')

    else:
        await ctx.send(value)


@bot.command(name='delete', help=delete_help_string)
async def delete(ctx, *text_ids):

    # detect DM
    if isinstance(ctx.channel, discord.channel.DMChannel):
        delete_as = ctx.author.id

    else:
        delete_as = ctx.channel.id

    # remove the id from the id's that are associated with author/channel
    deleted = r.srem(delete_as, *text_ids)  # unpacking argument list

    if deleted:
        # remove the id and text from the library
        # get a tuple of delete_as + : + text_id
        keys = tuple(map(lambda text_id: str(
            delete_as) + ':' + text_id, text_ids))
        r.hdel('library', *keys)

        await ctx.send('ID(s) deleted  :white_check_mark:')

    else:
        await ctx.send('Nonexistent ID  :robot:')


@bot.command(name='dump', help=dump_help_string)
async def dump(ctx):

    # the channel or author that we are dumping as
    dump_as = None

    # detect DM
    if isinstance(ctx.channel, discord.channel.DMChannel):
        dump_as = ctx.author.id

    else:
        dump_as = ctx.channel.id

    dump_ids = r.smembers(dump_as)

    if dump_ids:  # not None or {}

        dump_ids = list(dump_ids)
        dump_ids.sort()

        dump_string = ''

        for text_id in dump_ids:
            dump_string += (text_id + '\n')

        await ctx.send(dump_string)

    else:
        await ctx.send('No ID\'s found to dump  :robot:')


def prefix_check(prefix, old_prefix):
    if len(prefix) == 1:
        if not (prefix.isdigit() or prefix.isalpha()):
            if prefix != '@':
                return True, f'Prefix changed from {old_prefix} to {prefix}  :white_check_mark:'
            return False, 'Prefix cannot be changed to @  :x:'
        return False, 'Prefix cannot be number or letter  :x:'
    return False, 'Prefix cannot be more than one character long  :x:'


@ bot.command(name='prefix', help=prefix_help_string)
async def prefix(ctx, prefix):
    guild = ctx.guild
    if guild:
        old_prefix = r.hget('prefix', ctx.guild.id)
        passed, response = prefix_check(prefix, old_prefix)

        if passed:
            # go into redis prefix hash
            r.hset('prefix', ctx.guild.id, prefix)

        await ctx.send(response)

    else:
        await ctx.send('Prefix command cannot be used in DM channels  :x:')


bot.run(TOKEN)
