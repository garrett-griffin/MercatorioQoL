import json
from pymerc.client import Client
from pymerc.api.models.common import Item
from pymerc.game.building import Building
from pymerc.game.player import Player
from pymerc.game.recipe import Recipe

def load_settings(file_path: str = "settings.json") -> dict:
    with open(file_path, "r") as file:
        return json.load(file)

def load_clients(api_user: str, api_token: str, api_nicknames: str) -> dict:
    clients = {}

    if not api_user.startswith("[") and not api_token.startswith("["):
        api_user = "[" + api_user + "]"
        api_token = "[" + api_token + "]"

    if not api_user.startswith("[") or not api_token.startswith("["):
        raise ValueError("Invalid API user or token")

    users = json.loads(api_user)
    tokens = json.loads(api_token)
    nicknames = json.loads(api_nicknames)

    if len(users) != len(tokens) or len(users) != len(nicknames):
        raise ValueError("Mismatch in the number of users, tokens, and nicknames")

    for user, token, nickname in zip(users, tokens, nicknames):
        clients[nickname] = Client(user, token)

    return clients

async def can_produce_item(player: Player, item: Item) -> bool:
    """Check if the player's buildings can produce the specified item.

    Args:
        player (Player): The player object.
        item (Item): The item to check.

    Returns:
        bool: True if the item can be produced, False otherwise.
    """
    for building in player.buildings:
        if building.production:
            recipe: Recipe = Recipe(player._client, building.production.recipe.value)
            await recipe.load()
            for output in recipe.outputs:
                if output.product == item:
                    return True
    return False

async def is_building_producing_item(building: Building, item: Item) -> bool:
    """Check if the given building is currently producing the specified item.

    Args:
        building (Building): The building object.
        item (Item): The item to check.

    Returns:
        bool: True if the building is currently producing the item, False otherwise.
    """
    await building.load()

    if building.production:
        recipe_name = building.production.recipe.value
        recipe = Recipe(building._client, recipe_name)
        await recipe.load()

        for output in recipe.data.outputs:
            if output.product == item:
                return True
    return False

async def calculate_ideal_labor_for_player_buildings(player: Player):
    total_labor = 0.0

    for building in player.buildings:
        if building.production:
            labor_required = await building.calculate_current_labor_need()
            print(
                f"Building ID: {building.id}, Type: {building.type}, Recipe: {building.production.recipe.value}, Labor Required: {labor_required}"
            )
            total_labor += labor_required

    print(f"Total labor required for all buildings: {total_labor}")

async def calculate_production(building: Building, item: Item) -> float:
    """Calculate how much of an item the building would produce given its current recipe and target_production.

    Args:
        building (Building): The building object.
        item (Item): The item to check.

    Returns:
        float: The amount of the item produced.
    """
    await building.load()

    if building.production:
        recipe_name = building.production.recipe.value
        recipe = Recipe(building._client, recipe_name)
        await recipe.load()

        for output in recipe.data.outputs:
            if output.product == item:
                return output.amount * building.target_production
    return 0.0

async def calculate_target_production(building: Building, item: Item, desired_amount: float) -> float:
    """Determine the target_production needed to produce a specific amount of an item.

    Args:
        building (Building): The building object.
        item (Item): The item to produce.
        desired_amount (float): The desired amount of the item.

    Returns:
        float: The target_production needed to produce the desired amount of the item, rounded to one decimal point.
    """
    await building.load()

    if building.production:
        recipe_name = building.production.recipe.value
        recipe = Recipe(building._client, recipe_name)
        await recipe.load()

        for output in recipe.data.outputs:
            if output.product == item:
                return round(desired_amount / output.amount, 1)
    return 0.0

async def update_settings_with_current_items(player: Player, settings: dict, nickname: str) -> str:
    """Update settings with the player's current items in their storehouse.

    Args:
        player (Player): The player object.
        settings (dict): The settings dictionary.
        nickname (str): The player's nickname.

    Returns:
        str: The updated settings as a JSON string.
    """
    if "players" not in settings:
        settings["players"] = {}

    if nickname not in settings["players"]:
        settings["players"][nickname] = {
            "active": True,
            "items": {}
        }

    current_items = player.storehouse.data.inventory.account.assets
    for item, asset in current_items.items():
        settings["players"][nickname]["items"][item.name] = {
            "min_stock": 0,  # Default value, update as needed
            "sell_extras": False  # Default value, update as needed
        }

    return settings