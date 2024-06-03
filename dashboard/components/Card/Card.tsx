import React from 'react'

export default function Card({children}: {children: React.ReactNode}){
    return (
        <div className='rounded-[20px] bg-background shadow-card h-[500px] flex justify-center align-middle flex-col text-center m-5 w-[46%]'>
        {children}
        </div>
    );
}