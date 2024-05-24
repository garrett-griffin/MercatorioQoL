"""
This example demonstrates how to adjust the amount of labour being automatically
purchased in a storehouse to match the amount of labour being used.
"""


# TODO: Balance auto-buy for each item.
#
# TODO: Iteratively balance auto-buy and labor.
#
# TODO: Auto-switch sustenance based on availability. Turn off purchase of sustenance if cash is below auto-buy amount.
#
# TODO: Maintain x amount in warehouse - similar to a max stock amount for autobuy, but this turns production off and on based on what's needed to maintain a certain stock level.
#
# TODO: Auto adjust min sale price based on average cost of inventory - make sure you're not selling at a loss.

# TODO: Automatic recipe switching based on ingredient availability
import os
import asyncio
from dotenv import load_dotenv

from utils import load_settings, load_clients  # Import the functions from utils.py
from balance import balance_labour  # Import the functions from balance.py

# Load the API_USER, API_TOKEN, and API_NICKNAMES from the environment
load_dotenv()
settings = load_settings()

run_first_only = settings.get("run_first_only", False)

async def main():
    api_user = os.environ["API_USER"]
    api_token = os.environ["API_TOKEN"]
    api_nicknames = os.environ["API_NICKNAMES"]

    clients = load_clients(api_user, api_token, api_nicknames)

    for nickname, client in clients.items():
        if not settings["players"].get(nickname, {}).get("active", False):
            continue
        try:
            player = await client.player()
            print(f"Handling - {player.data.household.name} ({nickname})...")
            await balance_labour(player)
        except Exception as e:
            print(f"Error handling client {client}: {e}")
            continue
        if run_first_only:
            return

if __name__ == "__main__":
    asyncio.run(main())
