"use client";

import React, { useState, useRef, useEffect } from "react";
import Card from "@/components/Card/Card";
import { MQTTClient, Device } from "@/helpers/mqtt_client";
import Graph from "../../components/Graph/Graph";

const inputClass =
  "ml-auto font-normal text-2xl outline-none border-2 rounded-md text-[#828282] pl-2 pr-2";

export default function ManualControl() {
  const [inIrr, setInIrr] = useState<string>("");
  const [inStoragePower, setInStoragePower] = useState<string>("");
  const [peakPV, setPeakPV] = useState<number>(0);
  const [currentPV, setCurrentPV] = useState<number>(0);
  const [loadPowers, setLoadPowers] = useState<number[]>([0, 0, 0, 0]);
  const [importPower, setImportPower] = useState<number>(0);
  const [exportPower, setExportPower] = useState<number>(0);
  const [soc, setSoc] = useState<number>(0);
  const [socPower, setSocPower] = useState<number>(0);

  const [override, setOverride] = useState<boolean>(false);

  const mClient = useRef<MQTTClient | undefined>(undefined);

  useEffect(() => {
    if (mClient.current === undefined)
      mClient.current = new MQTTClient(
        setCurrentPV,
        setLoadPowers,
        setImportPower,
        setExportPower,
        setSoc,
        setSocPower
      );
  }, []);

  useEffect(() => {
    // console.log("running effect cb");
    if (currentPV > peakPV) setPeakPV(currentPV);
  }, [currentPV, peakPV]);

  const handleOverrideClick = () => {
    setOverride(!override);
  };

  return (
    <div>
      <div className="w-full flex flex-row gap-2 flex-wrap justify-center p-5 pt-8">
        <button
          onClick={handleOverrideClick}
          className={`${
            override ? "bg-green-600" : "bg-red-600"
          } h-fit w-[350px] text-primary py-3 rounded-lg`}
        >
          Click To{" "}
          {override
            ? "Control With The Algorithm"
            : "Manually Override Controls"}
        </button>
      </div>
      <main className="p-5 flex ml-12 mr-12 h-full gap-5">
        <div className="flex-1 flex gap-2 flex-row flex-wrap justify-center">
          <Card
            className="w-full "
            top={<p>Manual Irradiance</p>}
            middle={
              <>
                <p>Enter Irradiance</p>
                <input
                  disabled={!override}
                  placeholder="Enter a value"
                  onKeyDown={(e: any) => {
                    if (e.key === "Enter") {
                      // console.log(parseFloat(inIrr));
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
            bottom={<p>PV Array</p>}
          ></Card>

          <Card
            className=""
            top={<p>Peak PV Power</p>}
            middle={<p>{peakPV}W</p>}
            bottom={<p>PV Array</p>}
          ></Card>

          <Card
            className=""
            top={<p>Current PV Power</p>}
            middle={<p>{currentPV}W</p>}
            bottom={<p>PV Array</p>}
          ></Card>

          {/* Storage Input */}
          <Card
            className=""
            top={<p>Manual Storage</p>}
            middle={
              <>
                <p>Enter Power</p>
                <input
                  disabled={!override}
                  placeholder="Enter a value"
                  onKeyDown={(e: any) => {
                    if (e.key === "Enter") {
                      // console.log(parseFloat(inStoragePower));
                      mClient.current?.send_storage_power(
                        parseFloat(inStoragePower)
                      );
                    }
                  }}
                  value={inStoragePower}
                  onChange={(e) => setInStoragePower(e.target.value)}
                  className={inputClass}
                  type="text"
                />
              </>
            }
            bottom={<p>Storage</p>}
          ></Card>

          <Card
            className="w-[260px]"
            top={<p>SOC Power</p>}
            middle={<p>{socPower}W</p>}
            bottom={<p>Storage</p>}
          />
          <Card
            className="w-[260px]"
            top={<p>SOC</p>}
            middle={<p>{soc}%</p>}
            bottom={<p>Storage</p>}
          />

          {/* External Grid Outputs */}
          <Card
            className="w-[260px]"
            top={<p>Import Power</p>}
            middle={<p>{importPower}W</p>}
            bottom={<p>Storage</p>}
          />
          <Card
            className="w-[260px]"
            top={<p>Export Power</p>}
            middle={<p>{exportPower}W</p>}
            bottom={<p>External Grid</p>}
          />
        </div>

        <div className="flex-1 flex flex-row gap-2 flex-wrap justify-center">
          {/* LED Loads */}
          <Card
            className=""
            top={
              <p>
                Manual Load (LED <span className="text-[#FF0000]">Red</span>)
              </p>
            }
            middle={
              <>
                <p>{loadPowers[0]}W</p>
                <input
                  disabled={!override}
                  onKeyDown={(e: any) => {
                    if (e.key === "Enter") {
                      // console.log(e.target.value);
                      mClient.current?.send_load_power(
                        parseFloat(e.target.value),
                        Device.LOADR
                      );
                    }
                  }}
                  className={inputClass}
                  placeholder="Send Power To Load"
                  type="text"
                />
              </>
            }
            bottom={<p>Instant Load</p>}
          ></Card>
          <Card
            className=""
            top={
              <p>
                Manual Load (LED <span className="text-[#3A9BDC]">Blue</span>)
              </p>
            }
            middle={
              <>
                <p>{loadPowers[1]}W</p>
                <input
                  disabled={!override}
                  onKeyDown={(e: any) => {
                    if (e.key === "Enter") {
                      // console.log(e.target.value);
                      mClient.current?.send_load_power(
                        parseFloat(e.target.value),
                        Device.LOADB
                      );
                    }
                  }}
                  className={inputClass}
                  placeholder="Send Power To Load"
                  type="text"
                />
              </>
            }
            bottom={<p>Deferrable Load</p>}
          ></Card>
          <Card
            className=""
            top={
              <p>
                Manual Load (LED <span className="text-[#808080]">Grey</span>)
              </p>
            }
            middle={
              <>
                <p>{loadPowers[3]}W</p>
                <input
                  disabled={!override}
                  onKeyDown={(e: any) => {
                    if (e.key === "Enter") {
                      // console.log(e.target.value);
                      mClient.current?.send_load_power(
                        parseFloat(e.target.value),
                        Device.LOADK
                      );
                    }
                  }}
                  className={inputClass}
                  placeholder="Send Power To Load"
                  type="text"
                />
              </>
            }
            bottom={<p>Deferrable Load</p>}
          ></Card>
          <Card
            className=""
            top={
              <p>
                Manual Load (LED <span className="text-[#F6BE00]">Yellow</span>)
              </p>
            }
            middle={
              <>
                <p>{loadPowers[2]}W</p>
                <input
                  disabled={!override}
                  onKeyDown={(e: any) => {
                    if (e.key === "Enter") {
                      // console.log(e.target.value);
                      mClient.current?.send_load_power(
                        parseFloat(e.target.value),
                        Device.LOADY
                      );
                    }
                  }}
                  className={inputClass}
                  placeholder="Send Power To Load"
                  type="text"
                />
              </>
            }
            bottom={<p>Deferrable Load</p>}
          ></Card>
        </div>
      </main>
    </div>
  );
}
