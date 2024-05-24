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
import copy
import json
from dotenv import load_dotenv

from utils import load_settings, load_clients, can_produce_item, is_building_producing_item, calculate_production, calculate_target_production, update_settings_with_current_items # Import the functions from utils.py
from balance import balance_labour  # Import the functions from balance.py
from pymerc.api.models.common import Item
from pymerc.game.player import Player

# Load the API_USER, API_TOKEN, and API_NICKNAMES from the environment
load_dotenv()
settings = load_settings()

run_first_only = settings.get("run_first_only", False)

async def check_and_adjust_production(player: Player, nickname: str, item_name: str, item_settings: dict):
    """Check and adjust the production of a given item for the player.

    Args:
        player (Player): The player object.
        nickname (str): The player's nickname.
        item_name (str): The name of the item.
        item_settings (dict): The settings for the item.
    """
    item = Item[item_name]  # Assuming the item names in the JSON match the enum names
    min_stock = item_settings["min_stock"]
    sell_extras = item_settings["sell_extras"]

    # Determine current stock level
    current_stock = player.storehouse.items.get(item, 0).balance

    # Determine current consumption level
    flow = player.storehouse.flows.get(item)
    current_consumption = flow.consumption if flow else 0

    # Check if current stock is below min_stock
    required_amount = min_stock - (current_stock + current_consumption)
    if required_amount > 0:
        can_produce = await can_produce_item(player, item)
        if can_produce:
            print(f"\t{nickname} can produce {item_name}.")
            print(f"\t\tTo maintain a stock level of {min_stock}, we need to produce {required_amount}, because we have {current_stock} in stock and are consuming {current_consumption}.")
        if can_produce:
            for building in player.buildings:
                is_producing = await is_building_producing_item(building, item)
                if is_producing:
                    target_production = await calculate_target_production(building, item, required_amount)
                    print(
                        f"\t\tTo produce {required_amount} of {item}, set target production of building {building.id} to {target_production}")
                    print("\t-----")
                    if target_production != building.production.target_production:
                        return True
                    # Here you would set the building's target production to the calculated value
                    #building.production.target = target_production
                    #await building.set_target_production(target_production)
    return False

async def main():
    api_user: str = os.environ["API_USER"]
    api_token: str = os.environ["API_TOKEN"]
    api_nicknames: str = os.environ["API_NICKNAMES"]

    clients = load_clients(api_user, api_token, api_nicknames)

    updated_settings = copy.deepcopy(settings)

    for nickname, client in clients.items():
        if not settings["players"].get(nickname, {}).get("active", False):
            continue
        player = await client.player()
        print(f"Handling {player.data.household.name} ({nickname})...")

        changed_production: bool = True
        while changed_production:
            changed_production = False
            for item_name, item_settings in settings["players"][nickname]["items"].items():
                result: bool = await check_and_adjust_production(player, nickname, item_name, item_settings)
                changed_production = changed_production or result


        # try:
        #     player = await client.player()
        #     print(f"Handling {player.data.household.name} ({nickname})...")
        #
        #     # Update settings with the player's current items in stock
        #     updated_settings = await update_settings_with_current_items(player, updated_settings, nickname)
        #
        #     for item_name, item_settings in settings["players"][nickname]["items"].items():
        #         await check_and_adjust_production(player, nickname, item_name, item_settings)
        #
        #     #await balance_labour(player)
        #
        # except Exception as e:
        #     print(f"Error handling client {client}: {e}")
        #     continue
        if run_first_only:
            return

    # print(json.dumps(updated_settings, indent=4))

if __name__ == "__main__":
    asyncio.run(main())
