import * as React from "react";
import { Slot } from "@radix-ui/react-slot";
import { cva, type VariantProps } from "class-variance-authority";

import { cn } from "@/lib/utils";

const buttonVariants = cva(
  "inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium transition-all duration-normal ease-standard focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-strong focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-disabled active:scale-[0.98]",
  {
    variants: {
      variant: {
        // Primary: Solid Navy with white text
        default: "bg-[#272630] text-white hover:bg-[#272630]/90 shadow-soft hover:shadow-medium",
        destructive:
          "bg-destructive text-destructive-foreground hover:bg-destructive/90 shadow-soft hover:shadow-medium",
        // Outline: White background with Navy border
        outline:
          "border border-[#272630] bg-white text-[#272630] hover:bg-[#F5F5F0] hover:border-[#272630]/70",
        // Secondary: Beige background
        secondary:
          "bg-[#E9E7DC] text-[#272630] hover:bg-[#E9E7DC]/80 shadow-soft",
        // Ghost: Subtle beige on hover
        ghost: "hover:bg-[#F5F5F0] hover:text-[#272630]",
        link: "text-[#272630] underline-offset-4 hover:underline",
        // Bronze accent button
        accent: "bg-[#BCAB8A] text-white hover:bg-[#BCAB8A]/90 shadow-soft hover:shadow-medium",
      },
      size: {
        default: "h-10 px-4 py-2",
        sm: "h-9 rounded-md px-3",
        lg: "h-11 rounded-md px-8",
        icon: "h-10 w-10",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
);

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean;
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, asChild = false, ...props }, ref) => {
    const Comp = asChild ? Slot : "button";
    return (
      <Comp
        className={cn(buttonVariants({ variant, size, className }))}
        ref={ref}
        {...props}
      />
    );
  }
);
Button.displayName = "Button";

export { Button, buttonVariants };
