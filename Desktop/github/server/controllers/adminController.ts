import type { Request, Response } from "express";
import { storage } from "../storage";
import { adminLoginSchema } from "@shared/validation";
import { ApiResponse, UnauthorizedError } from "@shared/types";
import jwt from "jsonwebtoken";
import { z } from "zod";

const JWT_SECRET = process.env.JWT_SECRET || "your-super-secure-secret-key-change-in-production";

export class AdminController {
  static async login(req: Request, res: Response) {
    try {
      const validatedData = adminLoginSchema.parse(req.body);
      
      console.log(`[Security] Login attempt for username: ${validatedData.username} from IP: ${req.ip}`);

      const isValid = await storage.verifyAdminPassword(validatedData.username, validatedData.password);
      
      if (!isValid) {
        console.log(`[Security] Failed login attempt for username: ${validatedData.username} from IP: ${req.ip}`);
        
        const response: ApiResponse = {
          success: false,
          error: "Credenciais inválidas"
        };
        return res.status(401).json(response);
      }

      const admin = await storage.getAdminByUsername(validatedData.username);
      if (!admin || !admin.isActive) {
        console.log(`[Security] Login attempt for inactive user: ${validatedData.username} from IP: ${req.ip}`);
        
        const response: ApiResponse = {
          success: false,
          error: "Conta não está ativa"
        };
        return res.status(401).json(response);
      }

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

      console.log(`[Security] Successful login for username: ${validatedData.username} from IP: ${req.ip}`);

      // Frontend expects token and user in root level
      res.json({
        token,
        user: {
          id: admin.id,
          username: admin.username,
          email: admin.email
        }
      });
    } catch (error) {
      console.error("[AdminController] Login error:", error);
      
      if (error instanceof z.ZodError) {
        const response: ApiResponse = {
          success: false,
          error: "Dados de login inválidos",
          message: error.errors.map(e => `${e.path.join('.')}: ${e.message}`).join(', ')
        };
        return res.status(400).json(response);
      }

      const response: ApiResponse = {
        success: false,
        error: "Erro interno do servidor"
      };
      
      res.status(500).json(response);
    }
  }

  static async verifyToken(req: Request, res: Response) {
    try {
      const authHeader = req.headers.authorization;
      
      if (!authHeader || !authHeader.startsWith('Bearer ')) {
        throw new UnauthorizedError("Token de acesso inválido");
      }

      const token = authHeader.split(' ')[1];
      const decoded = jwt.verify(token, JWT_SECRET) as any;
      
      if (!decoded.id || !decoded.username) {
        throw new UnauthorizedError("Token inválido");
      }
      
      if (decoded.exp && Date.now() >= decoded.exp * 1000) {
        throw new UnauthorizedError("Token expirado");
      }

      const admin = await storage.getAdminByUsername(decoded.username);
      if (!admin || !admin.isActive) {
        throw new UnauthorizedError("Usuário não autorizado");
      }

      const response: ApiResponse = {
        success: true,
        data: {
          admin: {
            id: admin.id,
            username: admin.username,
            email: admin.email,
            isActive: admin.isActive
          }
        }
      };

      res.json(response);
    } catch (error) {
      console.error("[AdminController] Token verification error:", error);
      
      if (error instanceof UnauthorizedError) {
        const response: ApiResponse = {
          success: false,
          error: error.message
        };
        return res.status(401).json(response);
      }

      const response: ApiResponse = {
        success: false,
        error: "Erro de autenticação"
      };
      
      res.status(401).json(response);
    }
  }

  static async getDashboardStats(req: Request, res: Response) {
    try {
      const conversions = await storage.getAllWhatsappConversions();
      
      const today = new Date();
      const lastWeek = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000);
      const lastMonth = new Date(today.getTime() - 30 * 24 * 60 * 60 * 1000);
      
      const stats = {
        total: conversions.length,
        today: conversions.filter(c => c.createdAt && new Date(c.createdAt).toDateString() === today.toDateString()).length,
        thisWeek: conversions.filter(c => c.createdAt && new Date(c.createdAt) >= lastWeek).length,
        thisMonth: conversions.filter(c => c.createdAt && new Date(c.createdAt) >= lastMonth).length,
        byType: {
          plan_subscription: conversions.filter(c => c.buttonType === 'plan_subscription').length,
          doctor_appointment: conversions.filter(c => c.buttonType === 'doctor_appointment').length,
          enterprise_quote: conversions.filter(c => c.buttonType === 'enterprise_quote').length,
        },
        recentConversions: conversions
          .sort((a, b) => new Date(b.createdAt!).getTime() - new Date(a.createdAt!).getTime())
          .slice(0, 10)
      };

      const response: ApiResponse = {
        success: true,
        data: stats
      };

      res.json(response);
    } catch (error) {
      console.error("[AdminController] Dashboard stats error:", error);
      
      const response: ApiResponse = {
        success: false,
        error: "Erro ao buscar estatísticas"
      };
      
      res.status(500).json(response);
    }
  }
}