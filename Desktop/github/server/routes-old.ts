import type { Express } from "express";
import { createServer, type Server } from "http";
import { PlanController } from "./controllers/planController";
import { SubscriptionController } from "./controllers/subscriptionController";
import { WhatsAppController } from "./controllers/whatsappController";
import { AdminController } from "./controllers/adminController";
import { body, param } from "express-validator";
import { validateRequest, sanitizeInput } from "./middleware/validation";
import { loginLimiter, adminLimiter, whatsappLimiter } from "./middleware/rateLimiting";
import { authenticateAdmin } from "./middleware/auth";

// Health check endpoint
function setupHealthCheck(app: Express) {
  app.get("/health", (req, res) => {
    res.json({ 
      success: true, 
      status: "healthy", 
      timestamp: new Date().toISOString() 
    });
  });
}

export async function registerRoutes(app: Express): Promise<Server> {
  
  // Setup health check
  setupHealthCheck(app);
  
  // Apply global middleware for API routes
  app.use("/api", sanitizeInput);
  
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
      const plan = await storage.getPlanById(data.planId);
      if (!plan) {
        return res.status(404).json({ message: "Plano não encontrado" });
      }

      // Calculate total amount based on payment method and installments
      let totalAmount = parseFloat(plan.annualPrice) + parseFloat(plan.adhesionFee);
      
      if (data.paymentMethod === 'pix') {
        // 10% discount for PIX
        totalAmount = (parseFloat(plan.annualPrice) * 0.9) + parseFloat(plan.adhesionFee);
      } else if (data.paymentMethod === 'boleto' && data.installments > 1) {
        // Boleto pricing for installments
        const monthlyValue = data.planId === 1 ? 27.90 : 37.90; // Individual vs Familiar
        totalAmount = (monthlyValue * data.installments) + parseFloat(plan.adhesionFee);
      } else if (data.paymentMethod === 'credit' && data.installments > 1) {
        // Credit card pricing for installments  
        const monthlyValue = parseFloat(plan.monthlyPrice || "0");
        totalAmount = (monthlyValue * data.installments) + parseFloat(plan.adhesionFee);
      }

      // Create subscription
      const expiresAt = new Date();
      expiresAt.setFullYear(expiresAt.getFullYear() + 1); // 1 year from now

      const subscription = await storage.createSubscription({
        customerId: customer.id,
        planId: data.planId,
        paymentMethod: data.paymentMethod,
        totalAmount: totalAmount.toFixed(2),
        installments: data.installments,
        expiresAt,
      });

      // Simulate payment processing
      const paymentSuccess = await processPayment(subscription, data.paymentMethod);
      
      if (paymentSuccess) {
        await storage.updateSubscriptionStatus(subscription.id, 'paid');
        
        // Generate digital card
        const cardNumber = generateCardNumber();
        const qrCode = generateQRCode(subscription.id, customer.id);
        
        const digitalCard = await storage.createDigitalCard({
          subscriptionId: subscription.id,
          cardNumber,
          qrCode,
        });

        res.json({
          success: true,
          subscription,
          digitalCard,
          customer,
          plan,
        });
      } else {
        await storage.updateSubscriptionStatus(subscription.id, 'failed');
        res.status(400).json({ message: "Falha no processamento do pagamento" });
      }

    } catch (error) {
      console.error("Error creating subscription:", error);
      if (error instanceof z.ZodError) {
        res.status(400).json({ message: "Dados inválidos", errors: error.errors });
      } else {
        res.status(500).json({ message: "Erro interno do servidor" });
      }
    }
  });

  // Get subscription details
  app.get("/api/subscriptions/:id", async (req, res) => {
    try {
      const id = parseInt(req.params.id);
      const subscription = await storage.getSubscriptionById(id);
      
      if (!subscription) {
        return res.status(404).json({ message: "Assinatura não encontrada" });
      }

      const digitalCard = await storage.getDigitalCardBySubscription(id);
      
      res.json({
        subscription,
        digitalCard,
      });
    } catch (error) {
      console.error("Error fetching subscription:", error);
      res.status(500).json({ message: "Erro ao buscar assinatura" });
    }
  });

  // WhatsApp integration endpoint for enterprise plans
  app.post("/api/whatsapp/enterprise", async (req, res) => {
    try {
      const { name, email, phone, companyName, employeeCount } = req.body;
      
      // Format WhatsApp message
      const message = `Olá! Gostaria de informações sobre o plano empresarial.%0A%0A` +
        `Nome: ${name}%0A` +
        `Email: ${email}%0A` +
        `Telefone: ${phone}%0A` +
        `Empresa: ${companyName}%0A` +
        `Número de colaboradores: ${employeeCount}`;
      
      const whatsappUrl = `https://wa.me/5516993247676?text=${message}`;
      
      res.json({ whatsappUrl });
    } catch (error) {
      console.error("Error generating WhatsApp URL:", error);
      res.status(500).json({ message: "Erro ao gerar link do WhatsApp" });
    }
  });

  // JWT secret for admin authentication
  const JWT_SECRET = process.env.JWT_SECRET || "your-secret-key-here";

  // Enhanced admin authentication middleware
  const authenticateAdmin = (req: Request & { user?: any }, res: Response, next: NextFunction) => {
    const authHeader = req.headers.authorization;
    
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return res.status(401).json({ error: "Access denied. Invalid authorization header." });
    }

    const token = authHeader.split(' ')[1];

    try {
      const decoded = jwt.verify(token, JWT_SECRET) as any;
      
      // Verify token contains required fields
      if (!decoded.id || !decoded.username) {
        return res.status(401).json({ error: "Invalid token payload." });
      }
      
      // Check token expiration
      if (decoded.exp && Date.now() >= decoded.exp * 1000) {
        return res.status(401).json({ error: "Token expired." });
      }
      
      req.user = decoded;
      next();
    } catch (error) {
      console.error('JWT verification error:', error);
      return res.status(401).json({ error: "Invalid or expired token." });
    }
  };

  // Admin login route with enhanced security
  app.post("/api/admin/login", 
    loginLimiter,
    sanitizeInput,
    [
      body('username')
        .isLength({ min: 3, max: 50 })
        .trim()
        .escape()
        .matches(/^[a-zA-Z0-9_-]+$/)
        .withMessage('Username must contain only alphanumeric characters, underscores, and hyphens'),
      body('password')
        .isLength({ min: 6, max: 100 })
        .withMessage('Password must be between 6 and 100 characters')
    ],
    validateRequest,
    async (req, res) => {
    try {
      const { username, password } = req.body;
      
      // Additional security checks
      if (!username || !password || typeof username !== 'string' || typeof password !== 'string') {
        return res.status(400).json({ error: "Invalid input format" });
      }

      // Log login attempt for security monitoring
      console.log(`[Security] Login attempt for username: ${username} from IP: ${req.ip}`);

      const isValid = await storage.verifyAdminPassword(username, password);
      
      if (!isValid) {
        console.log(`[Security] Failed login attempt for username: ${username} from IP: ${req.ip}`);
        return res.status(401).json({ error: "Invalid credentials" });
      }

      const admin = await storage.getAdminByUsername(username);
      if (!admin || !admin.isActive) {
        console.log(`[Security] Login attempt for inactive user: ${username} from IP: ${req.ip}`);
        return res.status(401).json({ error: "Account not active" });
      }

      // Generate secure JWT token
      const token = jwt.sign(
        { 
          id: admin.id, 
          username: admin.username,
          iat: Math.floor(Date.now() / 1000),
          exp: Math.floor(Date.now() / 1000) + (2 * 60 * 60) // 2 hours
        },
        JWT_SECRET,
        { algorithm: 'HS256' }
      );

      res.json({
        token,
        user: {
          id: admin.id,
          username: admin.username,
          email: admin.email
        }
      });
    } catch (error) {
      console.error("Error during admin login:", error);
      res.status(500).json({ message: "Erro interno do servidor" });
    }
  });

  // Create admin user (only for initial setup)
  app.post("/api/admin/create", async (req, res) => {
    try {
      const adminData = insertAdminUserSchema.parse(req.body);
      
      // Check if admin already exists
      const existing = await storage.getAdminByUsername(adminData.username);
      if (existing) {
        return res.status(400).json({ message: "Usuário administrador já existe" });
      }

      const admin = await storage.createAdminUser(adminData);
      
      res.status(201).json({
        message: "Administrador criado com sucesso",
        user: {
          id: admin.id,
          username: admin.username,
          email: admin.email
        }
      });
    } catch (error) {
      console.error("Error creating admin:", error);
      res.status(500).json({ message: "Erro ao criar administrador" });
    }
  });

  // Track WhatsApp conversion with enhanced security
  app.post("/api/whatsapp/track", 
    sanitizeInput,
    [
      body('phone')
        .optional()
        .matches(/^[\d\s\-\+\(\)]+$/)
        .isLength({ max: 20 })
        .withMessage('Invalid phone format'),
      body('name')
        .optional()
        .trim()
        .isLength({ max: 100 })
        .matches(/^[a-zA-ZÀ-ÿ\s]+$/)
        .withMessage('Name must contain only letters and spaces'),
      body('email')
        .optional()
        .isEmail()
        .normalizeEmail()
        .isLength({ max: 100 })
        .withMessage('Invalid email format'),
      body('buttonType')
        .isIn(['plan_subscription', 'doctor_appointment', 'enterprise_quote'])
        .withMessage('Invalid button type'),
      body('planName')
        .optional()
        .trim()
        .isLength({ max: 100 })
        .withMessage('Plan name too long'),
      body('doctorName')
        .optional()
        .trim()
        .isLength({ max: 100 })
        .withMessage('Doctor name too long')
    ],
    validateRequest,
    async (req, res) => {
    try {
      const conversionData = insertWhatsappConversionSchema.parse(req.body);
      
      // Add security tracking info with length limits
      const ipAddress = req.ip || req.connection.remoteAddress;
      const userAgent = req.headers['user-agent']?.substring(0, 500); // Limit user agent length
      
      const conversion = await storage.createWhatsappConversion({
        ...conversionData,
        ipAddress,
        userAgent
      });

      res.status(201).json({ message: "Conversão registrada", id: conversion.id });
    } catch (error) {
      console.error("Error tracking conversion:", error);
      res.status(500).json({ message: "Erro ao registrar conversão" });
    }
  });

  // Get all WhatsApp conversions (admin only) with enhanced security
  app.get("/api/admin/conversions", 
    authenticateAdmin,
    [
      param('startDate').optional().isISO8601().withMessage('Invalid start date format'),
      param('endDate').optional().isISO8601().withMessage('Invalid end date format')
    ],
    async (req: Request, res: Response) => {
    try {
      const { startDate, endDate } = req.query;
      
      // Validate date range
      if (startDate && endDate) {
        const start = new Date(startDate as string);
        const end = new Date(endDate as string);
        
        if (start > end) {
          return res.status(400).json({ error: "Start date cannot be after end date" });
        }
        
        // Limit date range to prevent excessive queries
        const daysDiff = (end.getTime() - start.getTime()) / (1000 * 3600 * 24);
        if (daysDiff > 365) {
          return res.status(400).json({ error: "Date range cannot exceed 365 days" });
        }
      }
      
      let conversions;
      if (startDate && endDate) {
        conversions = await storage.getWhatsappConversionsByDateRange(
          new Date(startDate as string),
          new Date(endDate as string)
        );
      } else {
        conversions = await storage.getAllWhatsappConversions();
      }

      // Limit response size for performance
      if (conversions.length > 10000) {
        return res.status(413).json({ 
          error: "Result set too large. Please use date filters to narrow your search." 
        });
      }

      res.json(conversions);
    } catch (error) {
      console.error("Error fetching conversions:", error);
      res.status(500).json({ error: "Failed to fetch conversions" });
    }
  });

  // Export conversions as CSV for marketing campaigns (admin only)
  app.get("/api/admin/conversions/export", authenticateAdmin, async (req, res) => {
    try {
      const { startDate, endDate } = req.query;
      
      let conversions;
      if (startDate && endDate) {
        conversions = await storage.getWhatsappConversionsByDateRange(
          new Date(startDate as string),
          new Date(endDate as string)
        );
      } else {
        conversions = await storage.getAllWhatsappConversions();
      }

      // Generate CSV content compatible with Google/Facebook Ads
      const csvHeader = "Email,Phone,First_Name,Last_Name,Full_Name,Interest_Category,Product_Interest,Lead_Source,Campaign_Type,IP_Address,Conversion_Date,Lead_ID\n";
      const csvRows = conversions.map(conv => {
        const fullName = conv.name || '';
        const nameParts = fullName.split(' ');
        const firstName = nameParts[0] || '';
        const lastName = nameParts.slice(1).join(' ') || '';
        
        // Map button types to marketing categories
        const interestCategory = conv.buttonType === 'plan_subscription' ? 'Health_Plans' : 
                                conv.buttonType === 'doctor_appointment' ? 'Medical_Consultation' : 
                                'Enterprise_Solutions';
        
        const productInterest = conv.planName || conv.doctorName || 'General_Inquiry';
        const campaignType = conv.buttonType === 'plan_subscription' ? 'Plan_Conversion' : 
                            conv.buttonType === 'doctor_appointment' ? 'Appointment_Request' : 
                            'B2B_Quote';
        
        // Format phone for ads (remove special characters)
        const cleanPhone = (conv.phone || '').replace(/[^\d]/g, '');
        
        return `"${conv.email || ''}","${cleanPhone}","${firstName}","${lastName}","${fullName}","${interestCategory}","${productInterest}","Website","${campaignType}","${conv.ipAddress || ''}","${conv.createdAt}","${conv.id}"`;
      }).join('\n');
      
      const csv = csvHeader + csvRows;
      
      res.setHeader('Content-Type', 'text/csv');
      res.setHeader('Content-Disposition', 'attachment; filename="leads-marketing-digital.csv"');
      res.send(csv);
    } catch (error) {
      console.error("Error exporting conversions:", error);
      res.status(500).json({ message: "Erro ao exportar conversões" });
    }
  });

  // Export conversions as CSV for internal management (admin only)
  app.get("/api/admin/conversions/export-internal", authenticateAdmin, async (req, res) => {
    try {
      const { startDate, endDate } = req.query;
      
      let conversions;
      if (startDate && endDate) {
        conversions = await storage.getWhatsappConversionsByDateRange(
          new Date(startDate as string),
          new Date(endDate as string)
        );
      } else {
        conversions = await storage.getAllWhatsappConversions();
      }

      // Generate CSV content for internal management
      const csvHeader = "ID,Nome,Email,Telefone,Tipo,Plano,Médico,IP,User_Agent,Data\n";
      const csvRows = conversions.map(conv => 
        `${conv.id},"${conv.name || ''}","${conv.email || ''}","${conv.phone || ''}","${conv.buttonType}","${conv.planName || ''}","${conv.doctorName || ''}","${conv.ipAddress || ''}","${conv.userAgent || ''}","${conv.createdAt}"`
      ).join('\n');
      
      const csv = csvHeader + csvRows;
      
      res.setHeader('Content-Type', 'text/csv');
      res.setHeader('Content-Disposition', 'attachment; filename="gestao-interna-leads.csv"');
      res.send(csv);
    } catch (error) {
      console.error("Error exporting conversions:", error);
      res.status(500).json({ message: "Erro ao exportar conversões" });
    }
  });

  const httpServer = createServer(app);
  return httpServer;
}

// Helper functions
async function processPayment(subscription: any, paymentMethod: string): Promise<boolean> {
  // Simulate payment processing
  // In production, integrate with actual payment gateway
  return new Promise((resolve) => {
    setTimeout(() => {
      // Simulate 95% success rate
      resolve(Math.random() > 0.05);
    }, 1000);
  });
}

function generateCardNumber(): string {
  // Generate a unique card number
  const timestamp = Date.now().toString();
  const random = Math.random().toString(36).substring(2, 8).toUpperCase();
  return `VIDAH${timestamp.slice(-6)}${random}`;
}

function generateQRCode(subscriptionId: number, customerId: number): string {
  // Generate QR code data - in production this would create actual QR code
  const qrData = `VIDAH:${subscriptionId}:${customerId}:${Date.now()}`;
  return Buffer.from(qrData).toString('base64');
}
