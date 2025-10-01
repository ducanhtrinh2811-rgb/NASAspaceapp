import api from "./http";
import type { Document, Response, SearchRequest } from "../types";

// const mockDocuments: Document[] = [
//     { id: 1, title: "React Tips", summary: "Learn React effectively", link: "https://reactjs.org", category_id: 1 },
//     { id: 2, title: "Space Exploration", summary: "The future of space travel", link: "https://www.nasa.gov", category_id: 2 },
//     { id: 3, title: "Healthy Eating", summary: "Nutrition tips for everyone", link: "https://www.healthline.com", category_id: 3 },
//     { id: 4, title: "Advanced React", summary: "Hooks, Context, and more", link: "https://reactjs.org/docs/hooks-intro.html", category_id: 1 },
// ];


export const getDocumentsByCategory = async (categoryId: number): Promise<Document[]> => {
    // return mockDocuments
    try {
        const res = await api.get<Response<Document[]>>(`/categories/${categoryId}/documents`);
        if (res.data.status === "success") {
            return res.data.data;
        } else {
            throw new Error("Failed to fetch documents");
        }
    } catch (err) {
        console.error("getDocumentsByCategory error:", err);
        return [];
    }
}

export const searchDocuments = async (body: SearchRequest): Promise<Document[]> => {
    // return mockDocuments
    try {
        const res = await api.post<Response<Document[]>>(`/search`, body);
        if (res.data.status === "success") {
            return res.data.data;
        } else {
            throw new Error("Search documents failed");
        }
    } catch (err) {
        console.error("searchDocuments error:", err);
        return [];
    }
}