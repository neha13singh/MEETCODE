"use client";

import { useState, useEffect } from 'react';
import { createPortal } from 'react-dom';
import { useAuth } from '@/context/AuthContext';
import apiClient from '@/lib/api/client';
import { X, Zap, UserPlus, Loader2 } from 'lucide-react';
import { Button } from './ui/button';

interface LoginModalProps {
    isOpen: boolean;
    onCloseAction: () => void;
    initialView?: 'login' | 'register';
}

export default function LoginModal({ isOpen, onCloseAction, initialView = 'login' }: LoginModalProps) {
    const { login } = useAuth();
    const [isLogin, setIsLogin] = useState(initialView === 'login');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [formData, setFormData] = useState({
        username: '',
        email: '',
        password: ''
    });

    useEffect(() => {
        if (isOpen) {
            setIsLogin(initialView === 'login');
            setError(null);
            setFormData({ username: '', email: '', password: '' });
        }
    }, [isOpen, initialView]);

    if (!isOpen) return null;

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setError(null);

        try {
            if (isLogin) {
                const loginData = new URLSearchParams();
                loginData.append('username', formData.username);
                loginData.append('password', formData.password);

                const response = await apiClient.post('/auth/login', loginData, {
                    headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
                });
                login(response.data.access_token);
            } else {
                await apiClient.post('/users/register', {
                    username: formData.username,
                    email: formData.email,
                    password: formData.password
                });
                setIsLogin(true);
                setError("Account created! Please sign in.");
                return;
            }
            onCloseAction();
        } catch (err: any) {
            setError(err.response?.data?.detail || "Authentication failed. Check entries.");
        } finally {
            setLoading(false);
        }
    };

    // Use portal to render at root level to avoid stacking context issues
    if (typeof document === 'undefined') return null;

    return createPortal(
        <div className="fixed inset-0 z-[9999] flex items-center justify-center p-4">
            {/* Backdrop */}
            <div
                className="absolute inset-0 bg-black/50 backdrop-blur-md animate-in fade-in duration-300"
                onClick={onCloseAction}
            />

            {/* Modal Card */}
            <div className="relative w-[90%] md:w-full max-w-md glass-card p-6 md:p-10 border border-primary/20 cyber-shape shadow-2xl shadow-primary/10 max-h-[90vh] overflow-y-auto animate-in fade-in zoom-in-95 duration-300">

                {/* Close Button */}
                <button
                    onClick={onCloseAction}
                    className="absolute top-6 right-6 p-2 text-zinc-500 hover:text-white transition-colors z-10"
                >
                    <X className="w-5 h-5" />
                </button>

                {/* Header */}
                <div className="text-center mb-8 relative z-10">
                    <div className="inline-flex items-center justify-center w-12 h-12 bg-espresso-mid mb-4 cyber-shape border border-primary/30 glow-cyan">
                        {isLogin ? <Zap className="w-6 h-6 text-primary" /> : <UserPlus className="w-6 h-6 text-primary" />}
                    </div>
                    <h2 className="text-3xl font-black tracking-tighter italic mb-1 uppercase text-white">
                        {isLogin ? 'SIGN_IN' : 'SIGN_UP'}
                    </h2>
                    <p className="text-[10px] text-zinc-500 font-mono tracking-widest uppercase font-bold">
                        {isLogin ? 'ACCESS YOUR COMMAND CENTER' : 'CREATE YOUR SYSTEM PROFILE'}
                    </p>
                </div>

                {/* Form */}
                <form onSubmit={handleSubmit} className="space-y-6 relative z-10">
                    {error && (
                        <div className="p-3 bg-destructive/10 border border-destructive/20 text-destructive text-[9px] font-black tracking-widest uppercase cyber-shape text-center">
                            ERROR :: {error}
                        </div>
                    )}

                    <div className="space-y-4">
                        <div className="space-y-1.5">
                            <label className="text-[9px] font-black tracking-widest text-zinc-500 uppercase ml-2">USERNAME</label>
                            <input
                                type="text"
                                required
                                className="w-full h-12 px-5 bg-espresso-dark border border-white/5 text-white placeholder:text-zinc-700 focus:outline-none focus:border-primary/50 focus:glow-cyan transition-all cyber-shape font-mono text-xs"
                                placeholder="USERNAME"
                                value={formData.username}
                                onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                            />
                        </div>

                        {!isLogin && (
                            <div className="space-y-1.5">
                                <label className="text-[9px] font-black tracking-widest text-zinc-500 uppercase ml-2">EMAIL_ADDR</label>
                                <input
                                    type="email"
                                    required
                                    className="w-full h-12 px-5 bg-espresso-dark border border-white/5 text-white placeholder:text-zinc-700 focus:outline-none focus:border-primary/50 focus:glow-cyan transition-all cyber-shape font-mono text-xs"
                                    placeholder="EMAIL"
                                    value={formData.email}
                                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                                />
                            </div>
                        )}

                        <div className="space-y-1.5">
                            <label className="text-[9px] font-black tracking-widest text-zinc-500 uppercase ml-2">PASSWORD</label>
                            <input
                                type="password"
                                required
                                className="w-full h-12 px-5 bg-espresso-dark border border-white/5 text-white placeholder:text-zinc-700 focus:outline-none focus:border-primary/50 focus:glow-cyan transition-all cyber-shape font-mono text-xs"
                                placeholder="PASSWORD"
                                value={formData.password}
                                onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                            />
                        </div>
                    </div>

                    <Button
                        type="submit"
                        disabled={loading}
                        className="w-full h-12 bg-primary hover:bg-primary/80 text-white font-black tracking-widest text-[10px] cyber-shape border-0 glow-cyan shadow-xl shadow-primary/20"
                    >
                        {loading ? (
                            <Loader2 className="w-5 h-5 animate-spin" />
                        ) : (
                            isLogin ? 'INITIALIZE_SESSION' : 'CREATE_ACCOUNT'
                        )}
                    </Button>

                    <div className="text-center pt-2">
                        <button
                            type="button"
                            onClick={() => setIsLogin(!isLogin)}
                            className="text-[10px] font-black tracking-widest text-zinc-500 hover:text-primary transition-colors uppercase"
                        >
                            {isLogin ? 'NEW HERE?_SIGN_UP' : 'EXISTING_USER?_SIGN_IN'}
                        </button>
                    </div>
                </form>
            </div>
        </div>,
        document.body
    );
}
