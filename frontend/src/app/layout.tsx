import React from 'react'
import './globals.css'

export const metadata = {
  title: 'Resume Builder - AI-Powered Resume Assistant',
  description: 'Build and improve your resume with AI assistance',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className="antialiased">
        {children}
      </body>
    </html>
  )
}