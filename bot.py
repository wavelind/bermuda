import logging
import os
import random

from dotenv import load_dotenv
import discord
from discord.ext import commands

import utilities
import dialogue

guilds = (discord.Object(id=286651910058934273),  # Scrapyard
          discord.Object(id=844929908026900510))  # PYRE


logging.basicConfig(handlers=[logging.FileHandler("bermuda_operation.log", encoding="utf-8")])
discord.utils.setup_logging()

extensions = (
    'cogs.bank',
)


class Bermuda(commands.Bot):

    def __init__(self):

        super().__init__(
            command_prefix='b?',
            intents=discord.Intents.all(),
            owner_id=263093851051261952,

        )

    async def setup_hook(self):
        for extension in extensions:
            try:
                await self.load_extension(extension)
            except:
                print(f"Failed to load extension: {Exception}")

    async def on_ready(self):
        print(f'Logged in as {bermuda.user}')

    async def on_command_error(self, ctx, error):
        if ctx.error_handled:
            return

        if isinstance(error, commands.CommandNotFound):
            embed = utilities.EmbedBuilder.build_error_embed("Bermuda", random.choice(dialogue.error_descriptions))

            embed.add_field(name=":no_entry: Command Not Found",
                            value=f"Command ``{ctx.message.content}`` does not exist.")

            await ctx.send(embed=embed)

    async def get_context(self, message, *, cls=None):
        return await super().get_context(message, cls=cls or BermudaContext)


class BermudaContext(commands.Context):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._is_error_handled = False

    @property
    def error_handled(self):
        return self._is_error_handled

    @error_handled.setter
    def error_handled(self, value):
        self._is_error_handled = value


bermuda = Bermuda()


@bermuda.command()
@commands.is_owner()
async def sync(ctx):
    await bermuda.tree.sync()
    await ctx.send("Synced the command tree")


@bermuda.command()
async def source(ctx):
    await ctx.send("https://github.com/wavelind/bermuda")


@bermuda.command()
async def reload(ctx):
    for extension in extensions:
        try:
            await bermuda.reload_extension(extension)
            await ctx.send(f"Reloaded extension: {extension}")

        except Exception as e:
            await ctx.send(f"Failed to reload: {extension}")

if load_dotenv():
    bermuda.run(os.environ['TOKEN'])

else:
    print("Failed to load .env")