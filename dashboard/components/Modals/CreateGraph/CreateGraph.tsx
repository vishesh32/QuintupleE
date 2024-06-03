import React from 'react'
import { XMarkIcon } from '@heroicons/react/24/outline';

const sample = [
    "Tick Cost (Cents)",
    "Sun Intensity (%)",
    "Demand (Watts)"
]

export default function CreateGraph({setPlotGraphModal} : any){

    const handleClose = ()=>{
        setPlotGraphModal(false);
    }

    return (
        <div className='text-black bg-background flex flex-col text-center w-[50%] h-[40%] mt-[25%] rounded-2xl p-10'>
            <div className='flex flex-row justify-end'>
                <button onClick={handleClose}>
                    <XMarkIcon className='size-7'></XMarkIcon>
                </button>
            </div>
            <h2 className='text-4xl font-bold'>Plot A Graph</h2>
            <div className='flex flex-col justify-center items-center w-full h-full'>
                <select className='w-[250px] p-2.5 text-xl text-center rounded-xl shadow-md border-[#001E1D] border-[2px]' name="" id="" defaultValue="default">
                    <option value="default" disabled>Select a Variable</option>
                    {sample.map((val)=><option key={val}>{val}</option>)}
                </select>
                <br />
                <br />
                <button className='bg-[#001E1D] text-white text-xl p-2.5 w-[130px] rounded-xl hover:mt-[-3px] hover:mb-[3px] duration-[0.2s]'>Plot</button>
            </div>
        </div>
    );
}