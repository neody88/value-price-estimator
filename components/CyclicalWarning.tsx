"use client";

interface Props {
  warning: string;
}

export default function CyclicalWarning({ warning }: Props) {
  return (
    <div className="rounded-lg border border-red-300 bg-red-50 p-4">
      <div className="flex items-start gap-3">
        <span className="text-2xl" aria-hidden>⚠️</span>
        <div>
          <p className="font-semibold text-red-800">경기민감주 경고</p>
          <p className="mt-1 text-sm text-red-700">{warning}</p>
        </div>
      </div>
    </div>
  );
}
