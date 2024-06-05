import React from "react";
import { Line, LineChart } from 'recharts'

export default function Graph({data}: any){
    return (
        <LineChart width={500} height={300} data={data}>
            <Line type='monotone' dataKey={0} stroke='#000000'></Line>
        </LineChart>
    )
}