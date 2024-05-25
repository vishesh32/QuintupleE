'use server'

import { emptySimData, SimData } from "@/helpers/sim_data";

// this is a server action
// used as a proxy as external web server is missing the 'Access-Control-Allow-Origin' header
async function getSimData() : Promise<SimData> {
    // possible problem is ticks might be different
    // if different -> request all again

    try{
        const [price, demand, sun, deferables] = await Promise.all([
            (await fetch("https://icelec50015.azurewebsites.net/price")).json(), 
            (await fetch("https://icelec50015.azurewebsites.net/demand")).json(), 
            (await fetch("https://icelec50015.azurewebsites.net/sun")).json(),
            (await fetch("https://icelec50015.azurewebsites.net/deferables")).json()
        ]);

        return {
            day: price.day,
            tick: price.tick,
            buyPrice: price.buy_price,
            sellPrice: price.sell_price,
            demand: demand.demand,
            sun: sun.sun,
            deferables: deferables,
        }
    } catch {
        return emptySimData;
    }
}

export { getSimData }