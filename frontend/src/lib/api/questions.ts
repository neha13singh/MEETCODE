import apiClient from './client';

export interface TestCase {
  id: string;
  input: string;
  expected_output: string;
}

export interface Question {
  id: string;
  title: string;
  slug: string;
  description: string;
  difficulty: string;
  avg_solve_time?: number;
  examples: any[];
  test_cases?: TestCase[];
  templates?: any[];
  is_solved?: boolean;
}

export const questionApi = {
  getQuestionBySlug: async (slug: string): Promise<Question> => {
    const response = await apiClient.get(`/questions/${slug}`);
    return response.data;
  },

  getQuestions: async (): Promise<Question[]> => {
    const response = await apiClient.get('/questions/');
    return response.data;
  }
};
