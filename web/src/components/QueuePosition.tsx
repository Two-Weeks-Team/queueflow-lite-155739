"use client";

type Props = {
  position: number;
};

export default function QueuePosition({ position }: Props) {
  return (
    <div className="card">
      <h3 className="text-lg font-medium">Your Current Position</h3>
      <p className="text-4xl font-bold text-primary mt-2">{position}</p>
      <p className="text-sm text-muted mt-1">People ahead of you</p>
    </div>
  );
}
