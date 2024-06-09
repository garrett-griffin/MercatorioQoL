import os
import asyncio
from pymerc.client import Client
from pymerc.game.player import Player
from pymerc.api.models.common import Item
from bot_utils import load_settings, load_clients, produce_item
from dotenv import load_dotenv

async def main():
    load_dotenv()
    api_user = os.getenv("BOT_USER")
    api_token = os.getenv("BOT_TOKEN")
    api_nicknames = ["PreciosaWalmyr"]  # Directly use a list of nicknames

    clients = load_clients(api_user, api_token, api_nicknames)
    settings = load_settings()

    client = clients["PreciosaWalmyr"]
    player = Player(client)
    await player.load()

    print(f"Player Name: {player.household.name}")
    print(f"Prestige: {player.prestige}")
    print(f"Money: {player.money}")

    print("\nBuildings and Production Capacities:")
    for building in player.buildings:
        await building.load()
        print(f"Building ID: {building.id}, Type: {building.type}, Size: {building.size}")
        if building.production:
            print(f"\tRecipe: {building.production.recipe}")
            print(f"\tTarget Production: {building.production.target}")
            for ingredient, amount in building.production.ingredients.items():
                print(f"\t\tIngredient: {ingredient}, Amount: {amount}")

    print("\nAutobuy Setup:")
    for item, autobuy in player.storehouse.data.inventory.managers.items():
        print(f"{item.name}: Buy Volume = {autobuy.buy_volume}, Unit Cost = {autobuy.unit_cost}")

    print("\nInventory Details:")
    for item, asset in player.storehouse.data.inventory.items.items():
        print(f"{item.name}: Balance = {asset.balance}, Capacity = {asset.capacity}, Unit Cost = {asset.unit_cost}")

    print("\nProduction Chain Overview:")
    production_chain = {
        "Flax": ["Flax Fiber"],
        "Flax Fiber": ["Thread"],
        "Thread": ["Nets", "Ropes"],
        "Fish": ["Cured Fish", "Stockfish"]
    }
    for raw, products in production_chain.items():
        print(f"{raw}: {', '.join(products)}")

if __name__ == "__main__":
    asyncio.run(main())