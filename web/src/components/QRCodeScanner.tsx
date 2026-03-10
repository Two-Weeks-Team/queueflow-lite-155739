"use client";

import { useState } from 'react';
import { CameraIcon } from '@heroicons/react/24/outline';

type Props = {
  onScanned: (queueId: string) => void;
};

export default function QRCodeScanner({ onScanned }: Props) {
  const [scanning, setScanning] = useState(false);

  const simulateScan = () => {
    setScanning(true);
    // Mock a QR scan delay
    setTimeout(() => {
      const mockQueueId = 'demo-queue-1234';
      onScanned(mockQueueId);
      setScanning(false);
    }, 1500);
  };

  return (
    <div className="card flex flex-col items-center space-y-3">
      <h2 className="text-xl font-semibold">Scan QR to Join Queue</h2>
      <button
        onClick={simulateScan}
        disabled={scanning}
        className="flex items-center space-x-2 bg-primary text-white px-4 py-2 rounded-full hover:scale-105 transition-transform"
      >
        <CameraIcon className="h-5 w-5" />
        {scanning ? 'Scanning…' : 'Start Scan'}
      </button>
      <p className="text-sm text-muted">(Demo: click to simulate)</p>
    </div>
  );
}
