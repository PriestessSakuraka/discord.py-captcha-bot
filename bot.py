from captcha.image import ImageCaptcha
import os
import random
import string
import asyncio
import re
import datetime

import discord
from discord.ext import commands


def randomStr(n=5):
    randlst = [random.choice(string.digits + string.ascii_lowercase + string.ascii_uppercase) for i in range(n)]
    return ''.join(randlst)


def captcha(id, n=5, word=None):
    string = None

    if word is None:
        string = randomStr(n)
    else:
        string = word

    print(string)

    if string is None: return print("Could not generate captcha.")

    image = ImageCaptcha()
    image.generate(string)

    image.write(string, f'{id}.png')
    return string


TOKEN = ''
intents = discord.Intents.all()

intents.members = True
bot = commands.Bot(command_prefix='.', intents=intents)


@bot.event
async def on_ready():
    print('start!')

@bot.command()
async def test(ctx, arg=None):
    channel = bot.get_channel(864881388766887987)

    await channel.send(ctx.author.mention)
    await captchaMsg_forCmd(ctx, channel, title='認証してください。', word=arg)

@bot.command()
async def a(ctx):
    channel = bot.get_channel(1017815727182454784)
    if ctx.channel.id is not channel.id: return

    words = ''.join([random.choice(string.ascii_uppercase) for i in range(5)])
    await captchaMsg_forCmd(ctx, channel, word=words, level=1)

@bot.command()
async def b(ctx):
    channel = bot.get_channel(1017815321735856209)
    if ctx.channel.id is not channel.id: return

    words = ''.join([random.choice(string.digits + string.ascii_uppercase) for i in range(6)])
    await captchaMsg_forCmd(ctx, channel, word=words, level=2)

@bot.command()
async def c(ctx):
    channel = bot.get_channel(1017815388932821053)
    if ctx.channel.id is not channel.id: return

    words = randomStr(7)
    await captchaMsg_forCmd(ctx, channel, word=words, level=3)


async def captchaMsg_forCmd(ctx, ch, word=None, check=None, level=None):
    db_channel = bot.get_channel(1017817332493582356)

    captcha_string = captcha(ctx.author.id, word=word)

    false_text = f'正解は || {captcha_string} || です。\n(黒い部分を押すと答えが見えるよ！)'

    embed = discord.Embed(description='画像に表示された文字を入力してください。')
    await ch.send(embed=embed)
    await ch.send(file=discord.File(f'./{ctx.author.id}.png'))
    start = datetime.datetime.now()

    os.remove(f'./{ctx.author.id}.png')

    check = lambda msg: msg.author.id == ctx.author.id and re.match('^[A-Za-z0-9]*$', msg.content) and msg.channel.id == ch.id

    try:
        msg = await bot.wait_for('message', check=check, timeout=30)

        if msg.content == captcha_string:
            diff = datetime.datetime.now() - start
            score = diff.total_seconds()
            await ch.send(f'{msg.author.mention} 大正解！！おめでとう～！')
            await db_channel.send(f'レベル{level}が{score}秒でクリアされました！')
        elif msg.content != captcha_string:
            await ch.send(f'{msg.author.mention} 不正解です。\nまたチャレンジしたい場合はコマンドをもう一度使ってください。')
            await ch.send(false_text)

    except asyncio.TimeoutError:
        await ch.send('時間切れです。\nまたチャレンジしたい場合はコマンドをもう一度使ってください。')
        await ch.send(false_text)
    else:
        return

bot.run(TOKEN)
