import Graph from '../components/Graph/Graph';
interface Variables {
    name: string,
    value: string
}

const AllVars : Variables[] = [
    {
        name: "Buy Price (Cents)",
        value: "buy_price",
    },
    {
        name: "Sell Price (Cents)",
        value: "sell_price",
    },
    {
        name: "Demand (Watts)",
        value: "demand",
    },
    {
        name: "Irradiance (%)",
        value: "sun",
    }
];

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

export { AllVars, GraphData, FormatString };