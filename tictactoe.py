# Connected Discord-GitHub | Discord: AbyssalNoob1 | Roblox: AbyssalNoob1 

import discord
from discord.ext import commands
import os

bot = commands.Bot(command_prefix="!", intents=discord.Intents.default())

class TTTButton(discord.ui.Button):
    def __init__(self, x, y):
        # using a zero-width space for empty buttons looks cleaner than a normal space
        super().__init__(style=discord.ButtonStyle.secondary, label="\u200b", row=y)
        self.x = x
        self.y = y

    async def callback(self, interaction: discord.Interaction):
        view: TTTGame = self.view

        if interaction.user.id != view.turn.id:
            await interaction.response.send_message("It is not your turn right now.", ephemeral=True)
            return

        if view.board[self.y][self.x] != 0:
            await interaction.response.send_message("Someone already played there!", ephemeral=True)
            return

        # update the board matrix based on whose turn it is
        if view.turn == view.p1:
            view.board[self.y][self.x] = 1
            self.label = "X"
            self.style = discord.ButtonStyle.danger
            view.turn = view.p2
        else:
            view.board[self.y][self.x] = 2
            self.label = "O"
            self.style = discord.ButtonStyle.primary
            view.turn = view.p1

        self.disabled = True

        # check if the game is over after this move
        status = view.check_winner()

        if status != -1:
            for child in view.children:
                child.disabled = True
            
            if status == 0:
                final_msg = "Game ended in a tie."
            elif status == 1:
                final_msg = f"GG! {view.p1.mention} wins!"
            elif status == 2:
                final_msg = f"GG! {view.p2.mention} wins!"

            await interaction.response.edit_message(content=final_msg, view=view)
            view.stop()
        else:
            await interaction.response.edit_message(content=f"Turn: {view.turn.mention}", view=view)


class TTTGame(discord.ui.View):
    def __init__(self, p1, p2):
        super().__init__(timeout=120)
        self.p1 = p1
        self.p2 = p2
        self.turn = p1
        # 0 = empty, 1 = p1 (X), 2 = p2 (O)
        self.board = [
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0]
        ]
        self.message = None

        for y in range(3):
            for x in range(3):
                self.add_item(TTTButton(x, y))

    async def on_timeout(self):
        # prevents people from clicking buttons on abandoned games after 2 mins
        for btn in self.children:
            btn.disabled = True
        if self.message:
            try:
                await self.message.edit(content="Game timed out due to inactivity.", view=self)
            except Exception:
                pass

    def check_winner(self):
        # manual check for rows
        for row in self.board:
            if row[0] == row[1] == row[2] and row[0] != 0:
                return row[0]
        
        # manual check for columns
        for col in range(3):
            if self.board[0][col] == self.board[1][col] == self.board[2][col] and self.board[0][col] != 0:
                return self.board[0][col]

        # check the two diagonals
        if self.board[0][0] == self.board[1][1] == self.board[2][2] and self.board[0][0] != 0:
            return self.board[0][0]
        if self.board[0][2] == self.board[1][1] == self.board[2][0] and self.board[0][2] != 0:
            return self.board[0][2]

        # check if there are any empty spaces left (if not, it's a tie)
        for row in self.board:
            for cell in row:
                if cell == 0:
                    return -1 
        
        return 0


@bot.tree.command(name="tictactoe", description="Play a game of Tic Tac Toe")
async def ttt_cmd(interaction: discord.Interaction, opponent: discord.Member):
    if opponent == interaction.user:
        await interaction.response.send_message("You cannot play against yourself.", ephemeral=True)
        return
    if opponent.bot:
        await interaction.response.send_message("You cannot play against a bot.", ephemeral=True)
        return

    game_view = TTTGame(interaction.user, opponent)
    await interaction.response.send_message(
        f"Tic Tac Toe: {interaction.user.mention} vs {opponent.mention}\nTurn: {interaction.user.mention}", 
        view=game_view
    )
    
    # grab the message object so we can edit it later if the view times out
    game_view.message = await interaction.original_response()


@bot.event
async def on_ready():
    await bot.tree.sync()
    print("Bot is online!")


my_token = os.getenv("BOT_TOKEN")
if my_token is None:
    print("Error: No bot token found in environment variables.")
else:
    bot.run("my_token")
