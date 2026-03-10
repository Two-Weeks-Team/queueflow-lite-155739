"use client";

type Props = {
  waitTime: number;
};

export default function InsightPanel({ waitTime }: Props) {
  return (
    <div className="card">
      <h3 className="text-lg font-medium">Estimated Wait Time</h3>
      <p className="text-3xl font-semibold text-accent mt-2">
        {waitTime} minute{waitTime !== 1 ? 's' : ''}
      </p>
    </div>
  );
}
