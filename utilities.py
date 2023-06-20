import discord.ext
import logging
import datetime


class CogLogger:
    def __init__(self, cog: discord.ext.commands.Cog):
        self.cog = cog

    """
    This class in of itself is not particularly necessary, however, I hope to expand upon it in the future
    """

    def command_executed(self, command_name: str, invoker: discord.Member, *parameters):
        logging.info(
            f"\n[{self.cog.qualified_name}] Command executed at {datetime.datetime.now(datetime.timezone.utc)}"
            f"\nCommand: \"{command_name}\" invoked by {invoker.display_name} ({invoker.id})"
            f"\nParameters: {parameters}"
        )

    def command_failed(self, command_name: str, invoker: discord.Member, error, *parameters):
        logging.info(
            f"\n[{self.cog.qualified_name}] Command failed at {datetime.datetime.now(datetime.timezone.utc)}"
            f"\nError: {error}"
            f"\nCommand: \"{command_name}\" invoked by {invoker.display_name} ({invoker.id})"
            f"\nParameters: {parameters}"
        )

    def listener_executed(self, listener_name: str):
        logging.info(
            f"\n[{self.cog.qualified_name}] Listener \"{listener_name}\" fired at {datetime.datetime.now(datetime.timezone.utc)}"
        )

    def log_warning(self, event: str, warning: str):
        logging.warning(
            f"\n[{self.cog.qualified_name}] ({event}) {warning}"
        )

    def log_info(self, description: str):
        logging.info(
            f"\n[{self.cog.qualified_name}] {description}"
        )


class EmbedBuilder:
    """I hope to implement this once I have finished all commands in bank.py, as this utility class can be used to
        generalize the process of building of embeds and to centralize future modifications"""

    def build_embed(footer: str, description_body: str):
        embed = discord.Embed(
            description=description_body,
            color=0x6bc5ff,
            timestamp=datetime.datetime.now(datetime.timezone.utc)
        )

        embed.set_author(name="Bermuda & Associates")
        embed.set_footer(text=f"{footer}")

        return embed

    def build_error_embed(footer: str, description_body: str):
        embed = discord.Embed(
            description=description_body,
            color=0xff6961,
            timestamp=datetime.datetime.now(datetime.timezone.utc)
        )

        embed.set_author(name="Bermuda & Associates")
        embed.set_footer(text=f"{footer}")

        return embed
