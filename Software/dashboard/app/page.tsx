"use client"

import React, {useEffect, useRef, useState} from 'react'
import Card from '../components/Card/Card';
import CreateGraph from '../components/Modals/CreateGraph/CreateGraph';
import Graph from '@/components/Graph/Graph'
import { getTick } from './actions';
import { GraphData } from '@/helpers/graph_data';
import History from './history/page';
import { MQTTClient } from '@/helpers/mqtt_client';

export default function Home() {
  // const [graphData, setGraphData] = useState<GraphData[]>([]);
  // const mqttClient = useRef<MQTTClient | undefined>(undefined);

  // const addGraphData = (data: any){
  //   const newGraphData = new GraphData(0, "ticks", "power_out", data);
  // }

  // useEffect(() => {
  //   if(mqttClient.current == undefined) mqttClient.current = new MQTTClient();
  // }, []);

  // return (
  //   <Card className=''>
  //     {graphData.length == 1 && <Graph data={graphData[0]}></Graph>}
  //   </Card>
  // );
  return null;
}
