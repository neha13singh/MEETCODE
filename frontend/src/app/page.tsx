"use client";

import { useAuth } from '@/context/AuthContext';
import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Sword, Users, Zap, Trophy, Github, Code2, ArrowRight } from 'lucide-react';
import Navbar from '@/components/Navbar';

export default function Home() {
  const { user, isLoading, setIsLoginModalOpen } = useAuth();
  const router = useRouter();

  if (isLoading) {
    return (
      <div className="min-h-screen bg-zinc-950 flex items-center justify-center text-white">
        <div className="animate-pulse flex flex-col items-center">
          <div className="h-12 w-12 bg-zinc-800 rounded-full mb-4"></div>
          <div className="h-4 w-32 bg-zinc-800 rounded"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-transparent text-foreground selection:bg-primary/30 relative">

      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-primary/10 rounded-full blur-[120px] opacity-40" />
        <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-secondary/10 rounded-full blur-[120px] opacity-30" />
      </div>

      <main className="relative max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 pt-32 pb-12">
        <div className="text-center mb-16 space-y-6">
          <div className="inline-block px-4 py-1.5 rounded-full glass border border-primary/20 text-xs font-bold tracking-widest text-primary glow-text-cyan animate-pulse">
            VERSION 4.0 :: READY
          </div>
          <h1 className="text-6xl md:text-8xl font-black tracking-tighter pb-2 leading-[0.9]">
            CODE. <span className="text-gradient hover:glow-text-cyan transition-all cursor-default">COMPETE.</span> CONQUER.
          </h1>
          <p className="text-lg text-zinc-400 max-w-2xl mx-auto font-medium">
            The best place to practice coding and compete with friends. Simple, fast, and powerful.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-[1400px] mx-auto px-4">
          <div className="group relative h-full">
            <div className="absolute inset-0 bg-primary/20 blur-xl rounded-2xl opacity-0 group-hover:opacity-30 transition-opacity duration-500"></div>
            <Card className="relative h-full flex flex-col p-6 glass-card border-white/5 cyber-shape group-hover:border-primary/40 transition-all duration-500 overflow-hidden">
              <div className="absolute top-0 right-0 w-32 h-32 bg-primary/5 rounded-full -mr-16 -mt-16 blur-3xl group-hover:bg-primary/10 transition-colors"></div>

              <CardHeader className="relative z-10 pb-2 p-0 mb-6">
                <div className="w-14 h-14 flex items-center justify-center bg-primary/10 border border-primary/20 mb-4 cyber-shape shadow-[0_0_15px_rgba(14,165,233,0.1)] group-hover:shadow-[0_0_25px_rgba(14,165,233,0.4)] group-hover:scale-105 transition-all duration-300">
                  <Sword className="w-7 h-7 text-primary group-hover:rotate-12 transition-transform duration-300" />
                </div>
                <CardTitle className="text-3xl font-black tracking-tighter text-white group-hover:text-primary transition-colors uppercase italic">RANDOM BATTLE</CardTitle>
                <CardDescription className="text-primary/70 font-mono text-[10px] font-bold tracking-widest uppercase mt-1">COMPETITIVE MODE</CardDescription>
              </CardHeader>

              <CardContent className="relative z-10 flex-1 flex flex-col space-y-4 p-0">
                <p className="text-zinc-400 text-sm leading-relaxed font-medium">
                  Challenge a random opponent to a real-time coding duel. Rank up, earn badges, and dominate the leaderboard.
                </p>
                <Button
                  onClick={() => {
                    if (!user) setIsLoginModalOpen(true);
                    else router.push('/matchmaking');
                  }}
                  className="mt-auto w-full h-12 cyber-shape bg-zinc-950/50 border border-primary hover:bg-primary/10 hover:shadow-[0_0_20px_rgba(14,165,233,0.4)] text-primary hover:text-white transition-all duration-300 font-bold tracking-widest flex items-center justify-center gap-3 group/btn relative overflow-hidden"
                >
                  <div className="absolute inset-0 bg-primary/10 translate-y-full group-hover/btn:translate-y-0 transition-transform duration-300"></div>
                  <span className="relative">FIND MATCH</span>
                  <Zap className="w-4 h-4 fill-current relative group-hover/btn:scale-110 transition-transform" />
                </Button>
              </CardContent>
            </Card>
          </div>

          <div className="group relative h-full">
            <div className="absolute inset-0 bg-secondary/20 blur-xl rounded-2xl opacity-0 group-hover:opacity-30 transition-opacity duration-500"></div>
            <Card className="relative h-full flex flex-col p-6 glass-card border-white/5 cyber-shape group-hover:border-secondary/40 transition-all duration-500 overflow-hidden">
              <div className="absolute top-0 right-0 w-32 h-32 bg-secondary/5 rounded-full -mr-16 -mt-16 blur-3xl group-hover:bg-secondary/10 transition-colors"></div>

              <CardHeader className="relative z-10 pb-2 p-0 mb-6">
                <div className="w-14 h-14 flex items-center justify-center bg-secondary/10 border border-secondary/20 mb-4 cyber-shape shadow-[0_0_15px_rgba(217,119,6,0.1)] group-hover:shadow-[0_0_25px_rgba(217,119,6,0.4)] group-hover:scale-105 transition-all duration-300">
                  <Code2 className="w-7 h-7 text-secondary group-hover:scale-110 transition-transform duration-300" />
                </div>
                <CardTitle className="text-3xl font-black tracking-tighter text-white group-hover:text-secondary transition-colors uppercase italic">PRACTICE AREA</CardTitle>
                <CardDescription className="text-secondary/70 font-mono text-[10px] font-bold tracking-widest uppercase mt-1">SOLO MODE</CardDescription>
              </CardHeader>

              <CardContent className="relative z-10 flex-1 flex flex-col space-y-4 p-0">
                <p className="text-zinc-400 text-sm leading-relaxed font-medium">
                  Hone your skills in a stress-free environment. Access our full library of problems and track your progress.
                </p>
                <Button
                  onClick={() => {
                    if (!user) setIsLoginModalOpen(true);
                    else router.push('/practice');
                  }}
                  className="mt-auto w-full h-12 cyber-shape bg-zinc-950/50 border border-secondary hover:bg-secondary/10 hover:shadow-[0_0_20px_rgba(217,119,6,0.4)] text-secondary hover:text-white transition-all duration-300 font-bold tracking-widest flex items-center justify-center gap-3 group/btn relative overflow-hidden"
                >
                  <div className="absolute inset-0 bg-secondary/10 translate-y-full group-hover/btn:translate-y-0 transition-transform duration-300"></div>
                  <span className="relative">START PRACTICE</span>
                  <ArrowRight className="w-4 h-4 relative group-hover/btn:translate-x-1 transition-transform" />
                </Button>
              </CardContent>
            </Card>
          </div>

          <div className="group relative h-full">
            <div className="absolute inset-0 bg-purple-500/20 blur-xl rounded-2xl opacity-0 group-hover:opacity-30 transition-opacity duration-500"></div>
            <Card className="relative h-full flex flex-col p-6 glass-card border-white/5 cyber-shape group-hover:border-purple-500/40 transition-all duration-500 overflow-hidden">
              <div className="absolute top-0 right-0 w-32 h-32 bg-purple-500/5 rounded-full -mr-16 -mt-16 blur-3xl group-hover:bg-purple-500/10 transition-colors"></div>

              <CardHeader className="relative z-10 pb-2 p-0 mb-6">
                <div className="w-14 h-14 flex items-center justify-center bg-purple-500/10 border border-purple-500/20 mb-4 cyber-shape shadow-[0_0_15px_rgba(168,85,247,0.1)] group-hover:shadow-[0_0_25px_rgba(168,85,247,0.4)] group-hover:scale-105 transition-all duration-300">
                  <Users className="w-7 h-7 text-purple-500 group-hover:scale-110 transition-transform duration-300" />
                </div>
                <CardTitle className="text-3xl font-black tracking-tighter text-white group-hover:text-purple-500 transition-colors uppercase italic">PLAY FRIENDS</CardTitle>
                <CardDescription className="text-purple-500/70 font-mono text-[10px] font-bold tracking-widest uppercase mt-1">PRIVATE MODE</CardDescription>
              </CardHeader>
              <CardContent className="relative z-10 flex-1 flex flex-col space-y-4 p-0">
                <p className="text-zinc-400 text-sm leading-relaxed font-medium">
                  Create private rooms and invite your friends for a custom match. Prove who is the better coder.
                </p>
                <Button
                  onClick={() => {
                    if (!user) setIsLoginModalOpen(true);
                    else router.push('/matchmaking?mode=private');
                  }}
                  className="mt-auto w-full h-12 cyber-shape bg-zinc-950/50 border border-purple-500 hover:bg-purple-500/10 hover:shadow-[0_0_20px_rgba(168,85,247,0.4)] text-purple-500 hover:text-white transition-all duration-300 font-bold tracking-widest flex items-center justify-center gap-3 group/btn relative overflow-hidden"
                >
                  <div className="absolute inset-0 bg-purple-500/10 translate-y-full group-hover/btn:translate-y-0 transition-transform duration-300"></div>
                  <span className="relative">INVITE FRIEND</span>
                  <Users className="w-4 h-4 relative group-hover/btn:scale-110 transition-transform" />
                </Button>
              </CardContent>
            </Card>
          </div>
        </div>

      </main>
    </div>
  );
}
