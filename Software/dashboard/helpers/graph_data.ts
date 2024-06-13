enum Collection {
    days = "days",
    ticks = "ticks",
}

interface Variable {
    name: string,
    value: string,
    units: string,
    collection: Collection,
}

const AllVars : Variable[] = [
    {
        name: "Buy Price",
        value: "buy_price",
        units: "Cents",
        collection: Collection.ticks,
    },
    {
        name: "Sell Price",
        value: "sell_price",
        units: "Cents",
        collection: Collection.ticks,
    },
    {
        name: "Demand",
        value: "demand",
        units: "Watts",
        collection: Collection.ticks,
    },
    {
        name: "Irradiance",
        value: "sun",
        units: "%",
        collection: Collection.ticks,
    },
    {
        name: "Cost",
        value: "cost",
        units: "Cents",
        collection: Collection.ticks,
    },
];

const xValues = {
    day: 1,
    tick: 1,
}

// interface GraphData {
//     id: number,
//     xValue: string,
//     yValue: string,
//     data: any
// }

class GraphData {
    id: number;
    xValue: string;
    yValue: string;
    data: any;

    constructor(id: number, xValue: string, yValue: string, data: any) {
        this.id = id;
        this.xValue = xValue;
        this.yValue = yValue;
        this.data = data;
    }

    getXLabel() {
        return FormatString(this.xValue);
    }
    getYLabel() {
        return FormatString(this.yValue);
    }
}

function FormatString(s: string){
    return s.split("_").map((word) => word.charAt(0).toUpperCase() + word.slice(1)).join(" ");
}

export { AllVars, GraphData, FormatString, xValues };
export type { Variable }