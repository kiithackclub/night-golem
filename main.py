import os
import discord
from discord.ext import tasks
from dotenv import load_dotenv
import datetime
from pytz import timezone
import re

load_dotenv()

client = discord.Client()
hackNightRegex = "next ((?:s?hr?|cr|u|o)(?:e|a|i|o|u)?c?o?w?(?:k|c|p|t|oo?|u(?:t|p)?)(?:e|a)?(?:s|y|lacka)?(?:\s|-)?(?:n|b)?(?:e|i|oo?|a)?u?(?:k|w|g|c|o|t)?k?a?(?:ey|ht|ky|e|t|wu|o(?:p|t)?|lacka))"
tz = timezone('US/Eastern')

def setTime(date, hours, mins, secs):
    date = date.replace(hour=hours, minute=mins, second=secs)
    return date

def happeningNow():
    
    time = datetime.datetime.now(tz)

    day = int(time.strftime("%w"))
    hours = int(time.hour)
    mins = int(time.minute)
    # Check if today is Wednesday
    if day==3:
        # Check if current time is between 15:30 and 23:59 ET
        if (hours > 15 or (hours == 15 and mins >= 30)) and (hours < 23 or (hours == 23 and mins <= 59)):
            return True

    # Check if today is Saturday
    if day==6:
        # Check if current time is between 20:30 and 23:59 ET
        if (hours >= 20 and mins >= 30) and (hours <= 23 and mins <= 59):
            return True
    return False

def nextDate():
    d = datetime.datetime.now(tz)
    today = int(datetime.datetime.now(tz).strftime("%w"))
    if today in range(0,4):
        d = d.replace(day = d.day + (((3 + 7 - int(d.strftime('%w'))) % 7))) # Sets to date of the next Wednesday
        d = setTime(d, 15, 30, 0); # Sets time to 15:30 Eastern
    elif today in range(4,7):
        # Today is Thu - Sat
        d = d.replace(day = d.day + (((6 + 7 - int(d.strftime('%w'))) % 7))) # Sets to date of the next Saturday
        d = setTime(d, 20, 30, 0); # Sets time to 20:30 Eastern
    return d

def genTimeMessage(textMatch):
    prompt=''
    if happeningNow():
        prompt = f'_{textMatch[1].title()}_ is happening right now, what are you still doing here!? Join the call!\nhttps://hack.af/night'
    else:
        nextHackNight = nextDate().astimezone(timezone('Asia/Kolkata'))
        prompt = f'The next _{textMatch[1]}_ is **{nextHackNight.strftime("%b %d at %I:%M %p")} IST**. See you there!'
    return prompt

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    checkUpdate.start(client.get_channel(int(os.getenv('CHANNEL_ID'))))

@client.event
async def on_message(message):
    channel = client.get_channel(int(os.getenv('CHANNEL_ID')))
    if message.author == client.user:
        return

    message = message.content
    textMatch = re.search(hackNightRegex,message)
    if textMatch!=None:
       await channel.send(genTimeMessage(textMatch))

@tasks.loop(minutes=2)
async def checkUpdate(channel):
    prompt=None
    mutex = int(os.getenv('MUTEX'))
    if happeningNow():
        if mutex > 0:
            prompt = f':crescent_moon: It\'s **Hack Night!**\n\nMeet some new people, build something cool, talk about it. There are no prizes or expectations—just have fun!\n\nThe Hack Night call link has been reactivated by yours truly the Night Golem.\n\n:arrow_right: Join Hack Night (https://hack.af/night)'
            mutex-= 1
            await channel.send(prompt)
    else:
        mutex = 1
    os.environ['MUTEX'] = str(mutex)

client.run(os.getenv('BOT_TOKEN'))