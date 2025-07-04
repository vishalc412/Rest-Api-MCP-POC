import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
});

export const metadata: Metadata = {
  title: "WarryWorks Agentic Builder - Premium AI Workflow Platform",
  description: "Professional agentic workflow builder for creating sophisticated AI-powered automation and agent systems",
  keywords: "WarryWorks, agentic, AI agents, workflow, automation, premium, drag-drop, visual programming, artificial intelligence",
  authors: [{ name: "WarryWorks Team" }],
  viewport: "width=device-width, initial-scale=1",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <link rel="icon" href="/logo.png" />
        <link rel="apple-touch-icon" href="/logo.png" />
        <meta name="theme-color" content="#6366f1" />
      </head>
      <body className={`${inter.variable} font-sans antialiased bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-gray-100 overflow-hidden`}>
        <div id="root" className="h-screen w-full">
          {children}
        </div>
      </body>
    </html>
  );
}
