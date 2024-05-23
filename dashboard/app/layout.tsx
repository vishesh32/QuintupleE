import type { Metadata } from "next";
import { Inter, Karla } from "next/font/google";
import "./globals.css";

// const inter = Inter({ subsets: ["latin"] });
const karla = Karla({subsets: ["latin"]});

export const metadata: Metadata = {
  title: "Quintuple E",
  description: "Dashboard for the system",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${karla.className} text-secondary`}>
        <h1 className='text-6xl font-medium text-center mt-3'>Quintuple E</h1>
        {children}
      </body>
    </html>
  );
}
