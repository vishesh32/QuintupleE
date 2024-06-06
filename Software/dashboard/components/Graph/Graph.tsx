import { GraphData } from "@/helpers/graph_data";
import React from "react";
import { Line, LineChart, XAxis, YAxis, CartesianGrid, Tooltip } from 'recharts'

export default function Graph({data}: {data: GraphData}){
    return (
        <LineChart width={800} height={450} data={data.data.slice(0, 20)}>
            <XAxis dataKey={data.xValue}  />
            <YAxis></YAxis>
            <CartesianGrid stroke="#ccc" />
            <Line type='monotone' dataKey={data.yValue} stroke='#000000'></Line>
            <Tooltip></Tooltip>
        </LineChart>
    )
}