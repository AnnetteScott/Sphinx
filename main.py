#import discord #import all the necessary modules
from discord.ext import commands, tasks
import os
from datetime import datetime, timedelta
from replit import db
from keep_alive import keep_alive

bot = commands.Bot(command_prefix='!') #define command decorator

userCommands = ['helpMe', 'hello', 'remindMe', 'remindHelp', 'reminders', 'channelID', 'DELremind']
channelIDs = {'sphinx':937053360702509126, 'general':936900906488827936, 'links':936905539739353128, 'important-docs':936905648128532540, 'food':936905748447895552, 'bills':936918392076664873}

@bot.event
async def on_message(message):
    if message.content.startswith('!remindMe'):
        content = message.content.split(", ")
        name = content[1]
        date = content[2]
        how_often = content[3]
        channel = channelIDs[content[4]]
        if name in db.keys():
          await message.channel.send(name + ' is already in the database')
        else:

            db[name] = [date, how_often, channel]
            await message.channel.send('I have added: ' + name + ' to the database')
    elif message.content.startswith('!DELremind'):
      content = message.content.split(", ")
      key = content[1]
      del db[key]
      await message.channel.send('I have deleted ' + key)
    else:
        await bot.process_commands(message)


@bot.command(pass_context=True)
async def helpMe(ctx):
    await ctx.channel.send('The available commands are:')
    new_message = "" 
    for com in userCommands:
        new_message += com + ", "
    await ctx.channel.send(new_message) 
    

@bot.command(pass_context=True)
async def hello(ctx):
    await ctx.send('Hello Da Bebe!')


@bot.command(pass_context=True)
async def reminders(ctx):
    reminder_keys = db.keys()
    if reminder_keys != set():
        await ctx.channel.send('Your current reminders are:')
        for key in reminder_keys:
            await ctx.channel.send(key + " next occurs on " + db[key][0] + " and happens every " + db[key][1])
        await ctx.channel.send('That is all of your reminders')
    else:
        await ctx.channel.send('You have no reminders')



@bot.command(pass_context=True)
async def remindHelp(ctx):
   await ctx.channel.send('Formating to add a new reminder: !remindMe, name, date in dd/mm/yy, how often in xday xmonth xyear, channelID(use !channelID to get the ID')



@bot.command(pass_context=True)
async def channelID(ctx):
   await ctx.channel.send(ctx.channel)



@tasks.loop(minutes=80)
async def reminder_due():
    reminder_keys = db.keys()
    if reminder_keys != set():
        for key in reminder_keys:
            today_date = str(datetime.now() + timedelta(hours=13)).split(" ")[0].split('-')
            user_todayDate = today_date[2] + "/" + today_date[1] + "/" + today_date[0][2:]
            reminder_date = db[key][0]
            if user_todayDate == reminder_date:
                channel = bot.get_channel(db[key][2])
                how_often = db[key][1].split(' ')
                daily = int(how_often[0].split('d')[0])
                montly = int(how_often[1].split('m')[0])
                year = int(how_often[2].split('y')[0])
                get_new_date(key, reminder_date, daysAdd=daily, monthly=montly, yearly=year)
                await channel.send(key + " is occuring/due today!")
                next_date = db[key][0]
                await channel.send("It will next occur on: " + str(next_date))


def get_new_date(key, date, daysAdd=0, monthsAdd=0, yearsAdd=0, monthly=0, yearly=0):
    oDay = int(date.split("/")[0])
    oMonth = int(date.split("/")[1])
    oYear = int(date.split("/")[2])

    nDays = oDay + daysAdd
    nMonth = oMonth + monthly + monthsAdd
    nYear = oYear + yearly + yearsAdd
    if nMonth > 12:
        nYear += (nMonth // 12)
        nMonth = nMonth % 12
        

    while nDays > get_month_day(nMonth):
        #nMonth += 1
        nDays -= get_month_day(nMonth)
        nMonth += 1

    fMonth = nMonth % 12
    fYear = nYear + (nMonth // 12)
    fDays = nDays

    if nDays < 10:
        fDays = "0" + str(nDays)

    fDate = str(fDays) + '/' + str(fMonth) + '/' + str(fYear)
    db_object = db[key]
    db[key] = [fDate, db_object[1], db_object[2]]


def get_month_day(month):
    if month == 1: #Jan
        return 31
    elif month == 2: #Feb
        return 28
    elif month == 3: #Mar
        return 31
    elif month == 4: #Apr
        return 30
    elif month == 5: #May
        return 31
    elif month == 6: #Jun
        return 30
    elif month == 7: #Jul
        return 31
    elif month == 8: #Aug
        return 31
    elif month == 9: #Sep
        return 30
    elif month == 10: #Oct
        return 31
    elif month == 11: #Nov
        return 30
    elif month == 12: #Dec
        return 31
    else:
        return 30
    

@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))
    reminder_due.start()

keep_alive()    
bot.run(os.environ['TOKEN'])
