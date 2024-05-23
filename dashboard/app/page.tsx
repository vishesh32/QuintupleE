"use client"

import React, {useEffect, useRef, useState} from 'react'
import InfoBox from '../components/InfoBox/InfoBox';
import { SimData, getSimData } from './actions';

export default function Home() {
  const [simData, setSimData] = useState<SimData>({
    day: 0,
    tick: 0,
    buyPrice: 0,
    sellPrice: 0,
    demand: 0,
    sun: 0,
    deferables: []
  });
  const timeoutId = useRef<string>("");

  const fetchData = async ()=>{
    const data = await getSimData();
    // console.log(data);
    setSimData(data)
    const tID = setTimeout(()=>{
      console.log("refresh")
      fetchData()
      clearTimeout(timeoutId.current)
    }, 500);

    timeoutId.current = tID.toString();
  };

  useEffect(()=>{
    fetchData();
    // .then(()=>{
    //   setTimeout(()=>{
    //     console.log("refresh")
    //     fetchData()
    //   }, 500)
    // })
  }, [])


  return (
    <main className="flex justify-center mt-[100px] flex-col items-center	" >
      <h3 className="text-3xl text-center">
        Day: {simData.day}
        <br />
        <br />
        Tick: {simData.tick}
      </h3>

      <InfoBox classes="mt-[100px]">
        <p className='text-xl'>
          Buy Price: {simData.buyPrice}
          <br /><br />
          Sell Price: {simData.sellPrice}
          <br /><br />
          Demand: {simData.demand}
          <br /><br />
          Sun: {simData.sun}%
        </p>
      </InfoBox>

      <h3 className="text-3xl text-center mt-[80px]">Deferrable Demand</h3>

      <div className='flex flex-row items-center justify-center mt-[30px] flex-wrap'>
        {simData.deferables.map(({end, energy, start}, i)=>{
          return (
            <InfoBox classes="ml-10 mt-10" key={i}>
              <p>
                Start: {start}
                <br /><br />
                End: {end}
                <br /><br />
                Demand: {energy}
              </p>
            </InfoBox>
          )
        })}
      </div>

    </main>
  );
}
