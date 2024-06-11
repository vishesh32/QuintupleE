import asyncio
import aiohttp

# runs an aysnc get request
async def get(client : aiohttp.ClientSession, url):
    res = await client.get(url, ssl=True)
    return await res.json()

# uses connection pooling:
# will use the same tcp connection where it can
async def parallel_get(base_url, paths):
    client = None
    res = None

    try:
        client = aiohttp.ClientSession(base_url=base_url)
        res = await asyncio.gather(*[get(client, path) for path in paths])

    except Exception as e:
        print(e)

    finally:
        if client: await client.close()
        if res == None:
            return [None] * len(paths)
        else:
            return res

if __name__ == "__main__":
    urls = ["/sun","/price","/demand","/deferables"]
    print(asyncio.run(parallel_get("https://icelec50015.azurewebsites.net/", urls)))