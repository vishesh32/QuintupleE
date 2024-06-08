import time
import math
import requests

DAY_LEN = 300
TICK_LEN = 5
POLLS_PER_TICK = 5

def getExternalTick():
    try:
        return requests.get("https://icelec50015.azurewebsites.net/sun").json()["tick"]
    except:
        raise Exception("Failed to get external tick")

def syncWithExternal():
    eTick = getExternalTick()

    curTick = eTick
    nextDelay = 0

    while curTick == eTick:
        curTick = getExternalTick()
        # print(f"curTick: {curTick}, eTick: {eTick}")

    prevTick = curTick

    while True:
        time.sleep(TICK_LEN/POLLS_PER_TICK - nextDelay)

        start = time.time()

        # main goes here
        eTick = getExternalTick()
        if(eTick != prevTick):
            t = time.time()
            print(f"prevTick: {prevTick}, eTick: {eTick}")
            prevTick = eTick
            with open("polling.csv", "a") as file:
                file.write(f"{t},{eTick}\n")

        end = time.time()
        nextDelay = end - start if end - start < TICK_LEN/POLLS_PER_TICK else 0

        print(f"timeout: {TICK_LEN/POLLS_PER_TICK - nextDelay}, fetch time: {end - start}")



# def getCurTick():
#     return int(math.fmod(time.time(),DAY_LEN)/TICK_LEN)

# def getSecsToNextTick(curTick):    
#     # find time of next tick in s
#     nextTick = (curTick + 1) * DAY_LEN / TICK_LEN

#     unixTime = time.time()

#     curTime = math.fmod(unixTime, DAY_LEN)
#     print(f"curTick: {curTick}, nextTick: {nextTick}, curTime: {curTime}")

#     # calc time to next tick in s
#     dt = nextTick - curTime

#     return dt

# def getAvgFetchDelay():
#     n = 1000
#     total = 0
#     for i in range(n):
#         start = time.time()
#         getExternalTick()
#         end = time.time()
#         total += end - start
        
#         if i % int(n/10) == 0:
#             print(f"i: {i}, total: {total}")

#     return total / n

# def testSync():
#     eTick = getExternalTick()
#     iTick = getCurTick()

#     if eTick != iTick:
#         print("Not Synced, eTick: ", eTick, "iTick: ", iTick)
#     # else:
#     #     print("Not synced")

if __name__ == "__main__":
    syncWithExternal()