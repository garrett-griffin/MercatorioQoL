import json
from pymerc.client import Client
from pymerc.api.models import common
from pymerc.game.recipe import Recipe

def load_settings():
    with open("bot_settings.json", "r") as f:
        return json.load(f)

def load_clients(api_user, api_token, api_nicknames):
    clients = {}
    for nickname in api_nicknames:
        client = Client(api_user, api_token)
        clients[nickname] = client
    return clients

async def calculate_production(entity, item_name):
    recipe = entity.production.recipe
    if not recipe:
        return 0

    recipe_obj = Recipe(entity._client, recipe)
    for output in recipe_obj.outputs.values():
        if output.product.name == item_name:
            return output.amount * entity.size
    return 0

async def produce_item(player, item_name, amount, settings):
    building_settings = settings.get("production_chains", {}).get(item_name, [])

    for building_id in building_settings:
        entity = next((b for b in player.buildings if b.id == building_id), None)
        if not entity:
            entity = next((t for t in player.transports if t.id == building_id), None)
        if not entity:
            continue

        recipe = Recipe(player._client, entity.production.recipe)
        max_multiplier = entity.size
        target_production = min(amount / await calculate_production(entity, item_name), max_multiplier)

        # Adjust production for required inputs
        for input_ingredient in recipe.inputs.values():
            required_amount = input_ingredient.amount * target_production
            await produce_item(player, input_ingredient.product.name, required_amount, settings)

        # Set production target for the current entity
        if entity.production:
            entity.production.target = target_production
            await entity.production.save()
            print(f"Set target production for {entity.type.name} (ID: {entity.id}) to {target_production}")

def update_settings_with_current_items(player, settings):
    current_items = player.storehouse.data.inventory.items.keys()
    for item in current_items:
        if item not in settings["items"]:
            settings["items"][item] = {"min_stock": 0, "sell_extras": False}
    with open("bot_settings.json", "w") as f:
        json.dump(settings, f, indent=4)
