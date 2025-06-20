import rateLimit from 'express-rate-limit';
import { RATE_LIMITS } from '@shared/constants';

/**
 * General rate limiter for all requests
 */
export const generalLimiter = rateLimit({
  windowMs: RATE_LIMITS.GENERAL.WINDOW_MS,
  max: RATE_LIMITS.GENERAL.MAX,
  message: { error: 'Muitas requisições. Tente novamente em alguns minutos.' },
  standardHeaders: true,
  legacyHeaders: false,
});

/**
 * API rate limiter for API endpoints
 */
export const apiLimiter = rateLimit({
  windowMs: RATE_LIMITS.API.WINDOW_MS,
  max: RATE_LIMITS.API.MAX,
  message: { error: 'Limite de requisições da API excedido. Tente novamente em alguns minutos.' },
  standardHeaders: true,
  legacyHeaders: false,
});

/**
 * WhatsApp tracking rate limiter
 */
export const whatsappLimiter = rateLimit({
  windowMs: RATE_LIMITS.WHATSAPP.WINDOW_MS,
  max: RATE_LIMITS.WHATSAPP.MAX,
  message: { error: 'Muitas solicitações WhatsApp. Aguarde alguns minutos.' },
  standardHeaders: true,
  legacyHeaders: false,
});

/**
 * Login rate limiter
 */
export const loginLimiter = rateLimit({
  windowMs: RATE_LIMITS.LOGIN.WINDOW_MS,
  max: RATE_LIMITS.LOGIN.MAX,
  message: { error: 'Muitas tentativas de login. Tente novamente em 15 minutos.' },
  standardHeaders: true,
  legacyHeaders: false,
});

/**
 * Admin rate limiter
 */
export const adminLimiter = rateLimit({
  windowMs: RATE_LIMITS.ADMIN.WINDOW_MS,
  max: RATE_LIMITS.ADMIN.MAX,
  message: { error: 'Limite de requisições administrativas excedido.' },
  standardHeaders: true,
  legacyHeaders: false,
});