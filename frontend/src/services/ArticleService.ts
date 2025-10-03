// src/services/ArticleService.ts
import type { ArticleSummary } from "../types";

const API_BASE_URL = "http://localhost:8000";

export async function getArticleSummary(url: string): Promise<ArticleSummary> {
    try {
        console.log("📡 Fetching article summary for:", url);

        const response = await fetch(
            `${API_BASE_URL}/article_content?url=${encodeURIComponent(url)}`,
            {
                method: "GET",
                headers: {
                    "Content-Type": "application/json",
                },
            }
        );

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();

        console.log("📦 API Response:", result);

        if (result.status === "error") {
            throw new Error(result.error || "Failed to fetch article");
        }

        if (!result.data) {
            throw new Error("No data returned from API");
        }

        // Validate response structure
        const data = result.data;

        if (!data.title) {
            data.title = "Untitled Article";
        }

        if (!data.authors || !Array.isArray(data.authors)) {
            data.authors = [];
        }

        if (!data.summary || typeof data.summary !== "object") {
            data.summary = {
                Background: "",
                KeyFindings: "",
                Methodology: "",
                EthicalConsiderations: "",
                Implications: "",
                AdditionalNotes: "",
                Conclusion: "",
            };
        }

        // Ensure all required summary keys exist
        const requiredKeys = [
            "Background",
            "KeyFindings",
            "Methodology",
            "EthicalConsiderations",
            "Implications",
            "AdditionalNotes",
            "Conclusion",
        ];

        for (const key of requiredKeys) {
            if (!(key in data.summary)) {
                data.summary[key] = "";
            }
        }

        // Validate pdf_url (optional field)
        if (!data.pdf_url) {
            data.pdf_url = "";
        }

        console.log("✅ Article data validated");
        console.log("📄 PDF URL:", data.pdf_url || "Not available");

        return data as ArticleSummary;

    } catch (error) {
        console.error("❌ Error in getArticleSummary:", error);

        if (error instanceof Error) {
            throw error;
        }

        throw new Error("Unknown error occurred while fetching article");
    }
}

// Optional: Function to check backend health
export async function checkBackendHealth(): Promise<boolean> {
    try {
        const response = await fetch(`${API_BASE_URL}/categories`);
        return response.ok;
    } catch {
        return false;
    }
}