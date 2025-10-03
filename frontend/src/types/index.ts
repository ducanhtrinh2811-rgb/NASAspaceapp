export interface Category {
    id: number;
    name: string;
}

export interface Keyword {
    id: number;
    name: string;
}

export interface Document {
    id: number;
    title: string;
    summary: string;
    link: string;
    category_id: number;
}

export interface Response<T> {
    status: string;
    data: T;
}

export interface SearchRequest {
    query: string;
    limit: number;
}

// ✅ Article summary với cấu trúc JSON từ Backend
export interface ArticleSummary {
    title: string;
    authors: string[];
    summary: {
        Background: string;
        KeyFindings: string;
        Methodology: string;
        EthicalConsiderations: string;
        Implications: string;
        AdditionalNotes: string;
        Conclusion: string;
    };
    pdf_url?: string; // Optional PDF download link
}