import api from './services/api';
import { Source } from './types';

export const getSources = async (): Promise<Source[]> => {
    const response = await api.get('/sources/');
    return response.data;
};

export const createSource = async (url: string): Promise<Source> => {
    // Generate a temporary name based on URL domain
    let name = "Nova Fonte";
    try {
        const urlObj = new URL(url);
        name = urlObj.hostname;
    } catch (e) {
        // ignore
    }
    const response = await api.post('/sources/', { url, name });
    return response.data;
};

export const analyzeSource = async (uid: string): Promise<{ inclusion_score: number, reasoning: string }> => {
    const response = await api.post(`/sources/${uid}/analyze`);
    return response.data;
};

export const sendChatMessage = async (uid: string, prompt: string): Promise<{ answer: string }> => {
    const response = await api.post(`/sources/${uid}/chat`, { prompt });
    return response.data;
};
