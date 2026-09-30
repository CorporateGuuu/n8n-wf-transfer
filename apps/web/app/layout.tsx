export default function RootLayout({children}:{children:React.ReactNode}) {
  return <html lang="en"><body style={{fontFamily:"system-ui",margin:0,background:"#f6f7f9",color:"#111"}}>{children}</body></html>;
}
