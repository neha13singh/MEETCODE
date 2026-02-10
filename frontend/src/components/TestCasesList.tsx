import { TestCase } from '@/lib/api/questions';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { CheckCircle2, Eye, EyeOff } from 'lucide-react';

interface TestCasesListProps {
    testCases: TestCase[];
}

export default function TestCasesList({ testCases }: TestCasesListProps) {
    const visibleCases = testCases.filter((tc: any) => tc.is_sample);

    if (!visibleCases || visibleCases.length === 0) {
        return (
            <div className="text-center py-12">
                <div className="bg-zinc-800/50 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                    <CheckCircle2 className="w-8 h-8 text-zinc-500" />
                </div>
                <h3 className="text-zinc-300 font-medium mb-1">No visible test cases available</h3>
                <p className="text-zinc-500 text-sm">Check back later or contact support.</p>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-white">Visible Test Cases</h3>
                <div className="flex space-x-2">
                    <Badge variant="outline" className="bg-emerald-500/10 text-emerald-400 border-emerald-500/20">
                        {visibleCases.length} Test Cases
                    </Badge>
                </div>
            </div>

            <div className="space-y-4">
                {visibleCases.map((tc: any, idx) => (
                    <Card key={tc.id || idx} className="bg-zinc-900/50 border-white/5 overflow-hidden transition-all hover:border-white/10 group">
                        <div className="flex items-center justify-between px-4 py-3 bg-white/5 border-b border-white/5">
                            <div className="flex items-center space-x-2">
                                <span className="text-xs font-mono text-zinc-500">#{idx + 1}</span>
                                <span className="text-sm font-medium text-zinc-300">
                                    Sample Case
                                </span>
                            </div>
                            <div className="flex items-center text-xs text-emerald-400 font-medium bg-emerald-400/10 px-2 py-0.5 rounded-full border border-emerald-400/20">
                                <Eye className="w-3 h-3 mr-1" />
                                Visible
                            </div>
                        </div>

                        <div className="p-4 space-y-4">
                            <div className="space-y-2">
                                <span className="text-xs font-semibold text-zinc-500 uppercase tracking-wider">Input</span>
                                <pre className="p-3 bg-black/50 rounded-lg border border-white/5 text-sm font-mono text-zinc-300 overflow-x-auto">
                                    <code>{tc.input}</code>
                                </pre>
                            </div>

                            <div className="space-y-2">
                                <span className="text-xs font-semibold text-zinc-500 uppercase tracking-wider">Expected Output</span>
                                <pre className="p-3 bg-emerald-500/5 rounded-lg border border-emerald-500/10 text-sm font-mono text-emerald-300 overflow-x-auto">
                                    <code>{tc.expected_output}</code>
                                </pre>
                            </div>
                        </div>
                    </Card>
                ))}
            </div>
        </div>
    );
}
