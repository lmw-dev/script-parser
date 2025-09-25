import type { Metadata } from "next"

export const metadata: Metadata = {
  title: "正在处理... | AI 脚本快拆",
}

export default function ProcessingLayout({ children }: { children: React.ReactNode }) {
  return <>{children}</>
}
