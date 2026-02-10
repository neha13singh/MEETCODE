"use client";

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { questionApi, Question } from '@/lib/api/questions';
import { matchesApi } from '@/lib/api/matches';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card } from '@/components/ui/card';
import { CheckCircle2, Circle, ArrowRight, Code2 } from 'lucide-react';
import Navbar from '@/components/Navbar';
import LoginModal from '@/components/LoginModal';
import { useAuth } from '@/context/AuthContext';

export default function PracticePage() {
  const { user, setIsLoginModalOpen } = useAuth();
  const router = useRouter();
  const [questions, setQuestions] = useState<Question[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadQuestions() {
      try {
        const data = await questionApi.getQuestions();
        setQuestions(data);
      } catch (error) {
        console.error("Failed to load questions", error);
      } finally {
        setLoading(false);
      }
    }
    loadQuestions();
  }, []);

  const handleSolve = async (questionId: string) => {
    if (!user) {
      setIsLoginModalOpen(true);
      return;
    }
    try {
      const match = await matchesApi.createMatch({
        mode: 'practice',
        question_id: questionId
      });
      router.push(`/editor/${match.id}`);
    } catch (error) {
      console.error("Failed to start practice match", error);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-black text-white flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-emerald-500"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-transparent text-foreground selection:bg-primary/30 relative">

      {/* Background decoration */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-[-10%] right-[-10%] w-[40%] h-[40%] bg-primary/10 rounded-full blur-[120px] opacity-40" />
      </div>

      <main className="container max-w-4xl mx-auto px-6 pt-32 pb-12 relative">
        <div className="mb-12 space-y-4">
          <h1 className="text-4xl font-black tracking-tighter text-gradient italic leading-none">
            PRACTICE_ARENA
          </h1>
          <p className="text-zinc-500 text-sm max-w-2xl font-medium tracking-tight">
            Master coding challenges and improve your problem-solving skills at your own pace.
          </p>
        </div>

        <div className="grid gap-4">
          {questions.map((q) => (
            <div key={q.id} className="group relative">
              <div className="absolute inset-0 bg-primary/10 blur-[2px] cyber-shape opacity-0 group-hover:opacity-100 transition-opacity"></div>
              <Card className="relative p-5 glass-card border-white/5 group-hover:border-primary/40 transition-all duration-500 cyber-shape">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    <div className={`w-10 h-10 flex items-center justify-center cyber-shape border transition-all ${q.is_solved ? 'bg-primary/10 text-primary border-primary/30 glow-cyan' : 'bg-espresso-mid text-zinc-600 border-white/5'}`}>
                      {q.is_solved ? <CheckCircle2 className="w-5 h-5" /> : <Code2 className="w-5 h-5" />}
                    </div>
                    <div>
                      <h3 className="text-lg font-black tracking-tight text-white mb-2 group-hover:text-primary transition-colors uppercase">
                        {q.title}
                      </h3>
                      <div className="flex items-center space-x-3">
                        <div className={`px-3 py-0.5 text-[9px] font-black tracking-widest uppercase cyber-shape border ${q.difficulty === 'easy' ? 'text-primary border-primary/20 bg-primary/5' :
                          q.difficulty === 'medium' ? 'text-secondary border-secondary/20 bg-secondary/5' :
                            'text-destructive border-destructive/20 bg-destructive/5'
                          }`}>
                          {q.difficulty}
                        </div>
                        <span className="text-zinc-600 font-mono text-[9px] uppercase font-bold tracking-widest">
                          EST. TIME :: {q.avg_solve_time ? `${Math.floor(q.avg_solve_time / 60)}M` : '15M'}
                        </span>
                      </div>
                    </div>
                  </div>

                  <Button
                    onClick={() => handleSolve(q.id)}
                    className={`
                                        h-9 px-4 font-black tracking-widest text-[9px] cyber-shape uppercase transition-all duration-500
                                        ${q.is_solved
                        ? 'bg-espresso-light hover:bg-espresso-mid text-zinc-400 border border-white/5'
                        : 'bg-primary hover:bg-primary/80 text-white border-0 shadow-lg shadow-primary/20 glow-cyan'}
                                    `}
                  >
                    {q.is_solved ? 'SOLVE AGAIN' : 'START SOLVING'}
                    <ArrowRight className="w-3 h-3 ml-2" />
                  </Button>
                </div>
              </Card>
            </div>
          ))}
        </div>
      </main>

    </div>
  );
}
