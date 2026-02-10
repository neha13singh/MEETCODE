import { useEffect, useState } from 'react';
import { submissionApi } from '@/lib/api/submissions';
import { formatDistanceToNow } from 'date-fns';
import { CheckCircle2, XCircle, Clock, AlertTriangle } from 'lucide-react';
import { Badge } from '@/components/ui/badge';

interface SubmissionsListProps {
  questionId: string;
}

export default function SubmissionsList({ questionId }: SubmissionsListProps) {
  const [submissions, setSubmissions] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchSubmissions() {
      try {
        const data = await submissionApi.getSubmissions(questionId);
        setSubmissions(data);
      } catch (error) {
        console.error("Failed to fetch submissions", error);
      } finally {
        setLoading(false);
      }
    }

    if (questionId) {
      fetchSubmissions();
    }
  }, [questionId]);

  const [selectedSubmission, setSelectedSubmission] = useState<any>(null);

  if (loading) {
    return <div className="text-zinc-500 text-center py-8">Loading submissions...</div>;
  }

  if (submissions.length === 0) {
    return (
      <div className="text-center py-12">
        <div className="bg-zinc-800/50 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
          <Clock className="w-8 h-8 text-zinc-500" />
        </div>
        <h3 className="text-zinc-300 font-medium mb-1">No submissions yet</h3>
        <p className="text-zinc-500 text-sm">Run your code to see results here.</p>
      </div>
    );
  }

  return (
    <>
      <div className="space-y-4">
        {submissions.map((sub) => (
          <div key={sub.id} className="bg-zinc-800/30 border border-white/5 rounded-lg p-4 hover:border-white/10 transition-colors">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center space-x-3">
                {sub.status === 'accepted' ? (
                  <CheckCircle2 className="w-5 h-5 text-emerald-500" />
                ) : sub.status === 'wrong_answer' ? (
                  <XCircle className="w-5 h-5 text-red-500" />
                ) : (
                  <AlertTriangle className="w-5 h-5 text-yellow-500" />
                )}
                <span className={`font-semibold ${sub.status === 'accepted' ? 'text-emerald-400' :
                    sub.status === 'wrong_answer' ? 'text-red-400' : 'text-yellow-400'
                  }`}>
                  {sub.status === 'accepted' ? 'Accepted' :
                    sub.status === 'wrong_answer' ? 'Wrong Answer' : 'Runtime Error'}
                </span>
              </div>
              <span className="text-xs text-zinc-500">
                {formatDistanceToNow(new Date(sub.created_at), { addSuffix: true })}
              </span>
            </div>

            <div className="grid grid-cols-3 gap-4 mt-3 text-sm">
              <div className="bg-zinc-900/50 rounded px-3 py-2">
                <span className="text-zinc-500 block text-xs mb-1">Language</span>
                <Badge variant="outline" className="text-xs border-zinc-700 text-zinc-400">
                  {sub.language}
                </Badge>
              </div>
              <div className="bg-zinc-900/50 rounded px-3 py-2">
                <span className="text-zinc-500 block text-xs mb-1">Test Cases</span>
                <span className={`${sub.test_cases_passed === sub.total_test_cases ? 'text-emerald-400' : 'text-zinc-300'}`}>
                  {sub.test_cases_passed}/{sub.total_test_cases}
                </span>
              </div>
              <button
                onClick={() => setSelectedSubmission(sub)}
                className="bg-zinc-900/50 hover:bg-zinc-800 rounded px-3 py-2 text-left transition-colors group"
              >
                <span className="text-zinc-500 block text-xs mb-1">Source Code</span>
                <span className="text-blue-400 text-xs font-medium group-hover:underline">View Code</span>
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Code Modal */}
      {selectedSubmission && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4 animate-in fade-in duration-200">
          <div className="bg-zinc-900 border border-white/10 rounded-xl shadow-2xl max-w-3xl w-full max-h-[80vh] flex flex-col">
            <div className="flex items-center justify-between p-4 border-b border-white/5">
              <h3 className="font-semibold text-white">Submission Code</h3>
              <button
                onClick={() => setSelectedSubmission(null)}
                className="text-zinc-500 hover:text-white transition-colors"
              >
                <XCircle className="w-6 h-6" />
              </button>
            </div>
            <div className="p-0 overflow-hidden flex-1 relative">
              <pre className="p-4 overflow-auto max-h-[60vh] text-sm font-mono text-zinc-300 bg-black/50">
                <code>{selectedSubmission.code}</code>
              </pre>
            </div>
            <div className="p-4 border-t border-white/5 flex justify-end">
              <button
                onClick={() => {
                  navigator.clipboard.writeText(selectedSubmission.code);
                }}
                className="text-xs text-zinc-400 hover:text-white mr-4"
              >
                Copy to Clipboard
              </button>
              <Badge variant="secondary" className="font-mono">
                {selectedSubmission.language}
              </Badge>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
