import asyncio
from discord.ext import commands
from discord.ext import commands

class MyCog(commands.Cog, name="embedig", description="sends ig embeds in #memes"):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        
        # Check if the message contains an Instagram link
        if "www.instagram.com" in message.content:
            # Replace "www.instagram.com" with "www.ddinstagram.com" directly in the message content
            modified_content = message.content.replace("www.instagram.com", "www.ddinstagram.com")
            
            # Handle "?igsh=" if present
            parts = modified_content.split("?")
            modified_link = parts[0]  # Get the link before "?"

            # Share a text with the modified_link and the user's display name
            shared_text = f"***This was shared by {message.author.display_name}***"
            
            # Send the modified link and shared text as a reply to the original message
            await message.reply(f"{shared_text}\n{modified_link}")

            # Delete the original message if it contains "?"
            if len(parts) > 1:
                await asyncio.sleep(3)
                await message.delete()

async def setup(bot):
    await bot.add_cog(MyCog(bot))