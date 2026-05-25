import discord
from discord.ext import commands
from discord import app_commands
import json

# ===== CONFIG =====

def load_config():
    with open("config.json", "r") as f:
        return json.load(f)

config = load_config()

# ===== VIEW =====

class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    # ===== ABRIR TICKET =====

    @discord.ui.button(
        label="Abrir Ticket",
        emoji="🎫",
        style=discord.ButtonStyle.primary,
        custom_id="ticket_open"
    )
    async def open_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):

        guild = interaction.guild
        user = interaction.user

        category = guild.get_channel(config["ticket_category"])

        channel = await guild.create_text_channel(
            name=f"ticket-{user.name}",
            category=category
        )

        await channel.set_permissions(guild.default_role, view_channel=False)

        await channel.set_permissions(
            user,
            view_channel=True,
            send_messages=True,
            read_message_history=True
        )

        embed = discord.Embed(
            title="🎫 Ticket Aberto",
            description=f"""
Olá {user.mention}!

Explique seu problema abaixo.

🔔 Aguarde um membro da staff.
            """,
            color=discord.Color.blue()
        )

        await channel.send(
            embed=embed,
            view=StaffView()
        )

        await interaction.response.send_message(
            f"✅ Seu ticket foi criado: {channel.mention}",
            ephemeral=True
        )

# ===== PAINEL STAFF =====

class StaffView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    # ===== FECHAR =====

    @discord.ui.button(
        label="Fechar",
        emoji="🔒",
        style=discord.ButtonStyle.danger,
        custom_id="ticket_close"
    )
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):

        await interaction.response.send_message(
            "🔒 Fechando ticket...",
            ephemeral=True
        )

        await interaction.channel.delete()

    # ===== CALL =====

    @discord.ui.button(
        label="Criar Call",
        emoji="📞",
        style=discord.ButtonStyle.primary,
        custom_id="ticket_call"
    )
    async def create_call(self, interaction: discord.Interaction, button: discord.ui.Button):

        guild = interaction.guild

        voice = await guild.create_voice_channel(
            name=f"call-{interaction.user.name}"
        )

        await interaction.response.send_message(
            f"📞 Call criada: {voice.mention}"
        )

    # ===== NOTIFICAR =====

    @discord.ui.button(
        label="Notificar",
        emoji="🔔",
        style=discord.ButtonStyle.secondary,
        custom_id="ticket_notify"
    )
    async def notify_user(self, interaction: discord.Interaction, button: discord.ui.Button):

        await interaction.channel.send(
            f"{interaction.user.mention} chamou a staff!"
        )

# ===== COMANDOS =====

class Ticket(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ===== PAINEL =====

    @app_commands.command(
        name="ticket",
        description="Enviar painel de ticket"
    )
    async def ticket(self, interaction: discord.Interaction):

        role = interaction.guild.get_role(config["staff_role"])

        if role not in interaction.user.roles:
            await interaction.response.send_message(
                "❌ Você não é staff.",
                ephemeral=True
            )
            return

        embed = discord.Embed(
            title="🎫 Central de Atendimento",
            description="""
Clique no botão abaixo para abrir um ticket.

⚠ Não abra tickets sem motivo.
            """,
            color=discord.Color.blue()
        )

        await interaction.channel.send(
            embed=embed,
            view=TicketView()
        )

        await interaction.response.send_message(
            "✅ Painel enviado.",
            ephemeral=True
        )

# ===== SETUP =====

async def setup(bot):
    await bot.add_cog(Ticket(bot))
