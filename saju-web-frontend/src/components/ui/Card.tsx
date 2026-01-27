import { cn } from "@/lib/utils";
import { ReactNode } from "react";

interface CardProps {
    children: ReactNode;
    className?: string;
}

export function Card({ children, className }: CardProps) {
    return (
        <div className={cn("bg-gray-800 border border-gray-700 rounded-xl p-6 shadow-lg", className)}>
            {children}
        </div>
    );
}

export function CardHeader({ children, className }: CardProps) {
    return <div className={cn("mb-4", className)}>{children}</div>;
}

export function CardTitle({ children, className }: CardProps) {
    return <h3 className={cn("text-xl font-bold text-amber-500", className)}>{children}</h3>;
}

export function CardContent({ children, className }: CardProps) {
    return <div className={cn("", className)}>{children}</div>;
}
