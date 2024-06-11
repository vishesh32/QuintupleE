"use client";

import React, { useState, useRef, useEffect } from "react";
import Card from "@/components/Card/Card";
import { MQTTClient } from "@/helpers/mqtt_client";

export default function ManualControl() {
  const [inIrr, setInIrr] = useState<string>("");
  const [inStoragePower, setInStoragePower] = useState<string>("");
  const [peakPV, setPeakPV] = useState<number>(0);
  const [currentPV, setCurrentPV] = useState<number>(0);
  const [loadPowers, setLoadPowers] = useState<number[]>([0,0,0,0]);

  const mClient = useRef<MQTTClient | undefined>(undefined);

  useEffect(() => {
    if (mClient.current === undefined) mClient.current = new MQTTClient();
  }, []);

  useEffect(() => {
    if (mClient.current !== undefined) {
      if (mClient.current.pvArrayPower !== currentPV) {
        setCurrentPV(mClient.current.pvArrayPower);
        if (mClient.current.pvArrayPower > peakPV) setPeakPV(mClient.current.pvArrayPower);
      }
    }
  }, [mClient]);

  return (
    <main className="p-5 flex ml-12 mr-12 h-full gap-5">
      <div className="flex-1 flex gap-2 flex-row flex-wrap justify-center">
        <Card
          className="w-full "
          top={<p>Manual Irradiance</p>}
          middle={
            <>
              <p>Enter Irradiance</p>
              <input
                placeholder="Enter a value"
                onKeyDown={(e: any) => {
                  if (e.key === "Enter") {
                    console.log(parseFloat(inIrr));
                    mClient.current?.send_irradiance(parseFloat(inIrr));
                  }
                }}
                value={inIrr}
                onChange={(e) => setInIrr(e.target.value)}
                className="ml-auto font-normal text-2xl outline-none border-2 rounded-md text-[#828282] pl-2 pr-2"
                type="text"
              />
            </>
          }
          bottom={<p>Active</p>}
        ></Card>

        <Card
          className=""
          top={<p>Peak PV Power</p>}
          middle={<p>{peakPV}W</p>}
          bottom={<p>Average Power per 5s: -3.0W</p>}
        ></Card>

        <Card
          className=""
          top={<p>Current PV Power</p>}
          middle={<p>{currentPV}W</p>}
          bottom={<p>Average Power per 5s: -3.0W</p>}
        ></Card>

          {/* Storage Input */}
          <Card
          className=""
          top={<p>Manual Storage</p>}
          middle={
            <>
              <p>Enter Power</p>
              <input
                placeholder="Enter a value"
                onKeyDown={(e: any) => {
                  if (e.key === "Enter") {
                    console.log(parseFloat(inStoragePower));
                    mClient.current?.send_storage_power(parseFloat(inStoragePower));
                  }
                }}
                value={inStoragePower}
                onChange={(e) => setInStoragePower(e.target.value)}
                className="ml-auto font-normal text-2xl outline-none border-2 rounded-md text-[#828282] pl-2 pr-2"
                type="text"
              />
            </>
          }
          bottom={<p>Active</p>}
        ></Card>

      </div>

      <div className="flex-1 flex flex-row gap-2 flex-wrap justify-center">
        {/* LED Loads */}
        <Card
          className=""
          top={
            <p>
              Manual Load (LED <span className="text-[#3A9BDC]">Blue</span>)
            </p>
          }
          middle={<p>3.6W</p>}
          bottom={<p>Average Power per 5s: -3.0W</p>}
        ></Card>
        <Card
          className=""
          top={
            <p>
              Manual Load (LED <span className="text-[#808080]">Grey</span>)
            </p>
          }
          middle={<p>3.6W</p>}
          bottom={<p>Average Power per 5s: -3.0W</p>}
        ></Card>
        <Card
          className=""
          top={
            <p>
              Manual Load (LED <span className="text-[#FF0000]">Red</span>)
            </p>
          }
          middle={<p>3.6W</p>}
          bottom={<p>Average Power per 5s: -3.0W</p>}
        ></Card>
        <Card
          className=""
          top={
            <p>
              Manual Load (LED <span className="text-[#F6BE00]">Yellow</span>)
            </p>
          }
          middle={<p>3.6W</p>}
          bottom={<p>Average Power per 5s: -3.0W</p>}
        ></Card>
      </div>
    </main>
  );
}
