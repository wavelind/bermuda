import asqlite
import discord
from discord import app_commands
from discord.ext import commands


class Freeform(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    """
    @Curator
    def get_freeform_grade()
    
    @Curator
    def accept_freeform()
    
    @Members
    def submit_freeform()
    
    @Members
    def get_past_freeforms()
    """