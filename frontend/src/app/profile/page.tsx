"use client";

import { useEffect, useState } from 'react';
import { useAuth } from '@/context/AuthContext';
import { useRouter } from 'next/navigation';
import Navbar from '@/components/Navbar';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import {
    Trophy,
    Sword,
    Code2,
    Zap,
    Clock,
    CheckCircle2,
    User as UserIcon,
    ArrowRight,
    Search,
    Github,
    History
} from 'lucide-react';
import { questionApi, Question } from '@/lib/api/questions';
import { matchesApi } from '@/lib/api/matches';
import apiClient from '@/lib/api/client';
import { User as UserType } from '@/context/AuthContext';

interface EditProfileModalProps {
    isOpen: boolean;
    onClose: () => void;
    user: UserType | null;
}

function EditProfileModal({ isOpen, onClose, user }: EditProfileModalProps) {
    const [email, setEmail] = useState(user?.email || '');
    const [password, setPassword] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [success, setSuccess] = useState(false);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setError(null);
        setSuccess(false);

        try {
            await apiClient.patch('/users/me', {
                email: email !== user?.email ? email : undefined,
                password: password || undefined
            });
            setSuccess(true);
            setTimeout(() => {
                onClose();
                window.location.reload(); // Refresh to show new data
            }, 1500);
        } catch (err: any) {
            setError(err.response?.data?.detail || "Update failed. Check entries.");
        } finally {
            setLoading(false);
        }
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-4">
            <div className="absolute inset-0 bg-black/80 backdrop-blur-sm" onClick={onClose}></div>
            <Card className="relative w-full max-w-md p-8 glass-card border-primary/20 cyber-shape animate-in zoom-in-95 duration-200">
                <h2 className="text-2xl font-black tracking-tighter text-white mb-6 uppercase italic">EDIT_PROFILE_SECURED</h2>

                <form onSubmit={handleSubmit} className="space-y-6">
                    <div className="space-y-2">
                        <label className="text-[10px] font-black tracking-widest text-zinc-500 uppercase">EMAIL_ADDRESS</label>
                        <input
                            type="email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            className="w-full bg-espresso-mid/50 border border-white/5 rounded-lg p-3 text-zinc-300 font-mono text-xs focus:border-primary/50 focus:glow-cyan outline-none transition-all"
                            placeholder="new_email@address.com"
                        />
                    </div>

                    <div className="space-y-2">
                        <label className="text-[10px] font-black tracking-widest text-zinc-500 uppercase">NEW_PASSWORD</label>
                        <input
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            className="w-full bg-espresso-mid/50 border border-white/5 rounded-lg p-3 text-zinc-300 font-mono text-xs focus:border-primary/50 focus:glow-cyan outline-none transition-all"
                            placeholder="LEAVE_BLANK_TO_KEEP"
                        />
                    </div>

                    {error && (
                        <div className="p-3 bg-destructive/10 border border-destructive/20 text-destructive text-[10px] font-black tracking-widest uppercase cyber-shape">
                            {error}
                        </div>
                    )}

                    {success && (
                        <div className="p-3 bg-primary/10 border border-primary/20 text-primary text-[10px] font-black tracking-widest uppercase cyber-shape glow-cyan">
                            PROFILE_UPDATED_SUCCESSFULLY
                        </div>
                    )}

                    <div className="pt-4 flex space-x-4">
                        <Button type="submit" disabled={loading} className="flex-1 bg-primary hover:bg-primary/80 text-white font-black tracking-widest text-[10px] cyber-shape glow-cyan">
                            {loading ? 'UPLOADING...' : 'SAVE_CHANGES'}
                        </Button>
                        <Button type="button" onClick={onClose} variant="ghost" className="flex-1 border border-white/5 font-black tracking-widest text-[10px] cyber-shape">
                            CANCEL
                        </Button>
                    </div>
                </form>
            </Card>
        </div>
    );
}

export default function ProfilePage() {
    const { user, isLoading: authLoading } = useAuth();
    const router = useRouter();
    const [matchHistory, setMatchHistory] = useState<any[]>([]);
    const [privateMatchHistory, setPrivateMatchHistory] = useState<any[]>([]);
    const [solvedQuestions, setSolvedQuestions] = useState<Question[]>([]);
    const [loading, setLoading] = useState(true);
    const [activeTab, setActiveTab] = useState<'matches' | 'solved'>('matches');
    const [matchType, setMatchType] = useState<'competitive' | 'private'>('competitive');
    const [isEditModalOpen, setIsEditModalOpen] = useState(false);
    const [startingPractice, setStartingPractice] = useState(false);

    useEffect(() => {
        if (!authLoading && !user) {
            router.push('/');
            return;
        }

        async function fetchData() {
            if (!user) return;
            try {
                // Fetch Competitive Matches
                const matchRes = await apiClient.get('/users/me/matches?limit=100&mode=competitive');
                setMatchHistory(matchRes.data);

                // Fetch Private Matches
                const privateRes = await apiClient.get('/users/me/matches?limit=100&mode=private');
                setPrivateMatchHistory(privateRes.data);

                // Fetch Solved Questions (Practice)
                const questRes = await questionApi.getQuestions();
                setSolvedQuestions(questRes.filter(q => q.is_solved));
            } catch (err) {
                console.error("Failed to fetch profile data", err);
            } finally {
                setLoading(false);
            }
        }

        fetchData();
    }, [user, authLoading, router]);

    const handleSolve = async (questionId: string) => {
        setStartingPractice(true);
        try {
            const match = await matchesApi.createMatch({
                mode: 'practice',
                question_id: questionId
            });
            router.push(`/editor/${match.id}`);
        } catch (error) {
            console.error("Failed to start practice match", error);
        } finally {
            setStartingPractice(false);
        }
    };

    if (authLoading || (loading && !matchHistory.length)) {
        return (
            <div className="min-h-screen bg-black flex items-center justify-center">
                <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-primary"></div>
            </div>
        );
    }

    const winCount = matchHistory.filter(m => m.result === 'win').length;
    const winRate = matchHistory.length > 0 ? ((winCount / matchHistory.length) * 100).toFixed(1) : '0';

    return (
        <div className="min-h-screen bg-transparent text-foreground selection:bg-primary/30 relative overflow-x-hidden">

            {/* Background decoration */}
            <div className="fixed inset-0 overflow-hidden pointer-events-none">
                <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-primary/10 rounded-full blur-[120px] opacity-40" />
                <div className="absolute bottom-[-10%] right-[-20%] w-[50%] h-[50%] bg-secondary/10 rounded-full blur-[150px] opacity-30" />
            </div>

            <main className="container max-w-4xl mx-auto px-6 pt-32 pb-20 relative z-10">
                {/* Profile Header */}
                <div className="mb-12 flex flex-col md:flex-row items-center md:items-end gap-8">
                    <div className="relative group">
                        <div className="absolute inset-0 bg-primary/20 blur-xl rounded-full opacity-0 group-hover:opacity-100 transition-opacity duration-700"></div>
                        <div className="w-24 h-24 md:w-32 md:h-32 bg-espresso-mid rounded-3xl border-2 border-primary/30 flex items-center justify-center cyber-shape glow-cyan relative overflow-hidden transition-transform duration-500 hover:scale-105">
                            <UserIcon className="w-12 h-12 md:w-16 md:h-16 text-primary" />
                            <div className="absolute bottom-0 left-0 right-0 h-1/3 bg-gradient-to-t from-primary/20 to-transparent"></div>
                        </div>
                    </div>

                    <div className="flex-1 text-center md:text-left space-y-4">
                        <div className="inline-flex items-center px-4 py-1 rounded-full glass border border-primary/20 text-[10px] font-black tracking-widest text-primary glow-text-cyan">
                            ELITE_DEVELOPER_SECURED
                        </div>
                        <h1 className="text-4xl md:text-5xl font-black tracking-tighter text-white uppercase italic leading-none">
                            {user?.username}
                        </h1>
                        <p className="text-zinc-500 font-mono text-xs tracking-[0.2em] uppercase">
                            MEMBER SINCE :: {new Date().getFullYear()} // STATUS: ACTIVE
                        </p>
                    </div>

                    <div className="flex gap-4">
                        <Button
                            onClick={() => setIsEditModalOpen(true)}
                            className="h-9 px-6 font-black tracking-widest text-[9px] cyber-shape bg-amber-500/10 border border-amber-500/20 text-amber-500 hover:bg-amber-500/20 hover:border-amber-500/50 hover:shadow-[0_0_15px_rgba(245,158,11,0.2)] transition-all"
                        >
                            EDIT_PROFILE
                        </Button>
                    </div>
                </div>

                <EditProfileModal
                    isOpen={isEditModalOpen}
                    onClose={() => setIsEditModalOpen(false)}
                    user={user}
                />

                {/* Stats Grid */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-12">
                    {[
                        { label: 'MATCHES_PLAYED', value: matchHistory.length, icon: Sword, color: 'text-primary' },
                        { label: 'VICTORIES', value: winCount, icon: Trophy, color: 'text-emerald-500' },
                        { label: 'WIN_RATE', value: `${winRate}%`, icon: Zap, color: 'text-secondary' },
                        { label: 'PROBLEMS_SOLVED', value: solvedQuestions.length, icon: Code2, color: 'text-blue-500' },
                    ].map((stat, i) => (
                        <Card key={i} className="p-4 glass-card border-white/5 cyber-shape group hover:border-primary/30 transition-all duration-500">
                            <div className="flex items-start justify-between mb-4">
                                <div className={`w-8 h-8 flex items-center justify-center bg-zinc-900/50 cyber-shape border border-white/5 group-hover:${stat.color} transition-colors`}>
                                    <stat.icon className="w-4 h-4" />
                                </div>
                            </div>
                            <div className="text-2xl font-black text-white mb-1 tracking-tighter">{stat.value}</div>
                            <div className="text-[9px] font-black tracking-widest text-zinc-600 uppercase">{stat.label}</div>
                        </Card>
                    ))}
                </div>

                {/* Tabs */}
                <div className="flex space-x-6 mb-10 border-b border-primary/10 pb-4">
                    <button
                        onClick={() => setActiveTab('matches')}
                        className={`text-xs font-black tracking-widest uppercase transition-all flex items-center space-x-3 ${activeTab === 'matches' ? 'text-primary' : 'text-zinc-500 hover:text-zinc-300'}`}
                    >
                        <History className="w-4 h-4" />
                        <span>MATCH_HISTORY</span>
                        {activeTab === 'matches' && <div className="ml-2 w-1.5 h-1.5 rounded-full bg-primary glow-cyan animate-pulse"></div>}
                    </button>
                    <button
                        onClick={() => setActiveTab('solved')}
                        className={`text-xs font-black tracking-widest uppercase transition-all flex items-center space-x-3 ${activeTab === 'solved' ? 'text-secondary' : 'text-zinc-500 hover:text-zinc-300'}`}
                    >
                        <CheckCircle2 className="w-4 h-4" />
                        <span>SOLVED_CHALLENGES</span>
                        {activeTab === 'solved' && <div className="ml-2 w-1.5 h-1.5 rounded-full bg-secondary shadow-[0_0_10px_var(--secondary)] animate-pulse"></div>}
                    </button>
                </div>

                {/* Tab Content */}
                <div className="min-h-[400px]">
                    {activeTab === 'matches' ? (
                        <div className="animate-in fade-in slide-in-from-bottom-4 duration-500">
                            {/* Match Type Toggle */}
                            <div className="flex space-x-4 mb-6">
                                <button
                                    onClick={() => setMatchType('competitive')}
                                    className={`px-4 py-1.5 rounded-lg text-[10px] font-black tracking-widest uppercase transition-all cyber-shape border ${matchType === 'competitive'
                                        ? 'bg-primary/20 border-primary text-primary glow-cyan'
                                        : 'bg-zinc-900/50 border-white/5 text-zinc-500 hover:text-zinc-300'
                                        }`}
                                >
                                    COMPETITIVE
                                </button>
                                <button
                                    onClick={() => setMatchType('private')}
                                    className={`px-4 py-1.5 rounded-lg text-[10px] font-black tracking-widest uppercase transition-all cyber-shape border ${matchType === 'private'
                                        ? 'bg-purple-500/20 border-purple-500 text-purple-500 shadow-[0_0_10px_rgba(168,85,247,0.3)]'
                                        : 'bg-zinc-900/50 border-white/5 text-zinc-500 hover:text-zinc-300'
                                        }`}
                                >
                                    PRIVATE_LOBBY
                                </button>
                            </div>

                            {/* Render Table based on matchType */}
                            {(matchType === 'competitive' ? matchHistory : privateMatchHistory).length === 0 ? (
                                <div className="py-20 flex flex-col items-center justify-center text-zinc-600 space-y-6 glass-card border-dashed border-white/5 cyber-shape">
                                    <Github className="w-16 h-16 opacity-10" />
                                    <p className="font-mono text-xs tracking-widest uppercase font-bold">
                                        {matchType === 'competitive' ? 'NO COMPETITIVE DATA SECURED' : 'NO PRIVATE MATCHES FOUND'}
                                    </p>
                                    <Button onClick={() => router.push(matchType === 'competitive' ? '/matchmaking' : '/matchmaking?mode=private')} variant="outline" className={`cyber-shape text-[10px] font-black tracking-widest bg-transparent hover:bg-white/5 ${matchType === 'competitive' ? 'border-primary/20 text-primary' : 'border-purple-500/20 text-purple-500'}`}>
                                        {matchType === 'competitive' ? 'INITIALIZE BATTLE' : 'CREATE ROOM'}
                                    </Button>
                                </div>
                            ) : (
                                <div className="overflow-x-auto glass-card border-white/5 cyber-shape">
                                    <table className="w-full text-left">
                                        <thead className={`text-[10px] uppercase font-black tracking-[0.2em] border-b border-white/5 ${matchType === 'competitive' ? 'bg-primary/5 text-primary' : 'bg-purple-500/5 text-purple-500'}`}>
                                            <tr>
                                                <th className="px-8 py-5">Result</th>
                                                <th className="px-8 py-5">Problem</th>
                                                <th className="px-8 py-5">Opponent</th>
                                                <th className="px-8 py-5">Date</th>
                                            </tr>
                                        </thead>
                                        <tbody className="divide-y divide-white/5">
                                            {(matchType === 'competitive' ? matchHistory : privateMatchHistory).map((match) => (
                                                <tr key={match.id} className={`transition-colors group ${matchType === 'competitive' ? 'hover:bg-primary/5' : 'hover:bg-purple-500/5'}`}>
                                                    <td className="px-8 py-6">
                                                        <span className={`inline-flex items-center px-4 py-1 cyber-shape text-[10px] font-black tracking-widest ${match.result === 'win'
                                                            ? (matchType === 'competitive' ? 'bg-primary/10 text-primary border border-primary/20 glow-cyan' : 'bg-purple-500/10 text-purple-500 border border-purple-500/20 shadow-[0_0_10px_rgba(168,85,247,0.3)]')
                                                            : match.result === 'lose'
                                                                ? 'bg-destructive/10 text-destructive border border-destructive/20'
                                                                : match.result === 'timeout'
                                                                    ? 'bg-amber-500/10 text-amber-500 border border-amber-500/20'
                                                                    : 'bg-zinc-800/10 text-zinc-500 border border-zinc-800'
                                                            }`}>
                                                            {match.result === 'win' ? 'WON' : match.result === 'lose' ? 'LOST' : match.result === 'timeout' ? 'TIMEOUT' : 'PLAYING'}
                                                        </span>
                                                    </td>
                                                    <td className="px-8 py-6 text-zinc-200 font-bold tracking-tight">{match.questionTitle}</td>
                                                    <td className="px-8 py-6 text-zinc-500 font-mono text-xs italic">{match.opponent || 'N/A'}</td>
                                                    <td className="px-8 py-6 text-zinc-600 font-mono text-xs uppercase">
                                                        {new Date(match.date).toLocaleDateString()}
                                                    </td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                </div>
                            )}
                        </div>
                    ) : (
                        <div className="grid gap-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
                            {solvedQuestions.length === 0 ? (
                                <div className="py-20 flex flex-col items-center justify-center text-zinc-600 space-y-6 glass-card border-dashed border-white/5 cyber-shape">
                                    <Search className="w-16 h-16 opacity-10" />
                                    <p className="font-mono text-xs tracking-widest uppercase font-bold">NO CHALLENGES CONQUERED YET</p>
                                    <Button onClick={() => router.push('/practice')} variant="outline" className="cyber-shape text-[10px] font-black tracking-widest border-secondary/20 text-secondary hover:bg-secondary/10">
                                        ACCESS ARENA
                                    </Button>
                                </div>
                            ) : (
                                solvedQuestions.map((q) => (
                                    <div key={q.id} className="group relative">
                                        <div className="absolute inset-0 bg-secondary/10 blur-[2px] cyber-shape opacity-0 group-hover:opacity-100 transition-opacity"></div>
                                        <Card className="relative p-6 glass-card border-white/5 group-hover:border-secondary/40 transition-all duration-500 cyber-shape">
                                            <div className="flex items-center justify-between">
                                                <div className="flex items-center space-x-6">
                                                    <div className="w-12 h-12 flex items-center justify-center bg-secondary/10 text-secondary border border-secondary/30 cyber-shape shadow-[0_0_15px_rgba(217,119,6,0.3)]">
                                                        <CheckCircle2 className="w-6 h-6" />
                                                    </div>
                                                    <div>
                                                        <h3 className="text-xl font-black tracking-tight text-white mb-1 group-hover:text-secondary transition-colors uppercase">
                                                            {q.title}
                                                        </h3>
                                                        <div className="flex items-center space-x-4">
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
                                                    disabled={startingPractice}
                                                    variant="ghost"
                                                    className="text-zinc-500 hover:text-secondary transition-all group-hover:translate-x-1"
                                                >
                                                    {startingPractice ? <div className="animate-spin w-4 h-4 border-2 border-secondary border-t-transparent rounded-full" /> : <ArrowRight className="w-5 h-5" />}
                                                </Button>
                                            </div>
                                        </Card>
                                    </div>
                                ))
                            )}
                        </div>
                    )}
                </div>
            </main >
        </div >
    );
}
