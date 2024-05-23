import React from 'react'

export default function InfoBox({children, classes} : {children: React.ReactNode, classes: string}){
    return (
        <div className={'bg-primary w-[350px] h-fit p-12 rounded-[35px] justify-center shadow-info-box ' + classes}>
            {children}
        </div>
    );
}