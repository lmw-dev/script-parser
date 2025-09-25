import type { Metadata } from "next"

export const metadata: Metadata = {
  title: "分析结果 | AI 脚本快拆",
}

export default function ResultLayout({ children }: { children: React.ReactNode }) {
  return <>{children}</>
}
