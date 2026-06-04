import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "주식 가치 평가기",
  description: "서준식 ROE 기반 10년 주가 예측 및 매수 추천가 계산",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ko">
      <body className="min-h-screen bg-gray-50 text-gray-900 antialiased">
        {children}
      </body>
    </html>
  );
}
