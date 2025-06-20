import type { Request, Response } from "express";
import { storage } from "../storage";
import { ApiResponse } from "@shared/types";

export class PlanController {
  static async getAllPlans(req: Request, res: Response) {
    try {
      const plans = await storage.getAllPlans();
      
      const response: ApiResponse = {
        success: true,
        data: plans
      };
      
      res.json(response);
    } catch (error) {
      console.error("[PlanController] Error fetching plans:", error);
      
      const response: ApiResponse = {
        success: false,
        error: "Erro ao buscar planos disponíveis"
      };
      
      res.status(500).json(response);
    }
  }

  static async getPlanById(req: Request, res: Response) {
    try {
      const planId = parseInt(req.params.id);
      
      if (isNaN(planId) || planId <= 0) {
        const response: ApiResponse = {
          success: false,
          error: "ID do plano inválido"
        };
        return res.status(400).json(response);
      }

      const plan = await storage.getPlanById(planId);
      
      if (!plan) {
        const response: ApiResponse = {
          success: false,
          error: "Plano não encontrado"
        };
        return res.status(404).json(response);
      }

      const response: ApiResponse = {
        success: true,
        data: plan
      };
      
      res.json(response);
    } catch (error) {
      console.error("[PlanController] Error fetching plan:", error);
      
      const response: ApiResponse = {
        success: false,
        error: "Erro ao buscar plano"
      };
      
      res.status(500).json(response);
    }
  }
}