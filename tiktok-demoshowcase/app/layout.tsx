import type { Metadata } from "next";
import "./globals.css";
import UserProvider from "./context/user";
import AllOverlays from "./components/AllOverlays";
import { WebSocketProvider } from "./context/WebSocketContext"

export const metadata: Metadata = {
  title: "TikTok TechJam",
  description: "TikTok TechJam",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <WebSocketProvider>
        <UserProvider>
          <body>
            <AllOverlays />
            {children}
          </body>
        </UserProvider>
      </WebSocketProvider>
    </html>
  );
}
