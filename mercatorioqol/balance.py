import math
from pymerc.api.models.common import Item
from pymerc.game.player import Player

async def balance_item(player: Player, item: Item, buy_shortfall: bool = False, sell_excess: bool = False) -> bool:
    manager = player.storehouse.data.inventory.managers.get(item)
    flow = player.storehouse.data.flows.get(item)
    buy_volume: float | None = None

    if not manager or not flow:
        # print(f"No manager or flow for {item}")
        return False

    consumed = flow.consumption

    if flow.shortfall:
        consumed += flow.shortfall

    consumed -= flow.production

    if flow.resident:
        consumed -= flow.resident

    #print(f"\tCurrently consuming {consumed} {item}")
    #print(f"\tCurrently buying {manager.buy_volume} {item}")

    old_volume = manager.buy_volume
    buy_volume = math.ceil(consumed)
    sell_volume = 0 - buy_volume

    if buy_shortfall and flow.shortfall and flow.shortfall > 0.0:
        print(f"\t\tBuying Shortfall of {math.ceil(flow.shortfall)} of {item} at max price of {math.ceil(player.storehouse.items.get(item).average_cost * 2)}.")
        await player.storehouse.items.get(item).buy(math.ceil(flow.shortfall), math.ceil(player.storehouse.items.get(item).average_cost * 2))

    if consumed == manager.buy_volume:
        return False

    if (0 < buy_volume == old_volume) or (0 < sell_volume == manager.sell_volume) or (buy_volume == 0 and sell_volume == 0):
        # print(f"\t{item} consumption is balanced (wasting less than 1.0 {item})")
        return False

    print(f"Old volume: {old_volume} - Buy volume: {buy_volume}")
    print(f"Old sell volume: {manager.sell_volume} - Sell volume: {sell_volume}")

    if buy_volume > 0.0:
        print(f"\tAdjusting {item} purchase amount to {buy_volume}")
        result = await player.storehouse.items[item].patch_manager(buy_volume=buy_volume,sell_volume=0)
        print(f"\t{item} purchase amount adjusted successfully")
    elif sell_volume > 0.0:
        print(f"\tAdjusting {item} sale amount to {sell_volume}")
        result = await player.storehouse.items[item].patch_manager(buy_volume=0,sell_volume=sell_volume)
        print(f"\t{item} sale amount adjusted successfully")

    return True

async def balance_labour(player: Player) -> bool:
    return await balance_item(player, Item.Labour, buy_shortfall=True)

async def balance_carting(player: Player) -> bool:
    return await balance_item(player, Item.Carting, buy_shortfall=True)

async def balance_ox_power(player: Player) -> bool:
    return await balance_item(player, Item.OxPower, buy_shortfall=True)
