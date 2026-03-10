"use client";

type Props = {
  state: 'loading' | 'error' | 'empty' | 'success';
  message?: string;
};

export default function StatePanel({ state, message }: Props) {
  const variants = {
    loading: {
      icon: '⏳',
      text: 'Loading…',
    },
    error: {
      icon: '❗',
      text: message || 'Something went wrong.',
    },
    empty: {
      icon: '🧐',
      text: message || 'No data yet.',
    },
    success: {
      icon: '✅',
      text: message || 'All set!',
    },
  }[state];

  return (
    <div className="card flex items-center space-x-3">
      <span className="text-2xl">{variants.icon}</span>
      <span>{variants.text}</span>
    </div>
  );
}
