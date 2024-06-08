"use client";

import React, { useEffect, useRef, useState } from "react";
import Card from "@/components/Card/Card";
import CreateGraph from "@/components/Modals/CreateGraph/CreateGraph";
import Graph from "@/components/Graph/Graph";
import { getTick } from "../actions";
import { GraphData } from "@/helpers/graph_data";

export default function History() {
  const [plotGraphModal, setPlotGraphModal] = useState<boolean>(false);
  const [graphFullScreen, setGraphFullScreen] = useState<GraphData | null>(
    null
  );
  const [graphData, setGraphData] = useState<GraphData[]>([]);
  const idCount = useRef<number>(0);

  const handleAddPlot = () => setPlotGraphModal(true);

  const addGraphData = (data: any, opt: string) => {
    if (data != null && data != undefined) {
      var gData = new GraphData(idCount.current,"tick",opt,data)
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

  // useEffect(() => {
  //   var opt = "buy_price";
  //   getTick(opt).then((data) => addGraphData(data, opt));
  // }, []);

  return (
    <div>
      {(plotGraphModal || graphFullScreen) && (
        <div className="bg-black w-full h-full z-[10] fixed top-0 bg-opacity-20 backdrop-blur-sm flex justify-center items-center duration-300">
          {plotGraphModal && (
            <CreateGraph
              setPlotGraphModal={setPlotGraphModal}
              addGraph={addGraphData}
            ></CreateGraph>
          )}
          {graphFullScreen && (
            <Card className="h-[80%] animate-ttb">
              <Graph
                data={graphFullScreen}
                handleRemoveGraph={null}
                graphFullScreen={graphFullScreen}
                setGraphFullScreen={setGraphFullScreen}
                animation={true}
              />
            </Card>
          )}
        </div>
      )}
      <main className="w-full mt-6 grid 2xl:grid-cols-2">
        {graphData.map((data, i) => (
          <Card className="" key={i}>
            <Graph
              handleRemoveGraph={removeGraph}
              graphFullScreen={graphFullScreen}
              data={data}
              setGraphFullScreen={setGraphFullScreen}
              animation={true}
            ></Graph>
          </Card>
        ))}

        <Card className="hover:brightness-[95%] duration-150">
          <button className="w-full h-full" onClick={handleAddPlot}>
            <p className="text-[#001E1D] text-opacity-80 text-[100px]">+</p>
          </button>
        </Card>
      </main>
    </div>
  );
}
