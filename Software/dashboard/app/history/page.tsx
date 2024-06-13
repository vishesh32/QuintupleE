"use client";

import React, { useEffect, useRef, useState } from "react";
import Card from "@/components/Card/Card";
import CreateGraph from "@/components/Modals/CreateGraph/CreateGraph";
import Graph from "@/components/Graph/Graph";
import { getTick } from "../actions";
import { AllVars, GraphData, Variable } from "@/helpers/graph_data";

let once = false;

export default function History() {
  const [plotGraphModal, setPlotGraphModal] = useState<boolean>(false);
  const [graphFullScreen, setGraphFullScreen] = useState<GraphData | null>(
    null
  );
  const [graphData, setGraphData] = useState<GraphData[]>([]);
  const idCount = useRef<number>(0);

  const handleAddPlot = () => setPlotGraphModal(true);

  const addGraphData = (data: any, opt: Variable) => {
    if (data != null && data != undefined) {
      var gData = new GraphData(idCount.current,"tick",opt.value,data)
      // console.log(gData)
      setGraphData((prev) => [...prev, gData]);
      idCount.current += 1;
    }
  };

  const removeGraph = (data: GraphData) => {
    const idx = graphData.indexOf(data);
    setGraphData((prev) => {
      return prev.toSpliced(idx, 1);
    });
  };

  useEffect(() => {
    if(!once) getTick(AllVars[0]).then((data) => addGraphData(data, AllVars[0]));
    once = true;
    console.log(graphData)
  }, [graphData]);

  return (
    <div>
      <main className="w-full mt-6 grid 2xl:gap-2 2xl:grid-cols-2">
        {graphData.map((data, i) => (<Graph key={i} data={data} animation={false} />))}
      </main>
    </div>
  );
}
