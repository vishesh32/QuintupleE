"use client";

import React, { useEffect, useRef, useState } from "react";
import Card from "@/components/Card/Card";
import Graph from "@/components/Graph/Graph";
import { getTick } from "../actions";
import { GraphData, Variable } from "@/helpers/graph_types";
import { AllVars, AllGraphs } from "@/helpers/graph_data";

export default function History() {
  const [graphData, setGraphData] = useState<GraphData[]>([]);

  useEffect(() => {
    if (graphData.length == 0) {
      for (let graph of AllGraphs) {
        // get yvalues
        var yValues: any = {};

        for (let unit1 of graph.unitData1) {
          yValues[unit1.yValue] = 1;
        }

        for (let unit2 of graph.unitData2) {
          yValues[unit2.yValue] = 1;
        }

        // console.log(yValues);
        // console.log(graph.title);

        getTick(yValues).then((data: any) => {
          setGraphData((prev) => {
            let gData = graph;
            gData.data = data;
            return [...prev, gData];
          });
        });
      }
    }
  }, []);

  return (
    <div>
      <main className="w-full mt-6 grid gap-5 2xl:grid-cols-2 px-8">
        {graphData.map((data, i) => (
          <Graph key={i} data={data} animation={false} />
        ))}
      </main>
    </div>
  );
}
