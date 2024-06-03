import React from 'react'
import Image from 'next/image';
import Link from 'next/link';

const navLinkStyle = 'text-2xl p-4 pl-7 pr-7 hover:underline hover:underline-offset-[13px] duration-200';

export default function NavBar(){
    return (
        <div className='flex justify-center'>
            <nav className='ml-10 mr-10 bg-primary rounded-full mt-8 w-full max-w-[800px] flex align-middle min-w-[600px]'>
                <Image className='rounded-full p-1' src="/Logo.png" alt="Quintuple E" width={72} height={71}></Image>
                <div className='flex align-middle justify-center text-center w-full'>
                    <Link className={navLinkStyle} href="/">Live</Link>
                    <Link className={navLinkStyle} href="/history">History</Link>
                    <Link className={navLinkStyle} href="/manualcontrol">Manual Control</Link>
                </div>
            </nav>
        </div>
    );
}