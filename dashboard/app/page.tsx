"use client"

import React, {useEffect, useRef, useState} from 'react'
import { getSimData } from './actions';
import { SimData, emptySimData } from '@/helpers/sim_data';

const precision = 3;

export default function Home() {
  const [simData, setSimData] = useState<SimData>(emptySimData);
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
    // fetchData();
  }, [])


  return (
    <main className="flex justify-center mt-[100px] flex-col items-center	" >
    </main>
  );
}
