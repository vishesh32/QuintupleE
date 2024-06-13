import { GraphData, FormatString } from "@/helpers/graph_data";
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
  ComposedChart,
  Legend
} from "recharts";
import {
  MagnifyingGlassMinusIcon,
  ArrowsPointingOutIcon,
  ArrowsPointingInIcon,
  TrashIcon,
} from "@heroicons/react/24/outline";

export default function Graph({
  data,
  animation = false,
}: {
  data: GraphData;
  animation: boolean;
}) {
  const [graphFullScreen, setGraphFullScreen] = useState<Boolean>(false);

  return (
    <>
      {graphFullScreen && (
        <div className="fixed w-full h-full z-10 bg-black/50 backdrop-blur-sm top-0 flex justify-center items-center">
          <Plot
            className="h-[70%] w-[90%]"
            data={data}
            animation={animation}
            graphFullScreen={graphFullScreen}
            setGraphFullScreen={setGraphFullScreen}
          ></Plot>
        </div>
      )}
      <Plot
      className="h-[600px]"
        data={data}
        animation={animation}
        graphFullScreen={graphFullScreen}
        setGraphFullScreen={setGraphFullScreen}
      ></Plot>
    </>
  );
}

function Plot({
  data,
  graphFullScreen,
  setGraphFullScreen,
  className,
  animation = false,
}: {
  data: GraphData;
  graphFullScreen: Boolean;
  setGraphFullScreen: React.Dispatch<React.SetStateAction<Boolean>>;
  className: string;
  animation: boolean;
}) {
  const [leftZoom, setLeftZoom] = useState<number | undefined>(undefined);
  const [rightZoom, setRightZoom] = useState<number | undefined>(undefined);
  const [leftDom, setLeftDom] = useState<number>(0);
  const [rightDom, setRightDom] = useState<number>(data.data.length);

  const handleMouseDown = (e: any) => {
    if (leftZoom == undefined) {
      // first click sets the value of the left zoom point
      setLeftZoom(e.activeTooltipIndex);
    } else {
      setLeftZoom(undefined);
      setRightZoom(undefined);
    }
  };

  const handleMouseUp = (e: any) => {
    if (leftZoom != undefined && rightZoom != undefined) {
      // second click sets the value of the right zoom click

      if (leftZoom < rightZoom) {
        setLeftDom(leftZoom - 1);
        setRightDom(rightZoom - 1);
      } else {
        // incase first selected the RHS
        setLeftDom(rightZoom - 1);
        setRightDom(leftZoom - 1);
      }
    }

    setLeftZoom(undefined);
    setRightZoom(undefined);
  };

  const handleZoomOut = () => {
    setLeftDom(0);
    setRightDom(data.data.length);
    setLeftZoom(undefined);
    setRightZoom(undefined);
  };

  const makeBigger = () => setGraphFullScreen(true);
  const makeSmaller = () => setGraphFullScreen(false);

  return (
    <div className={`w-full bg-blue flex flex-col justify-center items-center bg-primary rounded-2xl ${className}`}>
      {/* Control buttons */}
      <div className="w-full flex p-1 pb-4">
        <button
          className="bg-secondary p-2 rounded-full ml-auto"
          onClick={handleZoomOut}
        >
          <MagnifyingGlassMinusIcon className="size-6 text-primary" />
        </button>

        <button
          className="bg-secondary p-2 rounded-full ml-[10px] mr-[50px]"
          onClick={!graphFullScreen ? makeBigger : makeSmaller}
        >
          {!graphFullScreen ? (
            <ArrowsPointingOutIcon className="size-6 text-primary" />
          ) : (
            <ArrowsPointingInIcon className="size-6 text-white" />
          )}
        </button>
      </div>
      <ResponsiveContainer height="80%" width="90%">
        <ComposedChart
          data={data.data.slice(leftDom, rightDom)}
          onMouseDown={handleMouseDown}
          onMouseMove={(e: any) => {
            if (leftZoom) setRightZoom(e.activeTooltipIndex);
          }}
          onMouseUp={handleMouseUp}
          margin={{ bottom: 30 }}
          className="select-none"
        >
          <XAxis
            allowDataOverflow
            dataKey={data.xValue}
            label={{
              value: data.getXLabel(),
              position: "insideBottom",
              offset: -5,
            }}
            padding={{ left: 5, right: 5 }}
          />

          <YAxis
            allowDataOverflow
            label={{
              value: data.getYLabel(),
              angle: -90,
              position: "insideLeft",
            }}
          />
          <CartesianGrid stroke="#ccc" />

          <Line
            isAnimationActive={animation}
            type="monotone"
            dataKey={data.yValue}
            // stroke="#000000"
            activeDot={{ r: 3 }}
            dot={{ r: 3 }}
          ></Line>

          <Tooltip content={CustomTooltip}></Tooltip>

          <Legend></Legend>

          {leftZoom && rightZoom && (
            <ReferenceArea x1={leftZoom} x2={rightZoom}></ReferenceArea>
          )}
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
}

// tooltip show when hovering over datapoint
function CustomTooltip({ active, payload, label }: any) {
  let data = [];
  if (active && payload && payload.length > 0 && payload[0].payload) {
    // console.log(payload[0].payload);
    for (let key in payload[0].payload) {
      // console.log(key, payload[0].payload[key]);
      data.push([FormatString(key), payload[0].payload[key]]);
    }
  }

  return active ? (
    <div className="text-black bg-white p-3 rounded-md bg-opacity-90">
      {data.map((d, i) => (
        <p key={i}>
          {d[0]}: {d[1]}
        </p>
      ))}
    </div>
  ) : undefined;
}
