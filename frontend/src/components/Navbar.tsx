"use client";

import Link from 'next/link';
import { useAuth } from '@/context/AuthContext';
import { LogOut, User, Code2 } from 'lucide-react';
import { Button } from './ui/button';
import { useState } from 'react';
import LoginModal from './LoginModal';

export default function Navbar() {
  const { user, logout, isLoginModalOpen, setIsLoginModalOpen } = useAuth();
  const [modalView, setModalView] = useState<'login' | 'register'>('login');

  const openLogin = () => {
    setModalView('login');
    setIsLoginModalOpen(true);
  };

  const openRegister = () => {
    setModalView('register');
    setIsLoginModalOpen(true);
  };

  return (
    <nav className="glass border-b border-primary/20 fixed top-0 w-full z-50 shadow-[0_0_20px_rgba(14,165,233,0.15)] backdrop-blur-md">
      <div className="container mx-auto px-6 h-16 flex items-center justify-between">
        <Link href="/" className="flex items-center gap-2 group transition-all hover:scale-105 active:scale-95">
          <div className="p-1.5 bg-primary/10 rounded-lg border border-primary/20 group-hover:border-primary/50 transition-colors cyber-shape glow-cyan">
            <Code2 className="w-5 h-5 text-primary" />
          </div>
          <div className="text-2xl font-black tracking-tighter italic flex gap-0.5">
            <span className="text-transparent bg-clip-text bg-gradient-to-br from-white to-zinc-500 drop-shadow-sm">MEET</span>
            <span className="text-gradient">CODE</span>
          </div>
        </Link>
        <div className="flex items-center gap-3">
          {user ? (
            <div className="flex items-center gap-3 ml-2">
              <Link href="/profile" className="flex items-center gap-3 pl-2 pr-6 py-2 rounded-xl bg-white/5 border border-white/20 hover:bg-white/10 hover:border-white/50 hover:shadow-[0_0_20px_rgba(255,255,255,0.3)] transition-all group active:scale-95 duration-300 cyber-shape">
                <div className="w-8 h-8 rounded-lg bg-white/10 flex items-center justify-center group-hover:scale-110 transition-transform border border-white/10">
                  <User className="w-4 h-4 text-white" />
                </div>
                <span className="text-xs font-black tracking-widest uppercase text-white hidden md:block transition-colors">
                  {user.username}
                </span>
              </Link>
              <button
                onClick={logout}
                className="w-12 h-12 rounded-xl bg-zinc-900/50 border border-white/10 flex items-center justify-center text-zinc-400 hover:text-destructive hover:border-destructive/50 hover:bg-destructive/10 transition-all active:scale-95 cyber-shape"
                title="Sign Out"
              >
                <LogOut className="w-5 h-5" />
              </button>
            </div>
          ) : (
            <div className="flex items-center gap-4">
              <button
                onClick={openLogin}
                className="px-6 py-2 rounded-xl bg-transparent border border-primary/30 text-primary hover:bg-primary/10 hover:border-primary hover:shadow-[0_0_15px_rgba(14,165,233,0.3)] transition-all text-[10px] font-black tracking-[0.2em] uppercase active:scale-95 duration-300 cyber-shape"
              >
                SIGN IN
              </button>
              <Button
                onClick={openRegister}
                size="sm"
                className="rounded-xl bg-primary hover:bg-primary/90 text-zinc-950 border-0 font-black tracking-[0.2em] text-[10px] px-8 h-10 shadow-[0_0_20px_rgba(14,165,233,0.4)] hover:shadow-[0_0_30px_rgba(14,165,233,0.6)] hover:scale-105 transition-all active:scale-95 duration-300 cyber-shape glow-cyan"
              >
                SIGN UP
              </Button>
            </div>
          )}
        </div>
      </div>

      <LoginModal
        isOpen={isLoginModalOpen}
        onCloseAction={() => setIsLoginModalOpen(false)}
        initialView={modalView}
      />
    </nav>
  );
}
