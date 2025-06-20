import { apiRequest } from "./queryClient";
import type { ApiResponse, SelectedPlan, SubscriptionRequest, SubscriptionResponse, WhatsAppConversion } from "@shared/types";

// Plan API functions
export const planApi = {
  getAll: async (): Promise<SelectedPlan[]> => {
    const response = await fetch(`${import.meta.env.VITE_API_URL}/api/plans`);
    if (!response.ok) {
      throw new Error(`Failed to fetch plans: ${response.statusText}`);
    }
    const data: ApiResponse<SelectedPlan[]> = await response.json();
    if (!data.success) {
      throw new Error(data.error || 'Failed to fetch plans');
    }
    return data.data || [];
  },

  getById: async (id: number): Promise<SelectedPlan> => {
    const response = await fetch(`/api/plans/${id}`);
    if (!response.ok) {
      throw new Error(`Failed to fetch plan: ${response.statusText}`);
    }
    const data: ApiResponse<SelectedPlan> = await response.json();
    if (!data.success) {
      throw new Error(data.error || 'Failed to fetch plan');
    }
    return data.data!;
  }
};

// Subscription API functions
export const subscriptionApi = {
  create: async (subscriptionData: SubscriptionRequest): Promise<SubscriptionResponse> => {
    const response = await apiRequest('POST', '/api/subscriptions', subscriptionData);
    return await response.json();
  },

  getById: async (id: number) => {
    const response = await fetch(`/api/subscriptions/${id}`);
    if (!response.ok) {
      throw new Error(`Failed to fetch subscription: ${response.statusText}`);
    }
    const data: ApiResponse = await response.json();
    if (!data.success) {
      throw new Error(data.error || 'Failed to fetch subscription');
    }
    return data.data;
  }
};

// WhatsApp API functions
export const whatsappApi = {
  createConversion: async (conversionData: Omit<WhatsAppConversion, 'id' | 'ipAddress' | 'userAgent' | 'createdAt'>): Promise<{ whatsappUrl: string }> => {
    const response = await apiRequest('POST', '/api/whatsapp/conversions', conversionData);
    const data: ApiResponse = await response.json();
    if (!data.success) {
      throw new Error(data.error || 'Failed to create conversion');
    }
    return data.data;
  }
};

// Admin API functions
export const adminApi = {
  login: async (credentials: { username: string; password: string }) => {
    const response = await apiRequest('POST', '/api/admin/login', credentials);
    const data: ApiResponse = await response.json();
    if (!data.success) {
      throw new Error(data.error || 'Login failed');
    }
    return data.data;
  },

  verifyToken: async (token: string) => {
    const response = await fetch(`${import.meta.env.VITE_API_URL}/api/admin/verify`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    if (!response.ok) {
      throw new Error('Token verification failed');
    }
    const data: ApiResponse = await response.json();
    if (!data.success) {
      throw new Error(data.error || 'Token verification failed');
    }
    return data.data;
  },

  getDashboardStats: async (token: string) => {
    const response = await fetch(`${import.meta.env.VITE_API_URL}/api/admin/dashboard/stats`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    if (!response.ok) {
      throw new Error('Failed to fetch dashboard stats');
    }
    const data: ApiResponse = await response.json();
    if (!data.success) {
      throw new Error(data.error || 'Failed to fetch dashboard stats');
    }
    return data.data;
  },

  getConversions: async (token: string, params?: { startDate?: string; endDate?: string; type?: string }) => {
    const url = new URL('/api/admin/conversions', window.location.origin);
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value) url.searchParams.append(key, value);
      });
    }

    const response = await fetch(url.toString(), {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    if (!response.ok) {
      throw new Error('Failed to fetch conversions');
    }
    const data: ApiResponse = await response.json();
    if (!data.success) {
      throw new Error(data.error || 'Failed to fetch conversions');
    }
    return data.data;
  },

  exportConversions: async (token: string, format: string = 'csv', type: string = 'internal') => {
    const url = `/api/admin/conversions/export?format=${format}&type=${type}`;
    const response = await fetch(url, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    if (!response.ok) {
      throw new Error('Failed to export conversions');
    }
    
    if (format === 'csv') {
      const blob = await response.blob();
      const downloadUrl = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = downloadUrl;
      link.download = `conversions-${Date.now()}.csv`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(downloadUrl);
      return;
    }
    
    const data: ApiResponse = await response.json();
    if (!data.success) {
      throw new Error(data.error || 'Failed to export conversions');
    }
    return data.data;
  }
};