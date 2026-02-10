"use client";

import { usePathname } from 'next/navigation';
import Navbar from './Navbar';

export default function MainLayout({ children }: { children: React.ReactNode }) {
    const pathname = usePathname();
    const isEditor = pathname?.startsWith('/editor');

    return (
        <>
            {!isEditor && <Navbar />}
            <main className={`min-h-screen relative z-0 ${isEditor ? '' : 'pt-16'}`}>
                {children}
            </main>
        </>
    );
}
