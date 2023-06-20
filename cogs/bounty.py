import asqlite
import discord
from discord import app_commands
from discord.ext import commands


class Bounty(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    """
    @Curators GOOD CONTEXT MENU?
    def post_bounty(title: str, description: str, reward: int, is_active: bool)
    
    @Curator
    def remove_bounty(bounty_title: str)
    
    @Curator
    def activate_bounty(bounty_title: str)
    
    @Curator CONTEXT MENU?
    def set_bounty_details()
    
    @Curator
    def get_bounty_submissions()
    
    @Curator
    def accept_bounty()
    
    @Curator
    def reject_bounty()
    
    @Curator
    def set_bounty_eligible()

    @Members BETTER OFF AS A CONTEXT MENU
    def submit_bounty()
    
    @Members
    def get_bounty_details(bounty_title: str)
    
    @Members 
    def claim_bounty(bounty_title: str)
    
    @Members
    def unclaim_bounty(bounty_title: str)
    
    @Members
    def claimed_bounties()
    
    @Members
    def get_past_bounties()
    """