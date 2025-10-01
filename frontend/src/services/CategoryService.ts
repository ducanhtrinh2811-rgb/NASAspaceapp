import type { Category, Response } from "../types";
import api from "./http";
    // Mock service functions tạm thời
// const mockCategories: Category[] = [
//     { id: 1, name: "Technology" },
//     { id: 2, name: "Science" },
//     { id: 3, name: "Health" },
// ];

export const getCategories = async (): Promise<Category[]> => {
    // return mockCategories
    try {
        const res = await api.get<Response<Category[]>>('/categories');
        if (res.data.status === 'success') {
            return res.data.data;
        }
        else {
            throw new Error('Failed to fetch categories');
        }
    }
    catch (err) {
        console.error('get categories error:', err);
        return [];
    }
}