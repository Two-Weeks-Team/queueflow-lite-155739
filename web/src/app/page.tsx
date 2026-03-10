"use client";

import { useState, useEffect, useCallback } from 'react';
import Hero from '@/components/Hero';
import QRCodeScanner from '@/components/QRCodeScanner';
import QueuePosition from '@/components/QueuePosition';
import InsightPanel from '@/components/InsightPanel';
import StatePanel from '@/components/StatePanel';
import CollectionPanel from '@/components/CollectionPanel';
import StatsStrip from '@/components/StatsStrip';
import { fetchQueuePosition, fetchWaitTime } from '@/lib/api';

export default function HomePage() {
  const [queueId, setQueueId] = useState<string | null>(null);
  const [position, setPosition] = useState<number | null>(null);
  const [waitTime, setWaitTime] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // After we have a queueId, join the queue and start polling
  const startQueueFlow = useCallback(async (id: string) => {
    setLoading(true);
    setError(null);
    try {
      // Simulate join by fetching initial position & wait time
      const joinRes = await fetchQueuePosition(id, {
        name: 'Guest',
        party_size: 2,
        contact_info: { phone: '5551234567' },
      });
      setPosition(joinRes.queue_position);
      setWaitTime(joinRes.estimated_wait_time);
      // Poll every 5 seconds for updates
      const interval = setInterval(async () => {
        try {
          const pos = await fetchQueuePosition(id);
          setPosition(pos.current_position);
          setWaitTime(pos.estimated_wait_time);
        } catch (e) {
          console.error(e);
        }
      }, 5000);
      // cleanup on unmount or queue change
      return () => clearInterval(interval);
    } catch (e: any) {
      setError(e.message ?? 'Unexpected error');
    } finally {
      setLoading(false);
    }
  }, []);

  // React to QR code scan result
  useEffect(() => {
    if (queueId) {
      startQueueFlow(queueId);
    }
  }, [queueId, startQueueFlow]);

  return (
    <div className="flex flex-col min-h-screen p-4 space-y-6">
      <Hero />
      <StatsStrip />
      <div className="grid md:grid-cols-2 gap-6">
        <section className="flex flex-col space-y-4">
          <QRCodeScanner onScanned={setQueueId} />
          {loading && <StatePanel state="loading" />}
          {error && <StatePanel state="error" message={error} />}
          {position !== null && waitTime !== null && (
            <>
              <QueuePosition position={position} />
              <InsightPanel waitTime={waitTime} />
            </>
          )}
        </section>
        <section className="flex flex-col space-y-4">
          <CollectionPanel queueId={queueId} />
        </section>
      </div>
    </div>
  );
}
