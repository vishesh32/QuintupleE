import React from 'react'
import Image from 'next/image';
import Link from 'next/link';

const navLinkStyle = 'text-2xl ml-10 mr-10 p-1 pb-[3px] border-b-[3px] border-transparent hover:border-white duration-150';

export default function NavBar(){
    return (
        <div className='flex justify-center animate-ttb'>
            <nav className='ml-10 mr-10 bg-primary rounded-full mt-5 w-full max-w-[1000px] flex items-center min-w-[600px]'>
                <Image className='rounded-full p-1' src="/Logo.png" alt="Quintuple E" width={72} height={71}></Image>
                <div className='flex justify-center text-center w-full'>
                    <Link className={navLinkStyle} href="/">Live</Link>
                    <Link className={navLinkStyle} href="/history">History</Link>
                    <Link className={navLinkStyle} href="/manualcontrol">Manual Control</Link>
                </div>
            </nav>
        </div>
    );
}