// Application constants
export const WHATSAPP_CONFIG = {
  DEFAULT_PHONE: '5516993247676',
  WEB_URL: 'https://web.whatsapp.com/send',
  MOBILE_URL: 'https://wa.me',
  MESSAGE_TEMPLATES: {
    PLAN_SUBSCRIPTION: (name: string, phone: string, email: string, planName: string) =>
      `Olá! Tenho interesse no plano ${planName}.\n\nNome: ${name}\nTelefone: ${phone}\nEmail: ${email}\n\nGostaria de mais informações sobre como contratar.`,
    DOCTOR_APPOINTMENT: (name: string, phone: string, email: string, doctorName: string) =>
      `Olá! Gostaria de agendar uma consulta com ${doctorName}.\n\nNome: ${name}\nTelefone: ${phone}\nEmail: ${email}`,
    ENTERPRISE_QUOTE: (name: string, phone: string, email: string) =>
      `Olá! Gostaria de solicitar um orçamento corporativo.\n\nNome: ${name}\nTelefone: ${phone}\nEmail: ${email}`
  }
} as const;

export const VALIDATION_LIMITS = {
  NAME: { MIN: 2, MAX: 100 },
  PHONE: { MIN: 10, MAX: 11 },
  EMAIL: { MAX: 254 },
  CPF: { LENGTH: 11 },
  REQUEST_SIZE: { MAX: 10 * 1024 * 1024 } // 10MB
} as const;

export const RATE_LIMITS = {
  GENERAL: { WINDOW_MS: 15 * 60 * 1000, MAX: 100 }, // 100 requests per 15 minutes
  API: { WINDOW_MS: 15 * 60 * 1000, MAX: 50 }, // 50 API requests per 15 minutes
  WHATSAPP: { WINDOW_MS: 5 * 60 * 1000, MAX: 10 }, // 10 WhatsApp requests per 5 minutes
  LOGIN: { WINDOW_MS: 15 * 60 * 1000, MAX: 5 }, // 5 login attempts per 15 minutes
  ADMIN: { WINDOW_MS: 15 * 60 * 1000, MAX: 20 } // 20 admin requests per 15 minutes
} as const;

export const HTTP_STATUS = {
  OK: 200,
  CREATED: 201,
  BAD_REQUEST: 400,
  UNAUTHORIZED: 401,
  FORBIDDEN: 403,
  NOT_FOUND: 404,
  TOO_MANY_REQUESTS: 429,
  INTERNAL_SERVER_ERROR: 500
} as const;