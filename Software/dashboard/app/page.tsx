"use client"

import React, {useEffect, useRef, useState} from 'react'
import Card from '../components/Card/Card';
import CreateGraph from '../components/Modals/CreateGraph/CreateGraph';
import Graph from '@/components/Graph/Graph'
import { getTick } from './actions';
import { GraphData } from '@/helpers/graph_data';

export default function Home() {
  const [plotGraphModal, setPlotGraphModal] = useState<boolean>(false);
  const [graphData, setGraphData] = useState<GraphData[]>([]);

  const handleAddPlot = ()=>setPlotGraphModal(true);

  const addGraphData = (data: any, opt: string)=>{
    if(data != null && data != undefined){
      var gData: GraphData = {
        xValue: "tick",
        yValue: opt,
        data: data,
      }
      console.log(gData)
      setGraphData((prev)=>[...prev, gData]);
    }
  };

  useEffect(()=>{
    var opt = "buy_price";
    getTick(opt).then((data)=>addGraphData(data, opt))
  }, [])

  return (
    <div>
      {plotGraphModal && (
        <div 
        className='bg-black w-full h-full z-[10] fixed top-0 bg-opacity-20 backdrop-blur-sm flex justify-center items-center duration-300'>
          <CreateGraph setPlotGraphModal={setPlotGraphModal} addGraph={addGraphData} ></CreateGraph>
        </div>
      )}
      <main className="flex justify-start mt-6 flex-row items-start flex-wrap" >
        {graphData.map((data, i)=>(
          <Card className='' key={i}>
            <Graph data={data}>
            </Graph>
          </Card>
        ))}

        <Card className="hover:mt-4 duration-150">
          <button className='w-full h-full' onClick={handleAddPlot}>
            <p className='text-[#001E1D] text-opacity-80 text-[100px]'>+</p>
          </button>
        </Card>
      </main>
    </div>
  );
}
