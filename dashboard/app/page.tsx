"use client"

import React, {useEffect, useRef, useState} from 'react'
import Card from '../components/Card/Card';
import CreateGraph from '../components/Modals/CreateGraph/CreateGraph';

const precision = 3;

export default function Home() {
  const [plotGraphModal, setPlotGraphModal] = useState<boolean>(false);

  const handleAddPlot = ()=>setPlotGraphModal(true);

  return (
    <div>
      {plotGraphModal && (
        <div 
        className='bg-black w-full h-full z-[10] fixed top-0 bg-opacity-20 backdrop-blur-sm flex justify-center align-middle'>
          <CreateGraph setPlotGraphModal={setPlotGraphModal} ></CreateGraph>
        </div>
      )}
      <main className="flex justify-start mt-[100px] flex-row items-start flex-wrap" >
        <Card>
          <button className='w-full h-full' onClick={handleAddPlot}>
            <p className='text-black text-opacity-70 text-[100px]'>+</p>
          </button>
        </Card>
      </main>
    </div>
  );
}
