import React from 'react';
import { FormatString } from '@/helpers/graph_types';

export default function Connect({data}: any) {
    return (
        <div className='text-primary inline-block px-10'>
            <p>{FormatString(data.name)}</p>
            <p>{data.lastHeard} | {Date.now()}</p>
        </div>
    );
}