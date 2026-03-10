import '@/app/globals.css';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'QueueFlow Lite',
  description: 'Simple, real-time queue management for restaurants.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="bg-background text-foreground antialiased">
      <body>{children}</body>
    </html>
  );
}
