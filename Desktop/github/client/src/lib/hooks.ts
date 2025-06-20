import { useQuery } from "@tanstack/react-query";
import { planApi } from "./api";

// Custom hooks for API calls
export const usePlans = () => {
  return useQuery({
    queryKey: ['/api/plans'],
    queryFn: planApi.getAll,
    staleTime: 5 * 60 * 1000, // 5 minutes
    refetchOnWindowFocus: false,
  });
};

export const usePlan = (id: number) => {
  return useQuery({
    queryKey: ['/api/plans', id],
    queryFn: () => planApi.getById(id),
    enabled: !!id,
    staleTime: 5 * 60 * 1000,
    refetchOnWindowFocus: false,
  });
};