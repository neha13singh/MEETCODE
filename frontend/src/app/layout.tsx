import { AuthProvider } from '@/context/AuthContext';
import { Inter } from 'next/font/google';
import '../globals.css';
import MainLayout from '@/components/MainLayout';
import { logger } from '@/lib/logger';
import { Toaster } from 'react-hot-toast';

const inter = Inter({ subsets: ['latin'] });

export const metadata = {
  title: 'MeetCode',
  description: 'Real-time competitive coding platform',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  logger.info("Application Root Layout Intercepted - Logger Active");
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.className} suppressHydrationWarning={true}>
        <AuthProvider>
          <Toaster position="top-center" toastOptions={{
            style: {
              background: '#333',
              color: '#fff',
            },
          }} />
          <MainLayout>
            {children}
          </MainLayout>
        </AuthProvider>
      </body>
    </html>
  );
}
