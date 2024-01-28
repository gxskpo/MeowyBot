import discord
from discord.ext import commands
import typing as t
import re
import os
from openai import OpenAI

API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=API_KEY)


class ChatBot(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    system_message: t.Dict[str, str] = {
        'role': 'system',
        'content': "Te llamas Meowybot, eres un bot de chat,pueden haber mas de 1 personas en la conversación, podrás "
                   "identificarlas por su nombre contenido en los brackets DEBES responder de forma graciosa, breve y"
                   " casual usando el contexto de los últimos mensajes (a continuación)"
    }

    z: t.Dict[int, t.List[discord.Message]] = {}
    counter: t.Dict[int, int] = {}

    @commands.Cog.listener()
    async def on_message(self, m: discord.Message):
        self.z.setdefault(m.channel.id, [])
        self.counter.setdefault(m.channel.id, 0)
        if m.author.bot:
            return

        response = client.moderations.create(input=m.content)
        if response.results[0].flagged:
            return await m.add_reaction('<:AA_no_autorizo:1200860946894164049>')

        self.z[m.channel.id].append(m)
        self.counter[m.channel.id] += 1

        if self.counter[m.channel.id] > 10 or m.guild.me in m.mentions:
            async with m.channel.typing():
                messages = [{
                    'role': 'user',
                    'content': f'[{ms.author.name}]: {ms.content}' if not ms.author.bot else f"[Meowybot]:{ms.content}"
                } for ms in self.z[m.channel.id] if len(ms.content) < 200]

                response = client.chat.completions.create(
                    model='gpt-4-0125-preview',
                    messages=[self.system_message] + messages,
                    max_tokens=65
                )

                patron = r'\[.*?\]:'
                response_content = re.sub(patron, '', response.choices[0].message.content)
                if response_content.startswith(" "):
                    response_content = response_content[1:]
                my_message = await m.reply(response_content)
                self.z[m.channel.id].append(my_message)
                if len(self.z[m.channel.id]) > 15:
                    self.z[m.channel.id].pop(0)
                self.counter[m.channel.id] = 0


async def setup(bot: commands.Bot):
    await bot.add_cog(ChatBot(bot))
    print('ChatBot cargado')
    return
