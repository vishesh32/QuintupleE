import { GraphData } from "@/helpers/graph_data";
import React, { useState } from "react";
import { Line, LineChart, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceArea } from 'recharts'

export default function Graph({data}: {data: GraphData}){
    const [leftZoom, setLeftZoom] = useState<number | undefined>(undefined);
    const [rightZoom, setRightZoom] = useState<number | undefined>(undefined);

    return (
        <ResponsiveContainer height="80%" width="90%">
            <LineChart 
            data={data.data}
            onMouseDown={(e: any)=>{setLeftZoom(e.activeLabel); console.log(e.activeLabel)}}
            onMouseMove={(e: any)=>setRightZoom(e.activeLabel)}
            // onMouseUp={}
            >
                <XAxis dataKey={data.xValue}  />
                <YAxis></YAxis>
                <CartesianGrid stroke="#ccc" />
                <Line type='monotone' dataKey={data.yValue} stroke='#000000'></Line>
                <Tooltip></Tooltip>
                {leftZoom && leftZoom && <ReferenceArea x1={leftZoom} x2={rightZoom}></ReferenceArea>}

            </LineChart>
        </ResponsiveContainer>
    )
}