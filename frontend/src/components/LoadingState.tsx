// src/components/LoadingState.tsx
import { Loader2 } from "lucide-react";

interface LoadingStateProps {
    message?: string;
    submessage?: string;
}

export function LoadingState({
    message = "Loading...",
    submessage
}: LoadingStateProps) {
    return (
        <div className="min-h-screen bg-gray-50 flex items-center justify-center">
            <div className="text-center">
                <Loader2 className="w-16 h-16 text-blue-600 animate-spin mx-auto mb-4" />
                <p className="text-gray-700 text-lg font-medium">{message}</p>
                {submessage && (
                    <p className="text-gray-500 text-sm mt-2">{submessage}</p>
                )}
            </div>
        </div>
    );
}

// Alternative spinner styles
export function SpinnerSmall() {
    return (
        <div className="inline-block">
            <Loader2 className="w-5 h-5 text-blue-600 animate-spin" />
        </div>
    );
}

export function SpinnerOverlay({ message }: { message?: string }) {
    return (
        <div className="fixed inset-0 bg-black bg-opacity-30 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 shadow-xl">
                <Loader2 className="w-12 h-12 text-blue-600 animate-spin mx-auto mb-3" />
                {message && (
                    <p className="text-gray-700 font-medium">{message}</p>
                )}
            </div>
        </div>
    );
}