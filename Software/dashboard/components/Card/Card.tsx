import React from "react";

export default function Card({
  children,
  className,
}: {
  children: React.ReactNode;
  className: string;
}) {
  return (
    <div
      className={`rounded-[20px] bg-background shadow-card h-[600px] flex justify-center items-center flex-col m-2 w-[98%] ${className}`}
    >
      {children}
    </div>
  );
}
