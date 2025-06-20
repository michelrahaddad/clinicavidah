import type { Express } from "express";
import { createServer, type Server } from "http";
import { PlanController } from "./controllers/planController";
import { SubscriptionController } from "./controllers/subscriptionController";
import { WhatsAppController } from "./controllers/whatsappController";
import { AdminController } from "./controllers/adminController";
import { body, param } from "express-validator";
import { validateRequest, sanitizeRequest } from "./middleware/validation";
import { loginLimiter, adminLimiter, whatsappLimiter } from "./middleware/rateLimiting";
import { authenticateAdmin } from "./middleware/auth";
import { sanitizeInput } from "./security";
import { formatAdminResponse } from "./middleware/responseFormatter";

export async function registerRoutes(app: Express): Promise<Server> {
  
  // Health check endpoint
  app.get("/health", (req, res) => {
    res.json({ 
      success: true, 
      status: "healthy", 
      timestamp: new Date().toISOString() 
    });
  });

  // Apply global middleware for API routes
  app.use("/api", sanitizeRequest);
  app.use(formatAdminResponse);
  
  // Plan routes
  app.get("/api/plans", PlanController.getAllPlans);
  app.get("/api/plans/:id", 
    [param('id').isInt({ min: 1 }).withMessage('ID do plano deve ser um número inteiro positivo')],
    validateRequest,
    PlanController.getPlanById
  );

  // Subscription routes
  app.post("/api/subscriptions",
    [
      body('customer.name').isLength({ min: 2, max: 100 }).trim().matches(/^[a-zA-ZÀ-ÿ\s]+$/).withMessage('Nome deve conter apenas letras e espaços'),
      body('customer.email').isEmail().normalizeEmail().withMessage('Email inválido'),
      body('customer.cpf').isLength({ min: 11, max: 14 }).withMessage('CPF deve ter 11 dígitos'),
      body('customer.phone').isLength({ min: 10, max: 15 }).withMessage('Telefone inválido'),
      body('planId').isInt({ min: 1 }).withMessage('ID do plano inválido'),
      body('paymentMethod').isIn(['pix', 'credit', 'boleto']).withMessage('Método de pagamento inválido'),
      body('installments').optional().isInt({ min: 1, max: 12 }).withMessage('Número de parcelas inválido')
    ],
    validateRequest,
    SubscriptionController.createSubscription
  );
  
  app.get("/api/subscriptions/:id",
    [param('id').isInt({ min: 1 }).withMessage('ID da assinatura deve ser um número inteiro positivo')],
    validateRequest,
    SubscriptionController.getSubscription
  );

  // WhatsApp conversion routes - validação simplificada
  app.post("/track-whatsapp",
    whatsappLimiter,
    [
      body('buttonType')
        .isIn(['plan_subscription', 'doctor_appointment', 'enterprise_quote'])
        .withMessage('Tipo de botão inválido'),
      body('name')
        .optional()
        .isLength({ min: 2, max: 100 })
        .trim(),
      body('phone')
        .optional({ nullable: true, checkFalsy: true }),
      body('email')
        .optional()
        .isEmail()
        .normalizeEmail()
        .withMessage('Email inválido'),
      body('planName')
        .optional()
        .isLength({ max: 100 })
        .trim(),
      body('doctorName')
        .optional()
        .isLength({ max: 100 })
        .trim()
    ],
    validateRequest,
    WhatsAppController.createConversion
  );

  app.post("/api/whatsapp/conversions",
    whatsappLimiter,
    [
      body('buttonType')
        .isIn(['plan_subscription', 'doctor_appointment', 'enterprise_quote'])
        .withMessage('Tipo de botão inválido'),
      body('name')
        .optional()
        .isLength({ min: 2, max: 100 })
        .trim()
        .matches(/^[a-zA-ZÀ-ÿ\s]+$/)
        .withMessage('Nome deve conter apenas letras e espaços'),
      body('phone')
        .optional({ nullable: true, checkFalsy: true }),
      body('email')
        .optional()
        .isEmail()
        .normalizeEmail()
        .withMessage('Email inválido'),
      body('planName')
        .optional()
        .isLength({ max: 100 })
        .trim(),
      body('doctorName')
        .optional()
        .isLength({ max: 100 })
        .trim()
    ],
    validateRequest,
    WhatsAppController.createConversion
  );

  // Admin routes
  app.post("/api/admin/login",
    loginLimiter,
    [
      body('username')
        .isLength({ min: 3, max: 50 })
        .trim()
        .matches(/^[a-zA-Z0-9_-]+$/)
        .withMessage('Username deve conter apenas letras, números, _ e -'),
      body('password')
        .isLength({ min: 6, max: 100 })
        .withMessage('Senha deve ter entre 6 e 100 caracteres')
    ],
    validateRequest,
    AdminController.login
  );

  app.get("/api/admin/verify", AdminController.verifyToken);

  // Protected admin routes
  app.use("/api/admin", adminLimiter);
  app.use("/api/admin", authenticateAdmin);

  app.get("/api/admin/dashboard/stats", AdminController.getDashboardStats);
  app.get("/api/admin/conversions", WhatsAppController.getConversions);
  app.get("/api/admin/conversions/export", WhatsAppController.exportConversions);

  return createServer(app);
}