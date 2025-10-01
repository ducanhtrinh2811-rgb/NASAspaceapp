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

export interface ArticleData {
    html: string;
    style: string;
    links: string[];
}