# Connected Discord-GitHub | Discord: AbyssalNoob1| Roblox: AbyssalNoob1 

import discord
from discord import app_commands
from discord.ext import commands

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

class TicTacToeButton(discord.ui.Button['TicTacToeView']):
    """Individual grid cell button handling move registration and turn swaps."""
    def __init__(self, x: int, y: int):
        super().__init__(style=discord.ButtonStyle.secondary, label="\u200b", row=y)
        self.x = x
        self.y = y

    async def callback(self, interaction: discord.Interaction):
        assert self.view is not None
        view = self.view

        # Validate turn ownership
        if interaction.user.id != view.current_player.id:
            await interaction.response.send_message("❌ It's not your turn!", ephemeral=True)
            return

        if view.board[self.y][self.x] != 0:
            await interaction.response.send_message("❌ That spot is already taken!", ephemeral=True)
            return

        # Update button state and internal matrix
        if view.current_player == view.player1:
            self.style = discord.ButtonStyle.danger
            self.label = "X"
            view.board[self.y][self.x] = 1
            view.current_player = view.player2
        else:
            self.style = discord.ButtonStyle.primary
            self.label = "O"
            view.board[self.y][self.x] = 2
            view.current_player = view.player1

        self.disabled = True
        winner = view.check_winner()

        if winner is not None:
            for child in view.children:
                child.disabled = True
            if winner == 0:
                content = "🤝 It's a tie!"
            elif winner == 1:
                content = f"🎉 {view.player1.mention} (X) won!"
            else:
                content = f"🎉 {view.player2.mention} (O) won!"
            await interaction.response.edit_message(content=content, view=view)
            view.stop()
        else:
            await interaction.response.edit_message(content=f"🎮 Turn: {view.current_player.mention}", view=view)


class TicTacToeView(discord.ui.View):
    """Grid controller managing board state matrix and win conditions."""
    def __init__(self, player1: discord.Member, player2: discord.Member):
        super().__init__(timeout=180)
        self.player1 = player1
        self.player2 = player2
        self.current_player = player1
        self.board = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]

        # Construct 3x3 interactive button grid
        for y in range(3):
            for x in range(3):
                self.add_item(TicTacToeButton(x, y))

    def check_winner(self):
        """Evaluates board matrix for rows, columns, diagonals, or tie states."""
        for i in range(3):
            if self.board[i][0] == self.board[i][1] == self.board[i][2] != 0:
                return self.board[i][0]
            if self.board[0][i] == self.board[1][i] == self.board[2][i] != 0:
                return self.board[0][i]

        if self.board[0][0] == self.board[1][1] == self.board[2][2] != 0:
            return self.board[0][0]
        if self.board[0][2] == self.board[1][1] == self.board[2][0] != 0:
            return self.board[0][2]

        if all(cell != 0 for row in self.board for cell in row):
            return 0  # Tie

        return None


@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Logged in as {bot.user.name}")


@bot.tree.command(name="tictactoe", description="Challenge another member to Tic-Tac-Toe")
async def tictactoe(interaction: discord.Interaction, opponent: discord.Member):
    """Initiates an interactive Tic-Tac-Toe duel between two members."""
    if opponent.bot or opponent.id == interaction.user.id:
        await interaction.response.send_message("❌ You cannot play against yourself or bots!", ephemeral=True)
        return

    view = TicTacToeView(interaction.user, opponent)
    await interaction.response.send_message(
        f"🎮 **Tic-Tac-Toe:** {interaction.user.mention} (X) vs {opponent.mention} (O)\nTurn: {interaction.user.mention}",
        view=view
    )

bot.run("")

