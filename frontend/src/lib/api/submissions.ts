import apiClient from './client';

export interface SubmissionRun {
  code: string;
  language: string;
  question_id: string; // uuid
  match_id?: string;
}

export interface SubmissionResult {
  status: string;
  test_cases_passed: number;
  total_test_cases: number;
  error_message?: string;
  details: any[];
}

export const submissionApi = {
  runCode: async (data: SubmissionRun): Promise<SubmissionResult> => {
    const response = await apiClient.post('/submissions/run', data);
    return response.data;
  },
  
  submitCode: async (data: SubmissionRun) => {
    const response = await apiClient.post('/submissions/submit', data);
    return response.data;
  },

  getSubmissions: async (questionId: string) => {
    const response = await apiClient.get(`/submissions/?question_id=${questionId}`);
    return response.data;
  }
};
