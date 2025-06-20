import type { Request, Response, NextFunction } from "express";
import jwt from "jsonwebtoken";
import { storage } from "../storage";
import { UnauthorizedError } from "@shared/types";

const JWT_SECRET = process.env.JWT_SECRET || "your-super-secure-secret-key-change-in-production";

export interface AuthenticatedRequest extends Request {
  user?: {
    id: number;
    username: string;
  };
}

export const authenticateAdmin = async (
  req: AuthenticatedRequest, 
  res: Response, 
  next: NextFunction
) => {
  try {
    const authHeader = req.headers.authorization;
    
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return res.status(401).json({ 
        success: false, 
        error: "Token de acesso obrigatório" 
      });
    }

    const token = authHeader.split(' ')[1];
    const decoded = jwt.verify(token, JWT_SECRET) as any;
    
    if (!decoded.id || !decoded.username) {
      return res.status(401).json({ 
        success: false, 
        error: "Token inválido" 
      });
    }
    
    if (decoded.exp && Date.now() >= decoded.exp * 1000) {
      return res.status(401).json({ 
        success: false, 
        error: "Token expirado" 
      });
    }

    const admin = await storage.getAdminByUsername(decoded.username);
    if (!admin || !admin.isActive) {
      return res.status(401).json({ 
        success: false, 
        error: "Usuário não autorizado" 
      });
    }
    
    req.user = {
      id: admin.id,
      username: admin.username
    };
    
    next();
  } catch (error) {
    console.error('[Auth] JWT verification error:', error);
    return res.status(401).json({ 
      success: false, 
      error: "Token inválido ou expirado" 
    });
  }
};