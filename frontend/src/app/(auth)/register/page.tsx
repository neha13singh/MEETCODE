"use client";

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import apiClient from '@/lib/api/client';
import { Button } from '@/components/ui/button';
import Link from 'next/link';
import { Zap, UserPlus, X } from 'lucide-react';

export default function RegisterPage() {
  const router = useRouter();
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      await apiClient.post('/users/register', {
        username,
        email,
        password
      });
      router.push('/login');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Registration failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background text-foreground flex items-center justify-center p-4 relative overflow-hidden selection:bg-primary/30">
      <Link href="/" className="absolute top-10 left-10 z-50 p-2 text-zinc-500 hover:text-white transition-all hover:scale-110 active:scale-95">
        <X className="w-8 h-8" />
      </Link>

      {/* Background decoration */}
      <div className="absolute top-[-20%] right-[-10%] w-[50%] h-[50%] bg-primary/10 rounded-full blur-[150px] opacity-40" />
      <div className="absolute bottom-[-20%] left-[-10%] w-[50%] h-[50%] bg-secondary/10 rounded-full blur-[150px] opacity-30" />

      <div className="w-full max-w-md glass-card p-10 border border-primary/10 relative z-10 animate-in fade-in zoom-in duration-700 cyber-shape shadow-2xl shadow-primary/5">
        <div className="text-center mb-10">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-espresso-mid mb-6 cyber-shape border border-primary/30 glow-cyan">
            <UserPlus className="w-8 h-8 text-primary" />
          </div>
          <h2 className="text-4xl font-black tracking-tighter italic mb-3">SIGN_UP</h2>
          <p className="text-zinc-500 font-mono text-[10px] tracking-widest uppercase font-bold">CREATE YOUR ACCOUNT TO JOIN</p>
        </div>

        <form className="space-y-8" onSubmit={handleSubmit}>
          {error && (
            <div className="p-4 bg-destructive/10 border border-destructive/20 text-destructive text-[10px] font-black tracking-widest uppercase cyber-shape text-center animate-in slide-in-from-top-2">
              FAILURE :: {error}
            </div>
          )}

          <div className="space-y-6">
            <div className="space-y-2">
              <label className="text-[10px] font-black tracking-[0.2em] text-zinc-500 uppercase ml-2">USERNAME</label>
              <input
                type="text"
                required
                className="w-full h-12 px-6 bg-espresso-dark border border-white/5 rounded-none text-white placeholder:text-zinc-700 focus:outline-none focus:border-primary/50 focus:glow-cyan transition-all cyber-shape font-mono text-sm"
                placeholder="USERNAME"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <label className="text-[10px] font-black tracking-[0.2em] text-zinc-500 uppercase ml-2">EMAIL ADDRESS</label>
              <input
                type="email"
                required
                className="w-full h-12 px-6 bg-espresso-dark border border-white/5 rounded-none text-white placeholder:text-zinc-700 focus:outline-none focus:border-primary/50 focus:glow-cyan transition-all cyber-shape font-mono text-sm"
                placeholder="EMAIL_ADDRESS"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <label className="text-[10px] font-black tracking-[0.2em] text-zinc-500 uppercase ml-2">PASSWORD</label>
              <input
                type="password"
                required
                className="w-full h-12 px-6 bg-espresso-dark border border-white/5 rounded-none text-white placeholder:text-zinc-700 focus:outline-none focus:border-primary/50 focus:glow-cyan transition-all cyber-shape font-mono text-sm"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>
          </div>

          <Button
            type="submit"
            disabled={loading}
            className="w-full h-14 bg-primary hover:bg-primary/90 text-white font-black tracking-[0.3em] text-[10px] uppercase cyber-shape border-0 shadow-xl shadow-primary/20 glow-cyan transition-all hover:scale-[1.02] active:scale-[0.98]"
          >
            {loading ? (
              <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
            ) : (
              'SIGN_UP'
            )}
          </Button>

          <div className="text-center">
            <Link href="/login" className="text-[10px] font-black tracking-widest text-zinc-600 hover:text-primary transition-colors uppercase">
              ALREADY_HAVE_AN_ACCOUNT?_SIGN_IN
            </Link>
          </div>
        </form>
      </div>
    </div>
  );
}
