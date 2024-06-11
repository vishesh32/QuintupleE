"use client"

import React, {useEffect, useRef, useState} from 'react'
import Card from '../components/Card/Card';
import CreateGraph from '../components/Modals/CreateGraph/CreateGraph';
import Graph from '@/components/Graph/Graph'
import { getTick } from './actions';
import { GraphData } from '@/helpers/graph_data';
import History from './history/page';
import { MQTTClient } from '@/helpers/mqtt_client';
import BigCard from '@/components/Card/BigCard';

export default function Home() {
  return (
    <BigCard className="">
      <div className='w-full h-full'>
        div
      </div>
    </BigCard>
  )
}
