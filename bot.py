from twitchio.ext import commands
from config import config
from dialogflow import getAnswerFromDialogflow
import re 
import time
from db import Settings, Phrase, get_data_from_db, get_setting_value

import queue

from threading import Thread
import socket

chat_queue = queue.Queue()

use_rules = { 'use_db': False, 'use_dialogflow': False }

def get_db_use_setting(setting_name):
    setting_value = get_setting_value(setting_name)
    try:
        return bool(int(setting_value))
    except Exception:
        return False

def set_use_rule_from_db(setting_names):
    global use_rules
    for setting_name in setting_names:
        use_rules[setting_name] = get_db_use_setting(setting_name)

class myBot(commands.Bot):
  def stop(self):
    self._ws.teardown()
    self.loop.stop()

def get_chat_message(ctx):
  return f'@ {ctx.author.display_name}\n{ctx.content}\n' + ('_' * 50)

bot = myBot(
    # set up the bot
    irc_token=get_setting_value('irc_token'),
    client_id=get_setting_value('client_id'),
    nick=get_setting_value('nick'),
    prefix='!',
    initial_channels=get_setting_value('initial_channels', ',')
)

@bot.event
async def event_ready():
  set_use_rule_from_db(['use_db', 'use_dialogflow'])  
  print(f"{get_setting_value('nick')} is online!")
  ws = bot._ws
  await ws.send_privmsg(get_setting_value('initial_channels', ',')[0], "/me has landed!")

@bot.event
async def event_message(ctx):
  if ctx.author.name.lower() == get_setting_value('nick').lower():
    return
  chat_queue.put(get_chat_message(ctx))
  if not re.fullmatch('^![b,б][o,о]?[t,т]? .*', ctx.content):
    return
  message_content = re.sub('^![b,б][o,о]?[t,т]?','',ctx.content).strip()
  bot_answer = None
  if bot_answer is None:
    bot_answer = get_data_from_db(Phrase, "text", message_content, "answer")
  if bot_answer is None:
    bot_answer = getAnswerFromDialogflow(ctx.content)
  if bot_answer is None or bot_answer == '':
    bot_answer = 'Я не могу ответить на этот вопрос'
  await ctx.channel.send(bot_answer)

# bot.py
if __name__ == "__main__":
  bot.run()