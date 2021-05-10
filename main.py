import os
import discord
from dotenv import load_dotenv
import datetime
from pytz import timezone
import re

load_dotenv()

client = discord.Client()
hackNightRegex = '/next ((?:s?hr?|cr|u|o)(?:e|a|i|o|u)?c?o?w?(?:k|c|p|t|oo?|u(?:t|p)?)(?:e|a)?(?:s|y|lacka)?(?:\s|-)?(?:n|b)?(?:e|i|oo?|a)?u?(?:k|w|g|c|o|t)?k?a?(?:ey|ht|ky|e|t|wu|o(?:p|t)?|lacka))/i'

tz = timezone('US/Eastern')

def setTime(date, hours, mins, secs):
    date = date.replace(hour=hours, minute=mins, second=secs)
    return date

def getSecs(ts):
    return int(datetime.datetime.timestamp(ts)/1000)


def isHappening():

    time = datetime.datetime.now(tz)

    day = time.strftime("%w")
    hours = time.hour
    mins = time.minute

    print(day, hours, mins)

    # Check if today is Wednesday
    if day==3:
        # Check if current time is between 15:30 and 23:59 ET
        if (hours > 15 or (hours == 15 and minutes >= 30)) and (hours < 23 or (hours == 23 and minutes <= 59)):
            return true

    # Check if today is Saturday
    if day==6:
        # Check if current time is between 20:30 and 23:59 ET
        if (hours >= 20 and mins >= 30) and (hours <= 23 and mins <= 59):
            return true

    return false

def nextDate():
    d = datetime.datetime.now()
    today = datetime.datetime.now(tz).strftime("%w")

    if today in range(0,3):
         d.replace(day = d.day + ((3 + 7 - d.strftime('%w')) % 7)); # Sets to date of the next Wednesday
         setTime(d, 15, 30, 0); # Sets time to 15:30 Eastern
    elif today in range(4,6):
        # Today is Thu - Sat
        d.replace(day = d.day + ((6 + 7 - d.strftime('%w')) % 7)); # Sets to date of the next Saturday
        setTime(d, 20, 30, 0); # Sets time to 20:30 Eastern

    return getSecs(d)

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    channel = client.get_channel(int(os.getenv('CHANNEL_TEST')))

    if message.author == client.user:
        return

    message = message.content
    print(message)
    textMatch = re.findall(message,hackNightRegex)#search
    print(textMatch)
    if textMatch!=None:
        nextHackNight = nextDate()
        prompt = f"The next _{textMatch[1]}_ is *<!date^{nextHackNight}^{date_short_pretty} at {time}|[Open Discord To View]>* your time. See you there!"
        await channel.send(prompt)
    await channel.send('Ack')

client.run(os.getenv('BOT_TOKEN'))
