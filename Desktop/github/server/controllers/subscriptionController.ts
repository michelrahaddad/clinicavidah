import type { Request, Response } from "express";
import { storage } from "../storage";
import { subscriptionRequestSchema } from "@shared/validation";
import { ApiResponse, SubscriptionResponse, ValidationError, NotFoundError } from "@shared/types";
import { z } from "zod";

export class SubscriptionController {
  static async createSubscription(req: Request, res: Response) {
    try {
      // Validate request data
      const validatedData = subscriptionRequestSchema.parse(req.body);
      
      // Check if customer already exists by email
      let customer = await storage.getCustomerByEmail(validatedData.customer.email);
      
      if (!customer) {
        // Check CPF uniqueness
        const existingCpf = await storage.getCustomerByCpf(validatedData.customer.cpf);
        if (existingCpf) {
          const response: ApiResponse = {
            success: false,
            error: "CPF já cadastrado no sistema"
          };
          return res.status(400).json(response);
        }
        
        // Create new customer
        customer = await storage.createCustomer(validatedData.customer);
      }

      // Get plan details
      const plan = await storage.getPlanById(validatedData.planId);
      if (!plan) {
        throw new NotFoundError("Plano não encontrado");
      }

      // Calculate total amount
      const totalAmount = SubscriptionController.calculateTotalAmount(
        plan, 
        validatedData.paymentMethod, 
        validatedData.installments || 1
      );

      // Create subscription
      const expiresAt = new Date();
      expiresAt.setFullYear(expiresAt.getFullYear() + 1);

      const subscription = await storage.createSubscription({
        customerId: customer.id,
        planId: validatedData.planId,
        paymentMethod: validatedData.paymentMethod,
        totalAmount: totalAmount.toFixed(2),
        installments: validatedData.installments || 1,
        expiresAt,
      });

      // Process payment
      const paymentSuccess = await SubscriptionController.processPayment(
        subscription, 
        validatedData.paymentMethod
      );

      if (paymentSuccess) {
        await storage.updateSubscriptionStatus(subscription.id, 'paid');
        
        // Generate digital card
        const digitalCard = await SubscriptionController.generateDigitalCard(subscription.id);

        const response: SubscriptionResponse = {
          success: true,
          subscription,
          digitalCard: digitalCard ? {
            id: digitalCard.id,
            cardNumber: digitalCard.cardNumber,
            qrCode: digitalCard.qrCode,
            isActive: digitalCard.isActive ?? true,
          } : undefined,
          customer,
          plan: {
            id: plan.id,
            name: plan.name,
            type: plan.type as 'individual' | 'familiar' | 'empresarial',
            annualPrice: parseFloat(plan.annualPrice),
            monthlyPrice: plan.monthlyPrice ? parseFloat(plan.monthlyPrice) : undefined,
            adhesionFee: parseFloat(plan.adhesionFee),
            maxDependents: plan.maxDependents || 0,
            description: plan.description || undefined,
            features: plan.features || undefined,
          }
        };

        res.json(response);
      } else {
        await storage.updateSubscriptionStatus(subscription.id, 'failed');
        
        const response: ApiResponse = {
          success: false,
          error: "Falha no processamento do pagamento"
        };
        
        res.status(400).json(response);
      }

    } catch (error) {
      console.error("[SubscriptionController] Error creating subscription:", error);
      
      if (error instanceof z.ZodError) {
        const response: ApiResponse = {
          success: false,
          error: "Dados inválidos fornecidos",
          message: error.errors.map(e => `${e.path.join('.')}: ${e.message}`).join(', ')
        };
        return res.status(400).json(response);
      }
      
      if (error instanceof ValidationError) {
        const response: ApiResponse = {
          success: false,
          error: error.message
        };
        return res.status(400).json(response);
      }
      
      if (error instanceof NotFoundError) {
        const response: ApiResponse = {
          success: false,
          error: error.message
        };
        return res.status(404).json(response);
      }

      const response: ApiResponse = {
        success: false,
        error: "Erro interno do servidor"
      };
      
      res.status(500).json(response);
    }
  }

  static async getSubscription(req: Request, res: Response) {
    try {
      const subscriptionId = parseInt(req.params.id);
      
      if (isNaN(subscriptionId) || subscriptionId <= 0) {
        const response: ApiResponse = {
          success: false,
          error: "ID da assinatura inválido"
        };
        return res.status(400).json(response);
      }

      const subscription = await storage.getSubscriptionById(subscriptionId);
      
      if (!subscription) {
        const response: ApiResponse = {
          success: false,
          error: "Assinatura não encontrada"
        };
        return res.status(404).json(response);
      }

      const digitalCard = await storage.getDigitalCardBySubscription(subscriptionId);
      
      const response: ApiResponse = {
        success: true,
        data: {
          subscription,
          digitalCard
        }
      };
      
      res.json(response);
    } catch (error) {
      console.error("[SubscriptionController] Error fetching subscription:", error);
      
      const response: ApiResponse = {
        success: false,
        error: "Erro ao buscar assinatura"
      };
      
      res.status(500).json(response);
    }
  }

  private static calculateTotalAmount(
    plan: any, 
    paymentMethod: string, 
    installments: number
  ): number {
    let totalAmount = parseFloat(plan.annualPrice) + parseFloat(plan.adhesionFee);
    
    if (paymentMethod === 'pix') {
      // 10% discount for PIX
      totalAmount = (parseFloat(plan.annualPrice) * 0.9) + parseFloat(plan.adhesionFee);
    } else if (paymentMethod === 'boleto' && installments > 1) {
      // Boleto pricing for installments
      const monthlyValue = plan.id === 1 ? 27.90 : 37.90;
      totalAmount = (monthlyValue * installments) + parseFloat(plan.adhesionFee);
    } else if (paymentMethod === 'credit' && installments > 1) {
      // Credit card pricing for installments
      const monthlyValue = parseFloat(plan.monthlyPrice || "0");
      totalAmount = (monthlyValue * installments) + parseFloat(plan.adhesionFee);
    }
    
    return totalAmount;
  }

  private static async processPayment(subscription: any, paymentMethod: string): Promise<boolean> {
    // Simulate payment processing - in production, integrate with real payment gateway
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    const successRates = {
      pix: 0.95,
      credit: 0.92,
      boleto: 0.98
    };
    
    const successRate = successRates[paymentMethod as keyof typeof successRates] || 0.9;
    return Math.random() < successRate;
  }

  private static async generateDigitalCard(subscriptionId: number) {
    const cardNumber = SubscriptionController.generateCardNumber();
    const qrCode = SubscriptionController.generateQRCode(subscriptionId);
    
    return await storage.createDigitalCard({
      subscriptionId,
      cardNumber,
      qrCode,
    });
  }

  private static generateCardNumber(): string {
    const timestamp = Date.now().toString();
    const random = Math.floor(Math.random() * 10000).toString().padStart(4, '0');
    return `5454${timestamp.slice(-6)}${random}`;
  }

  private static generateQRCode(subscriptionId: number): string {
    const data = {
      subscriptionId,
      timestamp: Date.now(),
      version: "1.0"
    };
    return Buffer.from(JSON.stringify(data)).toString('base64');
  }
}