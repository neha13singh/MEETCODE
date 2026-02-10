import apiClient from './client';

export interface MatchParticipant {
    id: string;
    user_id: string;
    result: string | null;
    execution_time: number | null;
    test_cases_passed: number | null;
    total_test_cases: number | null;
    joined_at: string;
}

export interface Match {
    id: string;
    question_id: string;
    mode: string;
    difficulty: string;
    max_time: number;
    status: string;
    started_at: string | null;
    started_at_ts: number | null;
    completed_at: string | null;
    winner_id: string | null;
    created_at: string;
    participants: MatchParticipant[];
    question?: any; // Avoiding circular dependency for now, or use Question interface
}

export const matchesApi = {
    getMatch: async (id: string): Promise<Match> => {
        const response = await apiClient.get(`/matches/${id}`);
        return response.data;
    },

    createMatch: async (data: { mode: string; question_id?: string; difficulty?: string }): Promise<Match> => {
        const response = await apiClient.post('/matches/', data);
        return response.data;
    },

    surrender: async (id: string): Promise<any> => {
        const response = await apiClient.post(`/matches/${id}/surrender`);
        return response.data;
    },

    timeout: async (id: string): Promise<any> => {
        const response = await apiClient.post(`/matches/${id}/timeout`);
        return response.data;
    }
};
