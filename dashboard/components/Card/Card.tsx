import React from 'react'

export default function Card({children, className}: {children: React.ReactNode, className: string}){
    return (
        <div className={`rounded-[20px] bg-background shadow-card h-[500px] flex justify-center items-center flex-col m-5 w-[46%] ${className}`}>
        {children}
        </div>
    );
}