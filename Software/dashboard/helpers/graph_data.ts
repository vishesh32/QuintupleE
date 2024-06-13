import { GraphData, Variable, FormatString, GraphType } from '@/helpers/graph_types';

const x = "tick"

const AllVars = {
    irradiance: new Variable("sun", "%", GraphType.Line),
    real_pv_power: new Variable("avg_pv_power", "Watts", GraphType.Line),
    real_import_power: new Variable("avg_import_export_power", "Watts", GraphType.Line),
    algo_import_power: new Variable("algo_import_power", "Watts", GraphType.Line),
    buy: new Variable("buy_price", "Cents", GraphType.Line),
    sell: new Variable("sell_price", "Cents", GraphType.Line),
    real_storage_power: new Variable("avg_storage_power", "Watts", GraphType.Line),
    algo_storage_power: new Variable("algo_store_power", "Watts", GraphType.Line),
    exp_instant_demand: new Variable("demand", "Watts", GraphType.Line),
    real_instant_demand: new Variable("avg_red_power", "Watts", GraphType.Line),
    soc: new Variable("storage_soc", "%", GraphType.Line),
    algo_blue_def: new Variable("algo_blue_power", "Watts", GraphType.Bar),
    algo_grey_def: new Variable("algo_grey_power", "Watts", GraphType.Bar),
    algo_yellow_def: new Variable("algo_yellow_power", "Watts", GraphType.Bar),
    real_blue_def: new Variable("avg_blue_power", "Watts", GraphType.Bar),
    real_grey_def: new Variable("avg_grey_power", "Watts", GraphType.Bar),
    real_yellow_def: new Variable("avg_yellow_power", "Watts", GraphType.Bar),
}

const AllGraphs: GraphData[] = [
    {
        title: "Irradiance vs Real PV Power",
        xValue: x,
        unitData1: [AllVars.irradiance],
        unitData2: [AllVars.real_pv_power],
        data: null,
    },
    {
        title: "Real Import Power vs Buy and Sell Prices",
        xValue: x,
        unitData1: [AllVars.real_import_power, AllVars.algo_import_power],
        unitData2: [AllVars.buy, AllVars.sell],
        data: null,
    },
    {
        title: "SOC, Buy and Sell Prices",
        xValue: x,
        unitData1: [AllVars.soc],
        unitData2: [AllVars.buy, AllVars.sell],
        data: null,
    },
    {
        title: "Storage Power vs Buy and Sell Prices",
        xValue: x,
        unitData1: [AllVars.real_storage_power, AllVars.algo_storage_power],
        unitData2: [AllVars.buy, AllVars.sell],
        data: null,
    },
    {
        title: "Instant Demand vs Expected Instant Demand",
        xValue: x,
        unitData1: [AllVars.real_instant_demand, AllVars.exp_instant_demand],
        unitData2: [],
        data: null,
    },
    {
        title: "Deferrables",
        xValue: x,
        unitData1: [AllVars.real_blue_def, AllVars.algo_blue_def, AllVars.real_grey_def, AllVars.algo_grey_def, AllVars.real_yellow_def, AllVars.algo_yellow_def],
        unitData2: [AllVars.buy, AllVars.sell],
        data: null,
    }
]

const Colours = [
	"#2D6EFF",
	"#F25F4C",
	"#2CB67D",
	"#FF8906",
	"#E53170",
	"#000000",
	"#fec7d7",
	"#994ff3",
]

export { AllGraphs, AllVars, x, Colours }