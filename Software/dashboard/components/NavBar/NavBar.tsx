import React from 'react'
import Image from 'next/image';
import Link from 'next/link';

const navLinkStyle = 'text-xl ml-8 mr-8 p-1 pb-[3px] border-b-[3px] border-transparent hover:border-white duration-150';

export default function NavBar(){
    return (
        <nav className='m-3 p-6 flex flex-row items-center justify-start animate-ttb bg-big-card rounded-md'>
            {/* <Image className='rounded-full p-1 ml-7' src="/Logo.png" alt="Quintuple E" width={72} height={71}></Image> */}
            <h1 className='text-3xl text-nowrap font-bold ml-4 mr-10'>Quintuple E</h1>
            <div className='flex justify-start text-center w-full'>
                <Link className={navLinkStyle} href="/">Live</Link>
                <Link className={navLinkStyle} href="/history">History</Link>
                <Link className={navLinkStyle} href="/control">Control</Link>
            </div>
        </nav>
    );
}