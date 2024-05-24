import math
from pymerc.api.models.common import Item
from pymerc.game.player import Player

async def balance_item(player: Player, item: Item) -> bool:
    manager = player.storehouse.data.inventory.managers.get(item)
    flow = player.storehouse.data.flows.get(item)
    buy_volume: float = None

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

    old_volume = manager.buy_volume
    buy_volume = math.ceil(consumed)

    if old_volume == manager.buy_volume:
        print(f"\t{item} consumption is balanced (wasting less than 1.0 {item})")
        return False

    print(f"\tAdjusting {item} purchase amount to {buy_volume}")

    result = await player.storehouse.items[item].patch_manager(buy_volume=buy_volume)

    if result:
        print(f"\t{item} purchase amount adjusted successfully")
        return True
    else:
        print(f"\tFailed to adjust {item} purchase amount")
        return False

async def balance_labour(player: Player) -> bool:
    return await balance_item(player, Item.Labour)
