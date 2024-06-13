enum GraphType {
    Bar = 0,
    Line = 1,
}

class Variable {
    yValue: string;
    yUnit: string;
    graphType: GraphType;

    constructor(yValue: string, yUnit: string, graphType: GraphType) {
        this.yValue = yValue;
        this.yUnit = yUnit;
        this.graphType = graphType;
    }

    getYUnit() {
        return FormatString(this.yUnit);
    }
    getYLabel() {
        return FormatString(this.yValue);
    }
}

interface GraphData {
    title: string;
    xValue: string;
    unitData1: Variable[];
    unitData2: Variable[];
    data: any;
}

function FormatString(s: string){
    return s.split("_").map((word) => word.charAt(0).toUpperCase() + word.slice(1)).join(" ");
}


export { Variable, FormatString, GraphType }
export type { GraphData }