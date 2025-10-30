import * as React from "react";
import { cn } from "@/lib/utils";

export function Button({ className, variant = "default", ...props }: any) {
  const variants = {
    default:
      "bg-indigo-600 hover:bg-indigo-500 text-white font-medium px-4 py-2 rounded-lg shadow-md",
    outline:
      "border border-gray-700 text-gray-300 hover:bg-gray-800 px-4 py-2 rounded-lg",
  };

  return <button className={cn(variants[variant], className)} {...props} />;
}
