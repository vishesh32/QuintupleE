import React from "react";

export default function SmallCard({
  children,
  className,
}: {
  children: React.ReactNode;
  className: string;
}) {
  return (
    <div
      className={`rounded-md bg-small-card p-8 m-3 ${className}`}
    >
      {children}
    </div>
  );
}
