"use client"

import React, {useEffect, useRef, useState} from 'react'
import Card from '../components/Card/Card';
import CreateGraph from '../components/Modals/CreateGraph/CreateGraph';
import Graph from '@/components/Graph/Graph'
import { getTick } from './actions';
import { GraphData } from '@/helpers/graph_data';
import History from './history/page';

export default function Home() {
  return <History />;
}
