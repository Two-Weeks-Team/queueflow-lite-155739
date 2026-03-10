"use client";

type Props = {
  queueId: string | null;
};

// Placeholder recent activity – in real app this would call an endpoint
const mockHistory = [
  { id: '1', name: 'Table for 2', position: 3, wait: 5 },
  { id: '2', name: 'Table for 4', position: 7, wait: 12 },
];

export default function CollectionPanel({ queueId }: Props) {
  if (!queueId) {
    return (
      <div className="card">
        <p className="text-muted">Scan a QR code to see recent queue activity.</p>
      </div>
    );
  }

  return (
    <div className="card">
      <h3 className="text-lg font-medium mb-2">Recent Queue Activity</h3>
      <ul className="space-y-2">
        {mockHistory.map((item) => (
          <li key={item.id} className="flex justify-between text-sm">
            <span>{item.name}</span>
            <span>{item.position} • {item.wait}m</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
