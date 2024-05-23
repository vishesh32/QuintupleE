interface SimData{
    day: number,
    tick: number,
    buyPrice: number,
    sellPrice: number,
    demand: number,
    sun: number,
    deferables: ({end: number, energy: number, start: number})[]
}

const emptySimData : SimData = {
    day: 0,
    tick: 0,
    buyPrice: 0,
    sellPrice: 0,
    demand: 0,
    sun: 0,
    deferables: []
}; 

export type { SimData }
export { emptySimData }