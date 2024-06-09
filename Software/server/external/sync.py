from external.parallel_get import get_day_and_tick

def sync_with_server(curTick, tick_len=5):
    eTick = curTick

    while curTick == eTick:
        day, tick = get_day_and_tick(tick_len)
        eTick = tick.tick

    return day, tick