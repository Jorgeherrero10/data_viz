'use client';

import dynamic from 'next/dynamic';
import { ComponentType } from 'react';

// Dynamically import Plotly to avoid SSR issues
const Plot: ComponentType<any> = dynamic(
  () => import('react-plotly.js'),
  { 
    ssr: false,
    loading: () => (
      <div className="loading">
        <div className="spinner"></div>
      </div>
    )
  }
);

export default Plot;
