"use client";

export default function StatsStrip() {
  // Demo static stats – replace with real analytics later
  const stats = [
    { label: 'Current Guests', value: 23 },
    { label: 'Avg Wait', value: '8m' },
    { label: 'Available Seats', value: 12 },
  ];
  return (
    <div className="flex justify-center gap-6 py-4">
      {stats.map((s) => (
        <div key={s.label} className="text-center">
          <p className="text-2xl font-bold text-primary">{s.value}</p>
          <p className="text-sm text-muted">{s.label}</p>
        </div>
      ))}
    </div>
  );
}
