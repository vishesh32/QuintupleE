
// async function getSimData() : Promise<SimData> {
//     // possible problem is ticks might be different
//     // if different -> request all again

//     // const [price, demand, sun] = await Promise.all([
//     //     (await fetch("https://icelec50015.azurewebsites.net/price", {mode: "no-cors"})).json(), 
//     //     (await fetch("https://icelec50015.azurewebsites.net/demand", {mode: "no-cors"})).json(), 
//     //     (await fetch("https://icelec50015.azurewebsites.net/sun", {mode: "no-cors"})).json()
//     // ]);

//     // return {
//     //     day: price.day,
//     //     tick: price.tick,
//     //     buyPrice: price.buy_price,
//     //     sellPrice: price.sell_price,
//     //     demand: demand.demand,
//     //     sun: sun.sun,
//     // }
// }

// interface SimData{
//     day: number,
//     tick: number,
//     buyPrice: number,
//     sellPrice: number,
//     demand: number,
//     sun: number

// }

// export type { SimData }
// export { getSimData }