import asyncio
from discord.ext import commands
import discord
import re
from discord.ext import commands
from discord.ext.commands import Context
import requests

class MyCog(commands.Cog,name="embedig",description="sends ig embeds in #memes"):
    def __init__(self, bot):
        self.bot = bot
        self.webhook_url = 'https://discord.com/api/webhooks/1138068053834334268/J8pxJtcdXtSKuRfZfCgiNBYaj9q2t1p6wbd8x-jZaNtEo_5bY7w-k5rXWFwS8TitHwNk'  # Replace with your webhook URL

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.id != 742284663552344086:
            return
        if message.author == self.bot.user or message.webhook_id is not None:
            return
        # Check if the message contains an Instagram link
        match = re.search(r'(?:https?:\/\/)?(?:www\.)?instagram\.com\/\w+', message.content)
        if match:
            # Replace "instagram.com" with "ddinstagram.com" and send the modified link
            modified_link = message.content.replace("instagram.com", "ddinstagram.com")

            # Create a new webhook object using the webhook URL
            webhook = discord.SyncWebhook.from_url(self.webhook_url)

            # Get the sender's name and avatar
            sender_name = message.author.name
            sender_avatar = message.author.avatar.url

            # Send the modified link using the webhook and the sender's name and avatar
            webhook.send(modified_link, username=sender_name, avatar_url=sender_avatar)

            # Delete the original message from the user
            await asyncio.sleep(10)
            await message.delete()

            
async def setup(bot):
    await bot.add_cog(MyCog(bot))
