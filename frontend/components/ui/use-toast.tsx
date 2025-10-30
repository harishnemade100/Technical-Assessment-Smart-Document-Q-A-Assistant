"use client";

import { toast as sonner } from "sonner";

export const useToast = () => {
  return {
    toast: sonner,
  };
};
