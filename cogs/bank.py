import typing
import datetime
import os
from random import choice
from dotenv import load_dotenv

import asqlite
import discord
from discord.ext import commands

import utilities as utils
from dialogue import bank_descriptions, error_descriptions

load_dotenv()  # Not sure if this needs to go somewhere else


class Bank(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.log = utils.CogLogger(self)

    @commands.Cog.listener()
    async def on_member_join(self, member):

        self.log.listener_executed("on_member_join")

        async with asqlite.connect(os.environ['DATABASE_PATH']) as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("SELECT * FROM Users WHERE discord_id = :member_id",
                                     {"member_id": member.id})

                user = await cursor.fetchone()  # Returns a list containing instances of sqlite3.Row

                if user is None:
                    await cursor.execute("INSERT INTO Bank (balance) VALUES (100)")
                    await cursor.execute("INSERT INTO Users (is_active, is_public, discord_id, bank_account) VALUES (1, 1, :member_id, (SELECT MAX(bank_id) FROM Bank))",
                                         {"member_id": member.id})

                    self.log.log_info(f"Created new User row for {member.display_name} ({member.id})")

                elif user["is_active"] == 0:
                    await cursor.execute("UPDATE Users SET is_active = 1 WHERE discord_id = :member_id",
                                         {"member_id": member.id})

                    self.log.log_info(f"Updated User row for {member.display_name} ({member.id}): is_active == 1")

                else:
                    self.log.log_warning("Listener", f"Member {member.display_name} ({member.id}) joined with is_active true. What happened?")
                    pass

                await conn.commit()

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        self.log.listener_executed("on_member_remove")

        async with asqlite.connect(os.environ['DATABASE_PATH']) as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("SELECT * FROM Users WHERE discord_id = :member_id",
                                     {"member_id": member.id})

                user = await cursor.fetchone()

                if user is None:
                    self.log.log_warning("Listener", f"Member {member.display_name} ({member.id}) left with no User row. What happened?")

                if user["is_active"] == 1:
                    await cursor.execute("UPDATE Users SET is_active = 0 WHERE discord_id = :member_id", {"member_id": member.id})

                    self.log.log_info(f"Updated User row for {member.display_name} ({member.id}): is_active == 0")

                await conn.commit()

    """
    @Curators
    def add_amount(amount: int, target: discord.Member)
    """
    @commands.command(name="add")
    @commands.has_any_role("Curator", "Server Manager")
    async def _add_amount(self, ctx, amount: int, target: discord.Member, reason: str = "None specified"):

        admin_embed = utils.EmbedBuilder.build_embed("b?add", choice(bank_descriptions["add_backend"]))
        member_embed = utils.EmbedBuilder.build_embed("b?add", choice(bank_descriptions["add_frontend"]))

        async with asqlite.connect(os.environ["DATABASE_PATH"]) as conn:
            async with conn.cursor() as cursor:

                # TODO Condense this query into a single script/statement
                await cursor.execute("SELECT balance FROM Bank INNER JOIN Users ON user_id=bank_id WHERE discord_id=:target_id",
                                     {"target_id": target.id})

                bank = await cursor.fetchone()

                new_balance = bank["balance"] + amount

                await cursor.execute("UPDATE Bank SET balance =:new_balance WHERE bank_id = (SELECT user_id FROM Users WHERE discord_id=:target_id)",
                                     {"target_id": target.id,
                                      "new_balance": new_balance})

                admin_embed.add_field(name="Coins Added", value=f"``{amount}`` has been added to {target.display_name}'s balance.")

                member_embed.add_field(name="Transaction Receipt",
                                       value=f"*Dear Account Holder,*"
                                             f"\n\n*A sum of* ***``{amount} $SC``*** *has been transferred into your account by {ctx.author.mention}. "
                                             f"The reason being:* ***``{reason}``***. *Your balance has been updated to* ***``{new_balance} $SC``***. "
                                             f"*All future inquires and transactions shall reflect this change.* "
                                             f"*Thank you for choosing Bermuda & Associates, based in the Whipping Stones Bay.*"
                                             f"\n\n*Yours,*"
                                             f"\n*Bermuda of Razor Reef*"
                                             f"\n\nThe closing is followed by a remarkably neat and tidy signature. Below is a clear ink stamp of the bank's emblem.""")
                await conn.commit()

        await ctx.send(embed=admin_embed)
        await target.send(embed=member_embed)

        self.log.command_executed("add", target, ctx.args)

    @_add_amount.error
    async def _add_amount_error(self, ctx, error):
        self.log.command_failed("add", ctx.author, error, ctx.args)
        embed = utils.EmbedBuilder.build_error_embed("b?add", choice(error_descriptions))

        if isinstance(error, commands.MissingAnyRole):
            ctx.error_handled = True
            embed.add_field(name=":no_entry: Missing Role", value="Only Curators and Server Managers may access this command.")

        elif isinstance(error, commands.MemberNotFound):
            ctx.error_handled = True
            embed.add_field(name=":no_entry: Unknown Member", value=f"{error}")  # The error is clean enough where just sending it is fine

        elif isinstance(error, Exception):
            ctx.error_handled = True
            embed.add_field(name=":no_entry: Missing Parameters", value="Command Usage: ``b?add (amount) (user) (optional: reason)``")

        await ctx.send(embed=embed)

    """
    @Server Managers
    def deduct_amount(amount: int, target: discord.Member)
    """
    @commands.command(name="deduct")
    @commands.has_any_role("Curator", "Server Manager")
    async def _deduct_amount(self, ctx, amount: int, target: discord.Member, reason: str = "None specified"):

        admin_embed = utils.EmbedBuilder.build_embed("b?deduct", choice(bank_descriptions["deduct_backend"]))
        member_embed = utils.EmbedBuilder.build_embed("b?deduct", choice(bank_descriptions["deduct_frontend"]))

        async with asqlite.connect(os.environ["DATABASE_PATH"]) as conn:
            async with conn.cursor() as cursor:

                # TODO Condense this query into a single script/statement
                await cursor.execute("SELECT balance FROM Bank INNER JOIN Users ON user_id=bank_id WHERE discord_id=:target_id",
                                     {"target_id": target.id})

                bank = await cursor.fetchone()

                new_balance = bank["balance"] - amount

                if new_balance < 0:
                    new_balance = 0

                await cursor.execute("UPDATE Bank SET balance =:new_balance WHERE bank_id = (SELECT user_id FROM Users WHERE discord_id=:target_id)",
                                     {"target_id": target.id,
                                      "new_balance": new_balance})

                admin_embed.add_field(name="Coins Removed", value=f"``{amount}`` has been deducted from {target.display_name}'s balance.")

                member_embed.add_field(name="Transaction Receipt",
                                       value=f"*Dear Account Holder,*"
                                             f"\n\n*An invoice of* ***``{amount} $SC``*** *has been placed on your account by {ctx.author.mention}. "
                                             f"The reason being:* ***``{reason}``***. *Your balance has been updated to* ***``{new_balance} $SC``***. "
                                             f"*All future inquires and transactions shall reflect this change.* "
                                             f"*Thank you for choosing Bermuda & Associates, based in the Whipping Stones Bay.*"
                                             f"\n\n*Yours,*"
                                             f"\n*Bermuda of Razor Reef*"
                                             f"\n\nThe closing is followed by a remarkably neat and tidy signature. Below is a clear ink stamp of the bank's emblem.""")
                await conn.commit()

        await ctx.send(embed=admin_embed)
        await target.send(embed=member_embed)

        self.log.command_executed("deduct", target, ctx.args)

    @_deduct_amount.error
    async def _deduct_amount_error(self, ctx, error):
        self.log.command_failed("deduct", ctx.author, error, ctx.args)
        embed = utils.EmbedBuilder.build_error_embed("b?add", choice(error_descriptions))

        if isinstance(error, commands.MissingAnyRole):
            ctx.error_handled = True
            embed.add_field(name=":no_entry: Missing Role", value="Only Curators and Server Managers may access this command.")

        elif isinstance(error, commands.MemberNotFound):
            ctx.error_handled = True
            embed.add_field(name=":no_entry: Unknown Member", value=f"{error}")  # The error is clean enough where just sending it is fine

        elif isinstance(error, ValueError):
            ctx.error_handled = True

        elif isinstance(error, Exception):
            ctx.error_handled = True
            embed.add_field(name=":no_entry: Missing Parameters", value="Command Usage: ``b?deduct (amount) (user) (optional: reason)``")

        await ctx.send(embed=embed)

    """
    @Server Managers
    def set_balance(amount: int, target: discord.Member)
    """
    @commands.command(name="set")
    @commands.has_role("Server Manager")
    async def _set_balance(self, ctx, amount: int, target: discord.Member, reason: str = "None specified"):

        admin_embed = utils.EmbedBuilder.build_embed("b?set", choice(bank_descriptions["set_backend"]))
        member_embed = utils.EmbedBuilder.build_embed("b?set", choice(bank_descriptions["set_frontend"]))

        async with asqlite.connect(os.environ["DATABASE_PATH"]) as conn:
            async with conn.cursor() as cursor:

                # TODO Condense this query into a single script/statement

                await cursor.execute("UPDATE Bank SET balance =:new_balance WHERE bank_id = (SELECT user_id FROM Users WHERE discord_id=:target_id)",
                                     {"target_id": target.id,
                                      "new_balance": amount})

                admin_embed.add_field(name="Balance Set", value=f"{target.display_name}'s balance has been set to ``{amount}``.")

                member_embed.add_field(name="Transaction Receipt",
                                       value=f"*Dear Account Holder,*"
                                             f"\n\n*An error has been detected with your account by {ctx.author.mention}.* "
                                             f"The error being:* ***``{reason}``***. *Your account has been adjusted, and its balance is now* ***``{amount} $SC``***. "
                                             f"*All future inquires and transactions shall reflect this change.* "
                                             f"*Thank you for choosing Bermuda & Associates, based in the Whipping Stones Bay.*"
                                             f"*We hope that this misfortune will not deter future investments.*"
                                             f"\n\n*Yours,*"
                                             f"\n*Bermuda of Razor Reef*"
                                             f"\n\nThe closing is followed by a remarkably neat and tidy signature. Below is a clear ink stamp of the bank's emblem.""")
                await conn.commit()

        await ctx.send(embed=admin_embed)
        await target.send(embed=member_embed)

        self.log.command_executed("set", target, ctx.args)

    @_set_balance.error
    async def _set_balance_error(self, ctx, error):
        self.log.command_failed("set", ctx.author, error, ctx.args)
        embed = utils.EmbedBuilder.build_error_embed("b?set", choice(error_descriptions))

        if isinstance(error, commands.MissingAnyRole):
            ctx.error_handled = True
            embed.add_field(name=":no_entry: Missing Role", value="Only Curators and Server Managers may access this command.")

        elif isinstance(error, commands.MemberNotFound):
            ctx.error_handled = True
            embed.add_field(name=":no_entry: Unknown Member", value=f"{error}")  # The error is clean enough where just sending it is fine

        elif isinstance(error, Exception):
            ctx.error_handled = True
            embed.add_field(name=":no_entry: Missing Parameters", value="Command Usage: ``b?set (amount) (user) (optional: reason)``")

        await ctx.send(embed=embed)

    @commands.command(name="balance", aliases=["bal", "b"])
    async def _get_balance(self, ctx, member: typing.Optional[discord.Member]):

        embed = utils.EmbedBuilder.build_embed("b?balance", choice(bank_descriptions['balance_frontend']))

        if member is None:
            member = ctx.author
            embed.add_field(name=":information_source: No Member Specified", value="Defaulting to command invoker")

        async with asqlite.connect(os.environ['DATABASE_PATH']) as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("SELECT * FROM Users WHERE discord_id=:member_id", {"member_id": member.id})

                user = await cursor.fetchone()

                if user["is_public"] == 1:
                    await cursor.execute("SELECT balance FROM Users INNER JOIN Bank ON Users.user_id=Bank.bank_id WHERE discord_id=:member_id",
                                         {"member_id": member.id})

                    balance = await cursor.fetchone()

                    balance_value = balance["balance"]

                    embed.add_field(
                        name=f"{member.name.title()}'s Balance",
                        value=f"``{balance_value}``"
                    )

                else:

                    embed.add_field(
                        name=f"{member.name.title()}'s Balance",
                        value="Just as you begin to read the scroll, Bermuda lurches over and tears the scroll from your talons, hissing all the while.\n\"" \
                              "Ah, *my* mistake. This is a **private** account.\""
                    )

                await ctx.send(embed=embed)

                self.log.command_executed("_get_balance", ctx.author, ctx.args)

    @_get_balance.error
    async def _get_balance_error(self, ctx, error):
        embed = utils.EmbedBuilder.build_error_embed("b?balance", choice(error_descriptions))

        if isinstance(error, commands.CommandInvokeError):
            ctx.error_handled = True

            self.log.command_failed("_get_balance_error", ctx.author, error, ctx.args)
            embed.add_field(name="Exception Raised", value="Something went wrong. Contact @Developers for help")

        if isinstance(error, KeyError):
            ctx.error_handled = True

            embed.add_field(name="Unknown User", value="The specified user could not be found. Try a different value.")

            self.log.command_failed("_get_balance_error", ctx.author, error, ctx.args)

        ctx.send(embed=embed)


async def setup(bermuda: commands.Bot):
    await bermuda.add_cog(Bank(bermuda))
