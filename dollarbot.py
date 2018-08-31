#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import datetime
import asyncio
from dotenv import load_dotenv
import discord
from discord.ext import commands

import extractor

load_dotenv('.env.local' if (os.path.isfile('.env.local')) else '.env')

client = commands.Bot(command_prefix='!')

async def update_dollar():
    await client.wait_until_ready()
    channel = client.get_channel(os.getenv('DISCORD_CHANNEL'))
    
    while not client.is_closed:
        timestamp = datetime.datetime.now().strftime('%A at %H:%M')
        dolar = extractor.dolar_average()
        if dolar:
            new_topic = 'Dólar promedio ${:,.2f}'.format(dolar) + ' (Última actualización: {timestamp})'.format(timestamp=timestamp)
            await client.edit_channel(channel, topic=new_topic)
        await asyncio.sleep(1800)

@client.command(pass_context=True, name='dolar') # Yes, with one L
async def print_detailed_values(ctx, banco=None):
    print ('Consulta', banco)
    if banco:
        await client.send_message(ctx.message.channel, extractor.get_one(banco))
    else:
        await client.send_message(ctx.message.channel, extractor.detailed_list())

@client.event
async def on_ready():
    print('Logged in')
    client.loop.create_task(update_dollar())

client.run(os.getenv('DISCORD_TOKEN'))
