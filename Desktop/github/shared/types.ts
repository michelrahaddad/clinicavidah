// Centralized type definitions for the entire application
export interface SelectedPlan {
  id: number;
  name: string;
  type: 'individual' | 'familiar' | 'empresarial';
  annualPrice: number;
  monthlyPrice?: number;
  adhesionFee: number;
  maxDependents?: number;
  description?: string;
  features?: string[];
  icon?: string; // Para compatibilidade com componentes existentes
}

export interface CustomerData {
  name: string;
  email: string;
  cpf: string;
  phone: string;
}

export interface SubscriptionRequest {
  customer: CustomerData;
  planId: number;
  paymentMethod: 'pix' | 'credit' | 'boleto';
  installments?: number;
}

export interface SubscriptionResponse {
  success: boolean;
  subscription: {
    id: number;
    customerId: number;
    planId: number;
    paymentMethod: string;
    paymentStatus: string;
    totalAmount: string;
    installments: number;
    createdAt: Date;
    expiresAt: Date;
  };
  digitalCard?: {
    id: number;
    cardNumber: string;
    qrCode: string;
    isActive: boolean;
  };
  customer: CustomerData & { id: number };
  plan: SelectedPlan;
}

export interface WhatsAppConversion {
  id?: number;
  phone?: string | null;
  name?: string | null;
  email?: string | null;
  buttonType: 'plan_subscription' | 'doctor_appointment' | 'enterprise_quote';
  planName?: string | null;
  doctorName?: string | null;
  ipAddress?: string | null;
  userAgent?: string | null;
  createdAt?: Date;
}

export interface AdminUser {
  id: number;
  username: string;
  email: string;
  isActive: boolean;
  createdAt: Date;
}

export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface PaginatedResponse<T> extends ApiResponse<T[]> {
  total: number;
  page: number;
  limit: number;
  totalPages: number;
}

// Error types
export class ValidationError extends Error {
  constructor(message: string, public field?: string) {
    super(message);
    this.name = 'ValidationError';
  }
}

export class NotFoundError extends Error {
  constructor(message: string = 'Resource not found') {
    super(message);
    this.name = 'NotFoundError';
  }
}

export class UnauthorizedError extends Error {
  constructor(message: string = 'Unauthorized') {
    super(message);
    this.name = 'UnauthorizedError';
  }
}