import React from 'react'
import Image from 'next/image';
import Link from 'next/link';

const navLinkStyle = 'text-xl ml-8 mr-8 p-1 pb-[3px] border-b-[3px] border-transparent hover:border-white duration-150';

export default function NavBar(){
    return (
        <nav className='p-6 flex flex-row items-center justify-start animate-ttb border-b-[1px]'>
            {/* <Image className='rounded-full p-1 ml-7' src="/Logo.png" alt="Quintuple E" width={72} height={71}></Image> */}
            <h1 className='text-3xl text-nowrap font-bold ml-4 mr-10'>Quintuple E</h1>
            <div className='flex justify-start text-center w-full'>
                <Link className={navLinkStyle} href="/history">Historical</Link>
                <Link className={navLinkStyle} href="/management">Management</Link>
                <Link className={navLinkStyle} href="/controls">Controls</Link>
                <Link className={navLinkStyle} href="/settings">Settings</Link>
            </div>
        </nav>
    );
}