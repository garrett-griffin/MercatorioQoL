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
import math
import os
import json

import asyncio
from dotenv import load_dotenv

from pymerc.api.models.common import Item
from pymerc.client import Client
from pymerc.game.player import Player

# Load the API_USER and API_TOKEN from the environment
load_dotenv()

run_first_only = True


def load_clients() -> list[Client]:
    clients: list[Client] = []

    api_user: str = os.environ["API_USER"]
    api_token: str = os.environ["API_TOKEN"]

    if not api_user.startswith("[") and not api_token.startswith("["):
        api_user = "[" + api_user + "]"
        api_token = "[" + api_token + "]"

    if not api_user.startswith("[") or not api_token.startswith("["):
        raise ValueError("Invalid API user or token")

    users: list[str] = json.loads(api_user)
    tokens: list[str] = json.loads(api_token)
    for user, token in zip(users, tokens):
        clients.append(Client(user, token))

    return clients

async def balance_item(player: Player, item: Item) -> bool:
    manager = player.storehouse.data.inventory.managers.get(item)
    flow = player.storehouse.data.total_flow.get(item)

    if not manager or not flow:
        print(f"No manager or flow for {item}")
        return False

    consumed = flow.consumption - flow.production

    print(f"\tCurrently consuming {consumed} {item}")
    print(f"\tCurrently buying {manager.buy_volume} {item}")

    if consumed < manager.buy_volume:
        print(f"\tWasting {manager.buy_volume - consumed} {item}")
    elif consumed > manager.buy_volume:
        print(f"\tMissing {consumed - manager.buy_volume} {item}")
    else:
        print(f"\t{item} consumption is balanced")
        return False

    print(f"\tAdjusting {item} purchase amount to {math.ceil(consumed)}")

    old_volume = manager.buy_volume
    manager.buy_volume = math.ceil(consumed)

    if old_volume == manager.buy_volume:
        print(f"\t{item} consumption is balanced (wasting less than 1.0 {item})")
        return False

    result = await player.storehouse.data.set_manager(item, manager)
    if result:
        print(f"\t{item} purchase amount adjusted successfully")
        return True
    else:
        print(f"\tFailed to adjust {item} purchase amount")
        return False

async def balance_labour(player: Player) -> bool:
    return await balance_item(player, Item.Labour)


async def main():
    clients = load_clients()

    for client in clients:
        try:
            player = await client.player()
            print(f"Handling {player.data.username} - {player.data.household.name}...")
            await balance_labour(player)
        except Exception as e:
            print(f"Error handling client {client}: {e}")
            continue
        if run_first_only:
            return


if __name__ == "__main__":
    asyncio.run(main())
