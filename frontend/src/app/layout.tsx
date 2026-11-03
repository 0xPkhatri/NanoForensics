import type {Metadata} from 'next';
import './globals.css';
export const metadata:Metadata={title:'NanoForensics · Scientific workbench',description:'Auditable counterfactual investigation in a real 2D Lennard-Jones computational testbed.'};
export default function RootLayout({children}:{children:React.ReactNode}){return <html lang="en"><body>{children}</body></html>}
