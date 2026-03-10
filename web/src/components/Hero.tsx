"use client";

import { Inter } from 'next/font/google';
import { Roboto } from 'next/font/google';

const headline = Inter({ subsets: ['latin'], weight: ['700'], variable: '--font-headline' });
const body = Roboto({ subsets: ['latin'], weight: ['400', '500'], variable: '--font-body' });

export default function Hero() {
  return (
    <section className={`${headline.variable} ${body.variable} text-center py-12`}>
      <h1 className="text-5xl font-bold text-primary mb-4">
        QueueFlow Lite
      </h1>
      <p className="text-xl text-foreground max-w-xl mx-auto">
        Simple, real‑time queue management for restaurants. Scan, join, and watch your place update instantly.
      </p>
    </section>
  );
}
