import { z } from "zod";
import { insertCustomerSchema, insertSubscriptionSchema, insertDigitalCardSchema, insertAdminUserSchema, insertWhatsappConversionSchema } from "./schema";

// CPF validation function
export function isValidCPF(cpf: string): boolean {
  cpf = cpf.replace(/[^\d]/g, '');
  
  if (cpf.length !== 11 || /^(\d)\1{10}$/.test(cpf)) {
    return false;
  }
  
  let sum = 0;
  for (let i = 0; i < 9; i++) {
    sum += parseInt(cpf.charAt(i)) * (10 - i);
  }
  let remainder = 11 - (sum % 11);
  if (remainder === 10 || remainder === 11) remainder = 0;
  if (remainder !== parseInt(cpf.charAt(9))) return false;
  
  sum = 0;
  for (let i = 0; i < 10; i++) {
    sum += parseInt(cpf.charAt(i)) * (11 - i);
  }
  remainder = 11 - (sum % 11);
  if (remainder === 10 || remainder === 11) remainder = 0;
  if (remainder !== parseInt(cpf.charAt(10))) return false;
  
  return true;
}

/**
 * Validates Brazilian phone numbers (landline and mobile)
 */
export function isValidPhone(phone: string): boolean {
  const cleanPhone = phone.replace(/\D/g, '');
  
  // Must have 10 or 11 digits (landline or mobile)
  if (cleanPhone.length < 10 || cleanPhone.length > 11) return false;
  
  // First two digits are area code (11-99)
  const areaCode = parseInt(cleanPhone.substring(0, 2));
  if (areaCode < 11 || areaCode > 99) return false;
  
  // Mobile numbers (11 digits) must start with 9 after area code
  if (cleanPhone.length === 11) {
    return cleanPhone.charAt(2) === '9';
  }
  
  // Landline numbers (10 digits) must NOT start with 9 after area code
  if (cleanPhone.length === 10) {
    return cleanPhone.charAt(2) !== '9';
  }
  
  return true;
}

// Validation schemas using constants
export const emailSchema = z.string()
  .email('Email inválido')
  .min(1, 'Email é obrigatório');

// CPF validation schema
export const cpfSchema = z.string()
  .min(11, 'CPF deve ter 11 dígitos')
  .max(14, 'CPF inválido')
  .refine((val) => isValidCPF(val), 'CPF inválido');

// Phone validation schema
export const phoneSchema = z.string()
  .min(1, 'Telefone é obrigatório')
  .refine((phone) => {
    const cleanPhone = phone.replace(/\D/g, '');
    return cleanPhone.length >= 10 && cleanPhone.length <= 11;
  }, 'Telefone deve ter entre 10 e 11 dígitos')
  .refine(isValidPhone, 'Formato de telefone inválido');

export const nameSchema = z.string()
  .min(2, 'Nome deve ter pelo menos 2 caracteres')
  .max(100, 'Nome muito longo')
  .regex(/^[a-zA-ZÀ-ÿ\s]+$/, 'Nome deve conter apenas letras e espaços');

// Customer data validation schema
export const customerSchema = z.object({
  name: nameSchema,
  email: emailSchema,
  cpf: cpfSchema,
  phone: phoneSchema,
});

// Subscription request validation schema
export const subscriptionRequestSchema = z.object({
  customer: customerSchema,
  planId: z.number().int().positive('ID do plano inválido'),
  paymentMethod: z.enum(['pix', 'credit', 'boleto'], {
    errorMap: () => ({ message: 'Método de pagamento inválido' })
  }),
  installments: z.number().int().min(1).max(12).optional().default(1),
});

// WhatsApp conversion validation schema
export const whatsappConversionSchema = z.object({
  phone: z.string().optional().or(z.literal("")),
  name: nameSchema.optional(),
  email: emailSchema.optional(),
  buttonType: z.enum(['plan_subscription', 'doctor_appointment', 'enterprise_quote']),
  planName: z.string().optional(),
  doctorName: z.string().optional(),
});

// Admin login validation schema
export const adminLoginSchema = z.object({
  username: z.string()
    .min(3, 'Username deve ter pelo menos 3 caracteres')
    .max(50, 'Username muito longo')
    .regex(/^[a-zA-Z0-9_-]+$/, 'Username deve conter apenas letras, números, _ e -'),
  password: z.string()
    .min(6, 'Senha deve ter pelo menos 6 caracteres')
    .max(100, 'Senha muito longa'),
});

// Plan validation schema
export const planSchema = z.object({
  id: z.number().int().positive(),
  name: z.string().min(1, 'Nome do plano é obrigatório'),
  type: z.enum(['individual', 'familiar', 'empresarial']),
  annualPrice: z.number().nonnegative('Preço anual deve ser não negativo'),
  monthlyPrice: z.number().nonnegative('Preço mensal deve ser não negativo').optional(),
  adhesionFee: z.number().nonnegative('Taxa de adesão deve ser não negativa'),
  maxDependents: z.number().int().nonnegative().optional().default(0),
  isActive: z.boolean().default(true),
});

// Sanitization functions
export function sanitizeString(input: string): string {
  return input
    .trim()
    .replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '')
    .replace(/javascript:/gi, '')
    .replace(/on\w+\s*=/gi, '')
    .replace(/[<>]/g, '');
}

export function sanitizeObject<T extends Record<string, any>>(obj: T): T {
  const sanitized = {} as T;
  
  for (const [key, value] of Object.entries(obj)) {
    if (typeof value === 'string') {
      sanitized[key as keyof T] = sanitizeString(value) as T[keyof T];
    } else if (typeof value === 'object' && value !== null) {
      sanitized[key as keyof T] = sanitizeObject(value) as T[keyof T];
    } else {
      sanitized[key as keyof T] = value;
    }
  }
  
  return sanitized;
}

// Format utilities
export function formatCPF(cpf: string): string {
  const cleaned = cpf.replace(/\D/g, '');
  return cleaned.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, '$1.$2.$3-$4');
}

export function formatPhone(phone: string): string {
  const cleaned = phone.replace(/\D/g, '');
  if (cleaned.length === 11) {
    return cleaned.replace(/(\d{2})(\d{5})(\d{4})/, '($1) $2-$3');
  } else if (cleaned.length === 10) {
    return cleaned.replace(/(\d{2})(\d{4})(\d{4})/, '($1) $2-$3');
  }
  return phone;
}

export function formatCurrency(value: number): string {
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL'
  }).format(value);
}