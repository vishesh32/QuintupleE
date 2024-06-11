import React from "react";

export default function BigCard({
  children,
  className,
}: {
  children: React.ReactNode;
  className: string;
}) {
  return (
    <div
      className={`rounded-md bg-big-card p-8 m-3 ${className}`}
    >
      {children}
    </div>
  );
}
