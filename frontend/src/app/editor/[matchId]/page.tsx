"use client";

import { useEffect, useState, useRef, Suspense } from 'react';
import { createPortal } from 'react-dom';
import { useParams, useSearchParams, useRouter } from 'next/navigation';
import { Editor } from '@monaco-editor/react';
import { Button } from '@/components/ui/button';
import { useAuth } from '@/context/AuthContext';
import { Play, Send, FileCode, Clock, CheckCircle2, Terminal, Timer as TimerIcon, ArrowLeft, Trophy, Zap, Loader2 } from 'lucide-react';
import { Card } from '@/components/ui/card';
import { questionApi, Question } from '@/lib/api/questions';
import { submissionApi } from '@/lib/api/submissions';
import { matchesApi } from '@/lib/api/matches';
import SubmissionsList from '@/components/SubmissionsList';
import TestCasesList from '@/components/TestCasesList';
import { toast } from 'react-hot-toast';

function EditorPageContent() {
    const router = useRouter();
    const { matchId } = useParams();
    const searchParams = useSearchParams();
    const { user } = useAuth();
    const [code, setCode] = useState('// Write your solution here\n');
    const [language, setLanguage] = useState('python');
    const [output, setOutput] = useState('');
    const [activeTab, setActiveTab] = useState<'problem' | 'submissions' | 'test-cases'>('problem');
    const [timeEncoded, setTimeEncoded] = useState<string>('00:00');
    const [question, setQuestion] = useState<Question | null>(null);
    const [loading, setLoading] = useState(true);
    const [running, setRunning] = useState(false);
    const [matchMode, setMatchMode] = useState<string>('competitive');
    const [maxTime, setMaxTime] = useState<number>(0);
    const [startedAt, setStartedAt] = useState<number>(0);

    const [showResultModal, setShowResultModal] = useState(false);
    const [showSurrenderModal, setShowSurrenderModal] = useState(false);
    const [matchResult, setMatchResult] = useState<{ result: 'win' | 'lose' } | null>(null);

    const socketRef = useRef<WebSocket | null>(null);

    // Timer Logic
    useEffect(() => {
        // If we don't have start time yet, try param or wait
        let start = startedAt;
        if (!start) {
            const startTimeParam = searchParams.get('startTime');
            if (startTimeParam) start = parseInt(startTimeParam);
        }

        if (!start || matchResult) return;

        const interval = setInterval(() => {
            const now = Date.now();

            if ((matchMode === 'competitive' || matchMode === 'private') && maxTime > 0) {
                // Countdown
                const elapsed = now - start;
                const remaining = (maxTime * 1000) - elapsed;

                if (remaining <= 0) {
                    setTimeEncoded("00:00");
                    clearInterval(interval);

                    // Handle Timeout
                    if (!matchResult) {
                        toast.error("Time's Up! Match Ended.", {
                            icon: '⏰',
                            style: {
                                background: '#EF4444',
                                color: '#fff',
                            }
                        });

                        // Helper to trigger timeout logic safely
                        const triggerTimeout = async () => {
                            try {
                                const id = Array.isArray(matchId) ? matchId[0] : matchId;
                                if (typeof id === 'string') await matchesApi.timeout(id);
                            } catch (err) {
                                console.error("Timeout API failed", err);
                            }
                            setTimeout(() => router.push('/'), 3000);
                        };
                        triggerTimeout();
                    }
                    return;
                }

                const minutes = Math.floor(remaining / 60000);
                const seconds = Math.floor((remaining % 60000) / 1000);
                setTimeEncoded(`${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`);
            } else {
                // Stopwatch (Practice)
                let diff = now - start;
                if (diff < 0) diff = 0;
                const minutes = Math.floor(diff / 60000);
                const seconds = Math.floor((diff % 60000) / 1000);
                setTimeEncoded(`${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`);
            }
        }, 1000);

        return () => clearInterval(interval);
    }, [matchId, searchParams, startedAt, maxTime, matchMode, matchResult, router]);

    // Fetch Match & Question
    useEffect(() => {
        async function loadMatchData() {
            if (!matchId) return;
            try {
                const id = Array.isArray(matchId) ? matchId[0] : matchId;

                // Skip if practice mode with hardcoded slug (optional fallback)
                // But for now, we assume even practice created a match record

                const match = await matchesApi.getMatch(id);
                if (match) {
                    if (match.mode) setMatchMode(match.mode);
                    if (match.max_time) setMaxTime(match.max_time);

                    // Phase 6: Handle already completed matches
                    if (match.status === 'completed') {
                        const winnerIdStr = match.winner_id ? String(match.winner_id) : null;
                        const userIdStr = user?.id ? String(user.id) : null;

                        // We check both because user might not be loaded yet, 
                        // so we also handle it in the websocket message just in case
                        if (userIdStr) {
                            const isWin = winnerIdStr === userIdStr;
                            setMatchResult({ result: isWin ? 'win' : 'lose' });
                            setShowResultModal(true);

                            setTimeout(() => {
                                window.location.href = '/';
                            }, 5000);
                        }
                    }

                    // Use server-provided timestamp if available, otherwise parse string
                    if (typeof match.started_at_ts === 'number') {
                        console.log("Using server timestamp:", match.started_at_ts);
                        setStartedAt(match.started_at_ts);
                    } else if (match.started_at) {
                        console.log("DEBUG: match.started_at RAW:", match.started_at);
                        setStartedAt(new Date(match.started_at).getTime());
                    } else if (!startedAt) {
                        setStartedAt(Date.now()); // Fallback
                    }

                    if (match.question) {
                        setQuestion(match.question);

                        // Set template if available
                        if (match.question.templates && match.question.templates.length > 0) {
                            const tmpl = match.question.templates.find((t: any) => t.language === language);
                            if (tmpl) setCode(tmpl.starter_code);
                        }
                    } else {
                        setOutput('Match not found or no question assigned.');
                    }
                }
            } catch (error) {
                console.error("Failed to load match data", error);
                setOutput('Error loading match data. Please try again.');
            } finally {
                setLoading(false);
            }
        }
        loadMatchData();
    }, [matchId]);


    useEffect(() => {
        // Connect to WebSocket
        const token = localStorage.getItem('token');
        if (!token || !matchId) return;

        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const host = process.env.NEXT_PUBLIC_API_URL
            ? new URL(process.env.NEXT_PUBLIC_API_URL).host
            : 'localhost:8000';
        const wsUrl = `${protocol}//${host}/ws?token=${token}`;
        const ws = new WebSocket(wsUrl);

        ws.onopen = () => {
            console.log('Connected to Game WebSocket');
            ws.send(JSON.stringify({
                event: 'match:join',
                data: { matchId: Array.isArray(matchId) ? matchId[0] : matchId }
            }));
        };

        ws.onmessage = (event) => {
            const message = JSON.parse(event.data);
            console.log('Editor Received:', message);

            if (message.event === 'match:completed') {
                const data = message.data;
                const isWinner = data.winnerId && user?.id ? String(data.winnerId) === String(user.id) : false;

                if (matchMode === 'practice') {
                    if (isWinner) {
                        toast.success("Congratulations! Problem Solved 🎉", {
                            duration: 5000,
                            position: 'top-center',
                            style: {
                                background: '#10B981',
                                color: '#fff',
                                fontSize: '16px',
                                fontWeight: 'bold',
                            }
                        });
                    }
                    // Do not redirect or show modal in practice mode
                    return;
                }

                // Competitive Mode Logic
                const resultText = isWinner ? "YOU WON!" : "YOU LOST";
                const resultColor = isWinner ? "text-emerald-500" : "text-red-500";

                setShowResultModal(true);
                setMatchResult({ result: isWinner ? 'win' : 'lose' });

                setTimeout(() => {
                    window.location.href = '/';
                }, 5000);
            }
        };

        socketRef.current = ws;

        return () => {
            ws.close();
        };
    }, [matchId, user, matchMode]);

    // Handle Browser Navigation/Close
    useEffect(() => {
        // 1. Unload/Refresh Protection
        const handleBeforeUnload = (e: BeforeUnloadEvent) => {
            if ((matchMode === 'competitive' || matchMode === 'private') && !matchResult) {
                e.preventDefault();
                e.returnValue = '';
            }
        };

        const handleUnload = () => {
            if ((matchMode === 'competitive' || matchMode === 'private') && !matchResult) {
                // Best effort surrender
                const token = localStorage.getItem('token');
                const id = typeof matchId === 'string' ? matchId : (Array.isArray(matchId) ? matchId[0] : '');
                if (token && id) {
                    fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'}/matches/${id}/surrender`, {
                        method: 'POST',
                        headers: {
                            'Authorization': `Bearer ${token}`
                        },
                        keepalive: true
                    });
                }
            }
        };

        window.addEventListener('beforeunload', handleBeforeUnload);
        window.addEventListener('unload', handleUnload);

        // 2. Back Button Interception (History API)
        const handlePopState = (event: PopStateEvent) => {
            if ((matchMode === 'competitive' || matchMode === 'private') && !matchResult) {
                // Prevent navigation by pushing state back
                window.history.pushState(null, '', window.location.href);
                setShowSurrenderModal(true);
            }
        };

        if ((matchMode === 'competitive' || matchMode === 'private') && !matchResult) {
            // Push dummy state to allow interception
            window.history.pushState(null, '', window.location.href);
            window.addEventListener('popstate', handlePopState);
        }

        return () => {
            window.removeEventListener('beforeunload', handleBeforeUnload);
            window.removeEventListener('unload', handleUnload);
            window.removeEventListener('popstate', handlePopState);
        };
    }, [matchMode, matchResult, matchId]);

    const handleBackClick = () => {
        if ((matchMode === 'competitive' || matchMode === 'private') && !matchResult) {
            setShowSurrenderModal(true);
        } else {
            router.push('/practice');
        }
    };

    const handleConfirmSurrender = async () => {
        try {
            const id = Array.isArray(matchId) ? matchId[0] : matchId;
            if (typeof id === 'string') await matchesApi.surrender(id);
            // The websocket will send 'match:completed', which handles the rest (modal + redirect)
            setShowSurrenderModal(false);
        } catch (error) {
            console.error("Surrender failed", error);
            toast.error("Failed to surrender. Please try again.");
        }
    };

    const handleRun = async () => {
        if (!question) return;
        setRunning(true);
        setOutput('Running test cases...');

        try {
            const result = await submissionApi.runCode({
                code,
                language,
                question_id: question.id,
                match_id: Array.isArray(matchId) ? matchId[0] : matchId
            });

            let outputStr = "";
            if (result.error_message) {
                outputStr += `Error: ${result.error_message}\n`;
            }

            outputStr += `Status: ${result.status}\n`;
            outputStr += `Passed: ${result.test_cases_passed}/${result.total_test_cases}\n\n`;

            result.details.forEach((res: any, idx: number) => {
                outputStr += `Test Case ${idx + 1}: ${res.passed ? 'PASSED' : 'FAILED'}\n`;
                if (!res.passed) {
                    if (res.error) outputStr += `  Error: ${res.error}\n`;
                    outputStr += `  Expected: ${res.expected}\n`;
                    outputStr += `  Actual:   ${res.output}\n`;
                }
                outputStr += `  Time: ${typeof res.execution_time === 'number' ? res.execution_time.toFixed(2) : res.execution_time}ms\n\n`;
            });

            setOutput(outputStr);

        } catch (error: any) {
            setOutput(`Execution failed: ${error.response?.data?.detail || error.message}`);
        } finally {
            setRunning(false);
        }
    };

    const handleSubmit = async () => {
        if (!question) return;

        setOutput('Submitting...');
        try {
            const result = await submissionApi.submitCode({
                code,
                language,
                question_id: question.id,
                match_id: Array.isArray(matchId) ? matchId[0] : matchId
            });

            let outputStr = `Submission Result: ${result.status.toUpperCase()}\n`;
            outputStr += `Passed: ${result.test_cases_passed}/${result.total_test_cases}\n`;
            if (result.status === 'accepted') {
                outputStr += "\nAll test cases passed!";
                if (matchMode === 'practice') {
                    setMatchResult({ result: 'win' });
                    toast.success("Problem Solved! Timer Stopped 🎉");
                } else {
                    outputStr += " Checking match status...";
                }
            } else {
                outputStr += "\nSome test cases failed. Try again.";
            }
            setOutput(outputStr);
        } catch (error: any) {
            setOutput(`Submission failed: ${error.response?.data?.detail || error.message}`);
        }
    };

    if (loading) {
        return <div className="flex items-center justify-center h-screen bg-black text-white">Loading...</div>;
    }

    if (!question) {
        return <div className="flex items-center justify-center h-screen bg-black text-white">Question not found. Please seed the database.</div>;
    }

    return (
        <div className="flex h-[calc(100vh-4rem)] bg-background text-foreground overflow-hidden font-sans relative">

            {/* Result Modal */}
            {showResultModal && matchResult && typeof document !== 'undefined' && createPortal(
                <div className="fixed inset-0 z-[9999] overflow-y-auto bg-black/50 backdrop-blur-md animate-in fade-in duration-500">
                    <div className="min-h-full flex justify-center items-start pt-32 pb-12 p-4">
                        <div className="relative w-[90%] md:w-full max-w-md mx-auto">
                            {/* Floating Icon - Outside the clipped card */}
                            <div className="absolute -top-10 left-1/2 -translate-x-1/2 w-20 h-20 bg-espresso-mid border-2 border-primary/50 flex items-center justify-center cyber-shape glow-cyan shadow-[0_0_30px_rgba(14,165,233,0.3)] z-20">
                                <Trophy className={`w-10 h-10 ${matchResult.result === 'win' ? 'text-primary' : 'text-zinc-500'}`} />
                            </div>

                            {/* Main Card Content - Clipped */}
                            <div className="glass-card p-8 md:p-10 rounded-3xl shadow-2xl text-center border-primary/20 cyber-shape relative z-10 pt-14">
                                <h2 className={`text-4xl md:text-5xl font-black mb-4 tracking-tighter ${matchResult.result === 'win' ? 'text-gradient glow-text-cyan' : 'text-zinc-600'}`}>
                                    {matchResult.result === 'win' ? 'VICTORY' : 'DEFEAT'}
                                </h2>
                                <p className="text-zinc-400 text-lg font-medium mb-8 tracking-tight">
                                    {matchResult.result === 'win'
                                        ? "Success! You earned +25 points."
                                        : "Better luck next time. You lost 15 points."}
                                </p>
                                <div className="w-full h-1 bg-white/5 rounded-full overflow-hidden">
                                    <div className="h-full bg-primary animate-[shimmer_2s_infinite] w-full"></div>
                                </div>
                                <p className="text-zinc-600 text-[10px] mt-6 font-mono tracking-widest uppercase animate-pulse">
                                    Returning to dashboard...
                                </p>
                            </div>
                        </div>
                    </div>
                </div>,
                document.body
            )}

            {/* Surrender Confirmation Modal */}
            {showSurrenderModal && typeof document !== 'undefined' && createPortal(
                <div className="fixed inset-0 z-[9999] overflow-y-auto bg-black/50 backdrop-blur-md animate-in fade-in duration-300">
                    <div className="min-h-full flex items-center justify-center p-4">
                        <div className="glass-card p-8 rounded-2xl shadow-2xl w-[90%] md:w-full max-w-sm text-center border-destructive/20 cyber-shape relative">
                            <h2 className="text-3xl font-black text-white mb-6 tracking-tighter italic">QUIT MATCH?</h2>
                            <p className="text-zinc-400 mb-8 leading-relaxed font-medium text-sm">
                                Are you sure you want to leave? This will be counted as a loss.
                            </p>
                            <div className="flex justify-center space-x-4">
                                <Button
                                    variant="ghost"
                                    onClick={() => setShowSurrenderModal(false)}
                                    className="h-10 px-6 bg-zinc-800 hover:bg-zinc-700 text-white font-bold tracking-tighter cyber-shape border-0 text-xs"
                                >
                                    STAY
                                </Button>
                                <Button
                                    variant="destructive"
                                    onClick={handleConfirmSurrender}
                                    className="h-10 px-6 bg-destructive hover:bg-destructive/80 text-white font-bold tracking-tighter cyber-shape border-0 glow-cyan text-xs"
                                >
                                    QUIT
                                </Button>
                            </div>
                        </div>
                    </div>
                </div>,
                document.body
            )}

            {/* Left Panel: Problem Description */}
            <div className="w-1/2 flex flex-col border-r border-primary/5 glass">
                {/* Header */}
                <div className="h-16 border-b border-primary/10 flex items-center px-6 bg-espresso-mid/50">
                    <button
                        onClick={handleBackClick}
                        className="mr-6 w-10 h-10 flex items-center justify-center bg-zinc-800/50 rounded-lg hover:bg-primary/20 hover:text-primary transition-all cyber-shape border border-white/5"
                        title={matchMode === 'competitive' ? "Quit Battle" : "Go to Practice Home"}
                    >
                        <ArrowLeft className="w-5 h-5" />
                    </button>
                    <div className="flex space-x-4">
                        {[
                            { id: 'problem', label: 'PROBLEM', icon: FileCode },
                            { id: 'submissions', label: 'HISTORY', icon: Clock, hide: matchMode === 'competitive' || matchMode === 'private' },
                            { id: 'test-cases', label: 'TESTING', icon: CheckCircle2 }
                        ].filter(t => !t.hide).map((tab) => (
                            <button
                                key={tab.id}
                                onClick={() => setActiveTab(tab.id as any)}
                                className={`group flex items-center space-x-2 px-4 py-1.5 rounded-lg text-[10px] font-black tracking-[0.2em] transition-all cyber-shape ${activeTab === tab.id
                                    ? 'bg-primary/10 text-primary border border-primary/20 glow-cyan'
                                    : 'text-zinc-500 hover:bg-white/5 border border-transparent'
                                    }`}
                            >
                                <tab.icon className={`w-3 h-3 ${activeTab === tab.id ? 'text-primary' : 'text-zinc-600 group-hover:text-zinc-400'}`} />
                                <span>{tab.label}</span>
                            </button>
                        ))}
                    </div>
                </div>

                {/* Content */}
                <div className="flex-1 overflow-y-auto p-6 custom-scrollbar">
                    {activeTab === 'problem' ? (
                        <div className="animate-in fade-in slide-in-from-bottom-4 duration-500">
                            <div className="flex items-start justify-between mb-6">
                                <h1 className="text-2xl font-black tracking-tighter text-gradient leading-tight">{question.title}</h1>
                                <div className="px-3 py-1 bg-primary/10 border border-primary/20 rounded-lg cyber-shape flex items-center space-x-2 glow-cyan">
                                    <div className="w-1.5 h-1.5 rounded-full bg-primary animate-pulse"></div>
                                    <span className="text-[9px] font-black tracking-widest text-primary uppercase">
                                        {question.difficulty}
                                    </span>
                                </div>
                            </div>

                            <div className="prose prose-invert max-w-none prose-p:text-zinc-400 prose-headings:text-white prose-strong:text-primary leading-relaxed">
                                <p className="text-base text-zinc-300 font-medium mb-8 uppercase tracking-tight">{question.description}</p>
                            </div>
                        </div>
                    ) : activeTab === 'submissions' ? (
                        <SubmissionsList questionId={question.id} />
                    ) : (
                        <TestCasesList testCases={question.test_cases || []} />
                    )}
                </div>
            </div>

            {/* Right Panel: Editor & Console */}
            <div className="w-1/2 flex flex-col bg-espresso-dark/50">
                {/* Editor Header */}
                <div className="h-14 border-b border-primary/10 flex items-center justify-between px-4 bg-espresso-mid/50">
                    <div className="flex items-center space-x-4">
                        <div className="flex items-center space-x-2 px-3 py-1 rounded-lg bg-espresso-light border border-white/5 cyber-shape shadow-lg">
                            <div className="w-1.5 h-1.5 rounded-full bg-blue-400 shadow-[0_0_8px_rgba(96,165,250,0.5)]"></div>
                            <span className="text-[9px] text-zinc-300 font-black tracking-widest uppercase">{language === 'python' ? 'PYTHON 3.11' : language === 'java' ? 'JAVA 17' : 'C++ 17'}</span>
                        </div>

                        {/* Timer Display */}
                        <div className="flex items-center space-x-2 px-3 py-1 rounded-lg bg-primary/5 border border-primary/20 text-primary cyber-shape glow-cyan">
                            <TimerIcon className="w-3 h-3 animate-pulse" />
                            <span className="text-xs font-black font-mono tabular-nums tracking-tighter italic">{timeEncoded}</span>
                        </div>

                        <div className="flex items-center ml-2 border-l border-white/10 pl-4">
                            <select
                                value={language}
                                onChange={(e) => {
                                    const newLang = e.target.value;
                                    setLanguage(newLang);
                                    if (question?.templates) {
                                        const tmpl = question.templates.find((t: any) => t.language === newLang);
                                        if (tmpl) setCode(tmpl.starter_code);
                                    }
                                }}
                                className="bg-espresso-mid hover:bg-espresso-light text-zinc-300 text-[9px] font-black border border-white/10 rounded-lg px-3 py-1 outline-none transition-all cursor-pointer focus:border-primary focus:glow-cyan cyber-shape tracking-widest uppercase"
                            >
                                <option value="python">PYTHON</option>
                                <option value="java">JAVA</option>
                                <option value="cpp">C++</option>
                            </select>
                        </div>
                    </div>

                    <div className="flex items-center space-x-3">
                        <Button
                            onClick={handleRun}
                            disabled={running}
                            variant="ghost"
                            size="sm"
                            className="h-9 px-4 text-zinc-400 hover:text-white hover:bg-white/5 font-black tracking-[0.2em] text-[9px] cyber-shape"
                        >
                            <Play className={`w-3 h-3 mr-2 fill-current ${running ? 'animate-pulse' : ''}`} />
                            {running ? 'RUNNING...' : 'RUN'}
                        </Button>
                        <Button
                            onClick={handleSubmit}
                            disabled={running}
                            size="sm"
                            className="h-9 px-6 bg-primary hover:bg-primary/80 text-white font-black tracking-[0.2em] text-[9px] cyber-shape border-0 shadow-lg shadow-primary/20 glow-cyan transition-all hover:scale-105 active:scale-95"
                        >
                            <Send className="w-3 h-3 mr-2" />
                            SUBMIT
                        </Button>
                    </div>
                </div>

                {/* Editor Area */}
                <div className="flex-grow relative border-b border-primary/5">
                    <Editor
                        height="100%"
                        language={language === 'python' ? 'python' : language === 'java' ? 'java' : 'cpp'}
                        theme="vs-dark"
                        value={code}
                        onChange={(val) => setCode(val || '')}
                        options={{
                            minimap: { enabled: false },
                            fontSize: 16,
                            fontFamily: 'var(--font-mono)',
                            lineHeight: 28,
                            padding: { top: 32 },
                            scrollBeyondLastLine: false,
                            smoothScrolling: true,
                            cursorBlinking: "smooth",
                            cursorSmoothCaretAnimation: "on",
                            roundedSelection: true,
                        }}
                    />
                </div>

                {/* Console/Output */}
                <div className="h-1/3 bg-espresso-mid/80 backdrop-blur-3xl flex flex-col">
                    <div className="h-12 flex items-center justify-between px-6 border-b border-white/5 bg-white/5">
                        <div className="flex items-center space-x-3 text-primary">
                            <Terminal className="w-4 h-4" />
                            <span className="text-[10px] font-black uppercase tracking-[0.3em]">CONSOLE</span>
                        </div>
                        <button
                            onClick={() => setOutput('')}
                            className="text-[10px] text-zinc-600 hover:text-zinc-300 transition-colors uppercase font-black tracking-widest"
                        >
                            CLEAR
                        </button>
                    </div>
                    <div className="flex-1 p-5 font-mono text-sm text-zinc-400 overflow-y-auto whitespace-pre-wrap custom-scrollbar">
                        {output ? (
                            <div className="animate-in fade-in slide-in-from-left-4 duration-300 bg-black/30 p-4 border-l-2 border-primary/50 text-zinc-300">
                                {output}
                            </div>
                        ) : (
                            <div className="flex flex-col items-center justify-center h-full opacity-20 filter grayscale">
                                <Zap className="w-12 h-12 mb-4 animate-pulse" />
                                <span className="text-xs font-mono tracking-widest">RUN YOUR CODE TO SEE OUTPUT</span>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}

export default function EditorPage() {
    return (
        <Suspense fallback={
            <div className="min-h-screen bg-zinc-950 flex items-center justify-center text-white">
                <Loader2 className="w-8 h-8 animate-spin text-blue-500" />
            </div>
        }>
            <EditorPageContent />
        </Suspense>
    );
}
