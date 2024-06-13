"use client";

import React, { useEffect, useRef, useState } from "react";
import { getDayAndTick, getValuesOnTick } from "./actions";
import { LiveGraphs } from "@/helpers/graph_data";
import { getYValues } from "@/helpers/graph_funcs";
import Graph from "@/components/Graph/Graph";
import { GraphData } from "@/helpers/graph_types";

export default function Home() {
  const [day, setDay] = useState(0);
  const [tick, setTick] = useState(0);
  const [graphData, setGraphData] = useState<GraphData[]>(LiveGraphs);

  const changeGraphData = async (prevDay: number, prevTick: number) => {
    const nextDay = prevTick == 59 ? prevDay + 1 : prevDay;
    const nextTick = (prevTick + 1) % 60;
    setDay(nextDay);
    setTick(nextTick);

    let tmpGraphData = [...graphData];

    console.log(day, tick);

    for (let graph of tmpGraphData) {
      const yValues = getYValues(graph);

      let data = await getValuesOnTick(yValues, nextDay, nextTick);
      console.log(data);
      if (data) {
        graph.data.push(data);
      }
    }

    setGraphData([...tmpGraphData]);

    console.log(graphData);

    // const timeoutId = setTimeout(()=>{
    //   changeGraphData(day, tick)
    //   console.log(timeoutId)
    //   clearTimeout(timeoutId)
    // }, 5000)

    // console.log(timeoutId)
  };

  useEffect(() => {
    // get the current day and tick
    // check if data from the last tick is available
    getDayAndTick().then((res) =>
      changeGraphData(
        res.tick == 0 ? res.day - 1 : res.day,
        res.tick == 0 ? 59 : res.tick - 1
      )
    );
  }, []);

  return (
    <main className="w-full mt-6 grid gap-5 2xl:grid-cols-2 px-8">
      {graphData.map((data, i) => (
        <Graph key={i} data={data} animation={false} />
      ))}
    </main>
  );
}
