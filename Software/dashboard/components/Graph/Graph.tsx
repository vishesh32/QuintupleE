import { GraphData } from "@/helpers/graph_data";
import React, { useState } from "react";
import {
  Line,
  LineChart,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceArea,
} from "recharts";
import {
  MagnifyingGlassMinusIcon,
  ArrowsPointingOutIcon,
  ArrowsPointingInIcon,
  TrashIcon,
} from "@heroicons/react/24/outline";

export default function Graph({
  data,
  handleRemoveGraph,
  graphFullScreen,
  setGraphFullScreen,
}: {
  data: GraphData;
  handleRemoveGraph: ((data: GraphData) => void) | null;
  graphFullScreen: GraphData | null;
  setGraphFullScreen: React.Dispatch<React.SetStateAction<GraphData | null>>;
}) {

  const [leftZoom, setLeftZoom] = useState<number | undefined>(undefined);
  const [rightZoom, setRightZoom] = useState<number | undefined>(undefined);
  const [leftDom, setLeftDom] = useState<number>(0);
  const [rightDom, setRightDom] = useState<number>(data.data.length);

  const handleMouseDown = (e: any) => {
    if (leftZoom == undefined) {
      // first click sets the value of the left zoom point
      setLeftZoom(e.activeTooltipIndex);
    } 
    else if (rightZoom != undefined) {
      // second click sets the value of the right zoom click

      if (leftZoom < rightZoom) {
        setLeftDom(leftZoom - 1);
        setRightDom(rightZoom - 1);
      } 
      else {
        // incase first selected the RHS
        setLeftDom(rightZoom - 1);
        setRightDom(leftZoom - 1);
      }

      setLeftZoom(undefined);
      setRightZoom(undefined);
    } 
    else {
      setLeftZoom(undefined);
      setRightZoom(undefined);
    }
  };

  const handleZoomOut = () => {
    setLeftDom(0);
    setRightDom(data.data.length);
    setLeftZoom(undefined);
    setRightZoom(undefined);
  };

  const makeBigger = () => setGraphFullScreen(data);

  const makeSmaller = () => setGraphFullScreen(null);

  return (
    <div className="w-full h-full bg-blue flex flex-col justify-center items-center">
      <div className="w-full flex p-1">

        {handleRemoveGraph != null && (
          <button
            className="bg-[#e16162] ml-[120px] p-2 rounded-full"
            onClick={(e: any) => handleRemoveGraph(data)}
          >
            <TrashIcon className="size-6" />
          </button>
        )}

        <button
          className="bg-primary p-2 rounded-full ml-auto"
          onClick={handleZoomOut}
        >
          <MagnifyingGlassMinusIcon className="size-6 text-white" />
        </button>

        <button
          className="bg-primary p-2 rounded-full ml-[20px] mr-[50px]"
          onClick={graphFullScreen === null ? makeBigger : makeSmaller}
        >
          {graphFullScreen === null ? (
            <ArrowsPointingOutIcon className="size-6 text-white" />
          ) : (
            <ArrowsPointingInIcon className="size-6 text-white" />
          )}
        </button>

      </div>


      <ResponsiveContainer height="80%" width="90%">
        <LineChart
          data={data.data.slice(leftDom, rightDom)}
          onMouseDown={handleMouseDown}
          onMouseMove={(e: any) => {
            if (leftZoom) setRightZoom(e.activeTooltipIndex);
          }}
        >
          <XAxis allowDataOverflow dataKey={data.xValue} label={{value: data.getXLabel(), position: 'insideBottom', offset: -5}} padding={{left: 5, right: 5}} />
          <YAxis allowDataOverflow label={{value: data.getYLabel(), angle: -90, position: 'insideLeft'}} />
          <CartesianGrid stroke="#ccc" />
          <Line type="monotone" dataKey={data.yValue} stroke="#000000"></Line>
          <Tooltip></Tooltip>
          {leftZoom && rightZoom && (
            <ReferenceArea x1={leftZoom} x2={rightZoom}></ReferenceArea>
          )}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
