"use client";

import { useEffect, useState, useRef, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { useAuth } from '@/context/AuthContext';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Zap, Shield, Swords, Loader2, X } from 'lucide-react';
import Navbar from '@/components/Navbar';
import LoginModal from '@/components/LoginModal';

function MatchmakingPageContent() {
  const { user, isLoading: authLoading, setIsLoginModalOpen } = useAuth();
  const router = useRouter();
  const searchParams = useSearchParams();
  const [status, setStatus] = useState<'idle' | 'searching' | 'found'>('idle');
  const [difficulty, setDifficulty] = useState<'easy' | 'medium' | 'hard'>('medium');
  const [timeLeft, setTimeLeft] = useState(60);
  const socketRef = useRef<WebSocket | null>(null);
  const [mode, setMode] = useState<'public' | 'private_menu' | 'private_create' | 'private_join'>('public');
  const [privateCode, setPrivateCode] = useState('');
  const [createdCode, setCreatedCode] = useState('');
  const [joinCode, setJoinCode] = useState('');
  const [errorMsg, setErrorMsg] = useState('');

  useEffect(() => {
    if (searchParams.get('mode') === 'private') {
      setMode('private_menu');
    }
  }, [searchParams]);

  useEffect(() => {
    // No longer redirecting immediately
  }, [user, authLoading, router]);

  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (status === 'searching' && timeLeft > 0) {
      interval = setInterval(() => {
        setTimeLeft((prev) => prev - 1);
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [status, timeLeft]);

  useEffect(() => {
    // Cleanup on unmount
    return () => {
      if (socketRef.current) {
        socketRef.current.close();
      }
    };
  }, []);

  const connectToWebSocket = () => {
    const token = localStorage.getItem('token');
    if (!token) return;

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = process.env.NEXT_PUBLIC_API_URL
      ? new URL(process.env.NEXT_PUBLIC_API_URL).host
      : 'localhost:8000';
    const wsUrl = `${protocol}//${host}/ws?token=${token}`;
    console.log('Connecting to WebSocket:', wsUrl);
    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      console.log('Connected to WebSocket');

      if (mode === 'public') {
        ws.send(JSON.stringify({
          event: 'queue:join',
          data: { difficulty }
        }));
        setStatus('searching');
        setTimeLeft(60);
      } else if (mode === 'private_create') {
        ws.send(JSON.stringify({
          event: 'match:create_private',
          data: { difficulty }
        }));
        // Status will be updated when we get the code
      } else if (mode === 'private_join') {
        ws.send(JSON.stringify({
          event: 'match:join_private',
          data: { code: joinCode }
        }));
        setStatus('searching'); // Show searching/joining UI
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      setStatus('idle');
      setErrorMsg('Connection failed');
    };

    ws.onmessage = (event) => {
      const message = JSON.parse(event.data);

      if (message.event === 'match:found') {
        setStatus('found');
        const { matchId, startTime } = message.data;
        setTimeout(() => {
          router.push(`/editor/${matchId}?startTime=${startTime}`);
        }, 1500);
      } else if (message.event === 'match:practice') {
        const { practiceId } = message.data;
        router.push(`/editor/${practiceId}?mode=practice`);
      } else if (message.event === 'match:private_created') {
        setCreatedCode(message.data.code);
        setStatus('searching'); // waiting for friend
      } else if (message.event === 'match:error') {
        setStatus('idle');
        setErrorMsg(message.data.message);
      }
    };

    ws.onclose = () => {
      console.log('Disconnected');
      if (status === 'searching') {
        setStatus('idle');
      }
    };

    socketRef.current = ws;
  };

  const cancelSearch = () => {
    if (socketRef.current) {
      if (status === 'searching' && mode === 'public') {
        socketRef.current.send(JSON.stringify({
          event: 'queue:leave',
          data: { difficulty }
        }));
      }
      socketRef.current.close();
      setStatus('idle');
      setCreatedCode('');
      setMode(searchParams.get('mode') === 'private' ? 'private_menu' : 'public');
      setErrorMsg('');
    }
  };

  if (authLoading || !user) {
    return (
      <div className="min-h-screen bg-zinc-950 flex items-center justify-center text-white">
        <Loader2 className="w-8 h-8 animate-spin text-blue-500" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-transparent text-foreground flex flex-col items-center justify-center p-4 relative overflow-hidden selection:bg-primary/30">

      {/* Background decoration */}
      <div className="absolute top-[-20%] left-[-10%] w-[50%] h-[50%] bg-primary/10 rounded-full blur-[150px] opacity-40" />
      <div className="absolute bottom-[-20%] right-[-10%] w-[50%] h-[50%] bg-secondary/10 rounded-full blur-[150px] opacity-30" />

      <Card className="w-[90%] md:w-full max-w-md glass-card border-primary/10 relative z-10 p-6 md:p-8 cyber-shape shadow-2xl shadow-primary/5">
        <button
          onClick={() => router.push('/')}
          className="absolute top-4 right-4 p-2 text-zinc-500 hover:text-white transition-colors hover:rotate-90 duration-300"
        >
          <X className="w-5 h-5" />
        </button>
        <div className="text-center mb-6">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-espresso-mid mb-6 cyber-shape border border-primary/30 glow-cyan transition-transform hover:scale-110 duration-500">
            <Swords className="w-8 h-8 text-primary" />
          </div>
          <h2 className="text-3xl font-black tracking-tighter mb-2 italic">FIND A MATCH</h2>
          <p className="text-zinc-500 font-medium font-mono text-[10px] tracking-widest uppercase">
            {mode === 'public' ? 'RANKED MATCHMAKING' : mode === 'private_menu' ? 'SELECT MODE' : mode === 'private_create' ? 'CREATE ROOM' : 'JOIN ROOM'}
          </p>
        </div>

        {status === 'idle' && mode === 'private_menu' && (
          <div className="space-y-4 animate-in fade-in slide-in-from-bottom-6 duration-700">
            <Button
              onClick={() => setMode('private_create')}
              className="w-full h-16 text-sm font-black tracking-[0.2em] uppercase bg-primary hover:bg-primary/90 text-white shadow-lg shadow-primary/20 transition-all border-0 cyber-shape glow-cyan"
            >
              CREATE ROOM
            </Button>
            <Button
              onClick={() => setMode('private_join')}
              className="w-full h-16 text-sm font-black tracking-[0.2em] uppercase bg-espresso-mid hover:bg-espresso-light border border-primary/20 hover:border-primary/50 text-white shadow-lg transition-all cyber-shape"
            >
              JOIN ROOM
            </Button>
            <Button
              variant="ghost"
              onClick={() => router.push('/')}
              className="w-full text-[10px] text-zinc-500 hover:text-zinc-300 mt-4"
            >
              BACK TO MENU
            </Button>
          </div>
        )}

        {status === 'idle' && mode === 'public' && (
          <div className="space-y-6 animate-in fade-in slide-in-from-bottom-6 duration-700">
            <div className="grid grid-cols-3 gap-3">
              {(['easy', 'medium', 'hard'] as const).map((level) => (
                <button
                  key={level}
                  onClick={() => setDifficulty(level)}
                  className={`relative group p-4 rounded-xl border transition-all duration-500 cyber-shape ${difficulty === level
                    ? 'bg-primary/10 border-primary/50 text-white shadow-primary/20 shadow-lg glow-cyan'
                    : 'bg-espresso-mid border-white/5 text-zinc-500 hover:bg-espresso-light hover:border-white/10'
                    }`}
                >
                  <div className={`text-[9px] font-black uppercase tracking-widest mb-2 ${difficulty === level ? 'text-primary' : 'text-zinc-600'}`}>
                    {level}
                  </div>
                  <div className="flex justify-center space-x-1">
                    {[...Array(level === 'easy' ? 1 : level === 'medium' ? 2 : 3)].map((_, i) => (
                      <div key={i} className={`w-1.5 h-1.5 rounded-full transition-all ${difficulty === level ? 'bg-primary shadow-[0_0_8px_var(--primary)]' : 'bg-zinc-800'}`} />
                    ))}
                  </div>
                </button>
              ))}
            </div>

            <Button
              onClick={() => {
                if (!user) setIsLoginModalOpen(true);
                else connectToWebSocket();
              }}
              className="w-full h-12 text-xs font-black tracking-[0.3em] uppercase bg-primary hover:bg-primary/90 text-white shadow-2xl shadow-primary/30 transition-all hover:scale-105 active:scale-95 border-0 cyber-shape glow-cyan"
            >
              START SEARCHING
              <Zap className="w-4 h-4 ml-4 fill-current" />
            </Button>
          </div>
        )}

        {status === 'idle' && mode === 'private_create' && (
          <div className="space-y-6 animate-in fade-in slide-in-from-bottom-6 duration-700">
            <div className="text-center p-4 bg-espresso-mid border border-white/5 cyber-shape rounded-xl">
              <p className="text-zinc-400 text-xs mb-4">Select difficulty for your private match</p>
              <div className="grid grid-cols-3 gap-2 mb-4">
                {(['easy', 'medium', 'hard'] as const).map((level) => (
                  <button
                    key={level}
                    onClick={() => setDifficulty(level)}
                    className={`p-2 rounded border text-[10px] uppercase font-bold transition-all ${difficulty === level
                      ? 'bg-primary/20 border-primary text-primary'
                      : 'bg-black/20 border-white/5 text-zinc-600 hover:bg-white/5'
                      }`}
                  >
                    {level}
                  </button>
                ))}
              </div>
            </div>
            <Button
              onClick={connectToWebSocket}
              className="w-full h-12 text-xs font-black tracking-[0.3em] uppercase bg-primary hover:bg-primary/90 text-white shadow-2xl shadow-primary/30 transition-all border-0 cyber-shape glow-cyan"
            >
              GENERATE CODE
            </Button>
            <Button
              variant="ghost"
              onClick={() => searchParams.get('mode') === 'private' ? setMode('private_menu') : setMode('public')}
              className="w-full text-[10px] text-zinc-500 hover:text-zinc-300"
            >
              BACK TO MENU
            </Button>
          </div>
        )}

        {status === 'idle' && mode === 'private_join' && (
          <div className="space-y-6 animate-in fade-in slide-in-from-bottom-6 duration-700">
            <div className="text-center">
              <input
                type="text"
                value={joinCode}
                onChange={(e) => setJoinCode(e.target.value.toUpperCase().replace(/\s/g, ''))}
                placeholder="ENTER CODE"
                maxLength={6}
                className="w-full bg-espresso-mid border border-primary/20 rounded-xl p-4 text-center text-2xl font-black tracking-[0.2em] text-primary focus:outline-none focus:border-primary/50 transition-all placeholder:text-zinc-700 font-mono mb-2"
              />
              {errorMsg && <p className="text-destructive text-xs font-bold mt-2 animate-pulse">{errorMsg}</p>}
            </div>
            <Button
              onClick={connectToWebSocket}
              disabled={joinCode.length < 6}
              className="w-full h-12 text-xs font-black tracking-[0.3em] uppercase bg-primary hover:bg-primary/90 text-white shadow-2xl shadow-primary/30 transition-all disabled:opacity-50 disabled:cursor-not-allowed border-0 cyber-shape glow-cyan"
            >
              JOIN ROOM
            </Button>
            <Button
              variant="ghost"
              onClick={() => {
                if (searchParams.get('mode') === 'private') setMode('private_menu');
                else setMode('public');
                setErrorMsg('');
              }}
              className="w-full text-[10px] text-zinc-500 hover:text-zinc-300"
            >
              BACK TO MENU
            </Button>
          </div>
        )}

        {status === 'searching' && (
          <div className="py-0 animate-in fade-in zoom-in duration-500">

            {mode === 'private_create' && createdCode ? (
              <>
                <div className="relative w-32 h-32 mx-auto mb-6 flex items-center justify-center">
                  <div className="absolute inset-0 bg-primary/20 rounded-full animate-ping opacity-20" style={{ animationDuration: '3s' }}></div>
                  <div className="w-24 h-24 bg-espresso-dark rounded-full border border-primary/30 flex items-center justify-center relative shadow-[0_0_40px_-5px_var(--primary)]">
                    <span className="text-3xl font-black font-mono text-primary italic glow-text-cyan">{createdCode}</span>
                  </div>
                </div>
                <div className="text-center space-y-2 mb-6">
                  <h3 className="text-xl font-bold tracking-tighter text-white">
                    WAITING FOR FRIEND...
                  </h3>
                  <p className="text-zinc-500 text-[10px] uppercase tracking-widest">Share this code with your friend</p>
                </div>
              </>
            ) : (
              <>
                <div className="relative w-24 h-24 mx-auto mb-4">
                  {/* Radar Waves */}
                  <div className="absolute inset-0 bg-primary/20 rounded-full animate-ping opacity-20" style={{ animationDuration: '3s' }}></div>
                  <div className="absolute inset-0 bg-primary/20 rounded-full animate-ping opacity-20 delay-1000" style={{ animationDuration: '3s' }}></div>

                  {/* Center Icon */}
                  <div className="absolute inset-0 flex items-center justify-center">
                    <div className="w-16 h-16 bg-espresso-dark rounded-full border border-primary/30 flex items-center justify-center relative shadow-[0_0_40px_-5px_var(--primary)]">
                      {mode === 'public' ? (
                        <span className="text-2xl font-black font-mono text-primary italic glow-text-cyan">{timeLeft}</span>
                      ) : (
                        <Loader2 className="w-8 h-8 text-primary animate-spin" />
                      )}
                    </div>
                  </div>
                </div>

                <div className="text-center space-y-2">
                  <h3 className="text-3xl font-black tracking-tighter text-gradient animate-pulse italic">
                    {mode === 'private_join' ? 'JOINING...' : 'SEARCHING...'}
                  </h3>
                  <div className="flex flex-col items-center space-y-3">
                    {mode !== 'private_join' && (
                      <p className="text-zinc-500 text-xs font-mono tracking-widest uppercase">
                        DIFFICULTY :: <span className="text-white font-black">{difficulty}</span>
                      </p>
                    )}
                    <div className="w-32 h-1 bg-white/5 rounded-full overflow-hidden">
                      <div className="h-full bg-primary animate-[shimmer_2s_infinite] w-full"></div>
                    </div>
                  </div>
                </div>
              </>
            )}

            <div className="mt-5 flex justify-center">
              <Button
                onClick={cancelSearch}
                className="bg-destructive/10 hover:bg-destructive/20 text-destructive border border-destructive/20 hover:border-destructive/50 h-10 px-8 font-black tracking-widest text-[10px] cyber-shape transition-all"
              >
                <X className="w-4 h-4 mr-2" />
                CANCEL
              </Button>
            </div>
          </div>
        )}

        {status === 'found' && (
          <div className="py-14 animate-in fade-in zoom-in duration-700 text-center">
            <div className="w-28 h-28 mx-auto mb-10 bg-primary/10 rounded-full flex items-center justify-center border border-primary/30 shadow-[0_0_50px_-10px_var(--primary)] cyber-shape glow-cyan">
              <Shield className="w-14 h-14 text-primary" />
            </div>
            <h3 className="text-4xl font-black text-white mb-4 tracking-tighter italic glow-text-cyan">MATCH_FOUND!</h3>
            <p className="text-zinc-500 font-mono text-[10px] tracking-widest uppercase">PREPARING YOUR MATCH...</p>
            <div className="mt-10 flex justify-center space-x-2">
              <div className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
              <div className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
              <div className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
            </div>
          </div>
        )}
      </Card>
    </div>
  );
}

export default function MatchmakingPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-zinc-950 flex items-center justify-center text-white">
        <Loader2 className="w-8 h-8 animate-spin text-blue-500" />
      </div>
    }>
      <MatchmakingPageContent />
    </Suspense>
  );
}
