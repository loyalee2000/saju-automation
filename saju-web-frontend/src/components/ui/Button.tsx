import { cn } from "@/lib/utils";
import { ButtonHTMLAttributes, forwardRef } from "react";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
    variant?: "primary" | "secondary" | "outline";
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
    ({ className, variant = "primary", ...props }, ref) => {
        const variants = {
            primary: "bg-amber-600 hover:bg-amber-500 text-white font-bold",
            secondary: "bg-gray-700 hover:bg-gray-600 text-gray-100",
            outline: "border border-amber-600 text-amber-500 hover:bg-amber-900/20",
        };

        return (
            <button
                ref={ref}
                className={cn(
                    "px-6 py-3 rounded-lg transition-all active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed",
                    variants[variant],
                    className
                )}
                {...props}
            />
        );
    }
);
Button.displayName = "Button";
