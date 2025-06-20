import { customers, subscriptions, digitalCards, plans, adminUsers, whatsappConversions, type Customer, type InsertCustomer, type Subscription, type InsertSubscription, type DigitalCard, type InsertDigitalCard, type Plan, users, type User, type InsertUser, type AdminUser, type InsertAdminUser, type WhatsappConversion, type InsertWhatsappConversion } from "@shared/schema";
import { db } from "./db";
import { eq, and, gte, lte } from "drizzle-orm";
import bcrypt from "bcrypt";

export interface IStorage {
  getUser(id: number): Promise<User | undefined>;
  getUserByUsername(username: string): Promise<User | undefined>;
  createUser(user: InsertUser): Promise<User>;
  
  createCustomer(customer: InsertCustomer): Promise<Customer>;
  getCustomerByEmail(email: string): Promise<Customer | undefined>;
  getCustomerByCpf(cpf: string): Promise<Customer | undefined>;
  
  getAllPlans(): Promise<Plan[]>;
  getPlanById(id: number): Promise<Plan | undefined>;
  
  createSubscription(subscription: InsertSubscription): Promise<Subscription>;
  getSubscriptionById(id: number): Promise<Subscription | undefined>;
  updateSubscriptionStatus(id: number, status: string): Promise<Subscription | undefined>;
  
  createDigitalCard(card: InsertDigitalCard): Promise<DigitalCard>;
  getDigitalCardBySubscription(subscriptionId: number): Promise<DigitalCard | undefined>;

  // Admin management
  createAdminUser(admin: InsertAdminUser): Promise<AdminUser>;
  getAdminByUsername(username: string): Promise<AdminUser | undefined>;
  verifyAdminPassword(username: string, password: string): Promise<boolean>;

  // WhatsApp conversion tracking
  createWhatsappConversion(conversion: InsertWhatsappConversion): Promise<WhatsappConversion>;
  getAllWhatsappConversions(): Promise<WhatsappConversion[]>;
  getWhatsappConversionsByDateRange(startDate: Date, endDate: Date): Promise<WhatsappConversion[]>;
}

export class DatabaseStorage implements IStorage {
  constructor() {
    this.initializePlans();
  }

  private async initializePlans() {
    try {
      const existingPlans = await db.select().from(plans);
      if (existingPlans.length === 0) {
        await db.insert(plans).values([
          {
            id: 1,
            name: "Cartão Familiar",
            type: "familiar",
            annualPrice: "418.80",
            monthlyPrice: "34.90",
            adhesionFee: "0",
            maxDependents: 4,
            isActive: true,
          },
          {
            id: 2,
            name: "Cartão Corporativo",
            type: "empresarial",
            annualPrice: "0",
            monthlyPrice: "0",
            adhesionFee: "0",
            maxDependents: 0,
            isActive: true,
          }
        ]);
      }
    } catch (error) {
      console.error("Error initializing plans:", error);
    }
  }

  async getUser(id: number): Promise<User | undefined> {
    const [user] = await db.select().from(users).where(eq(users.id, id));
    return user;
  }

  async getUserByUsername(username: string): Promise<User | undefined> {
    const [user] = await db.select().from(users).where(eq(users.username, username));
    return user;
  }

  async createUser(insertUser: InsertUser): Promise<User> {
    const hashedPassword = await bcrypt.hash(insertUser.password, 10);
    const [user] = await db
      .insert(users)
      .values({ ...insertUser, password: hashedPassword })
      .returning();
    return user;
  }

  async createCustomer(insertCustomer: InsertCustomer): Promise<Customer> {
    const [customer] = await db
      .insert(customers)
      .values(insertCustomer)
      .returning();
    return customer;
  }

  async getCustomerByEmail(email: string): Promise<Customer | undefined> {
    const [customer] = await db.select().from(customers).where(eq(customers.email, email));
    return customer;
  }

  async getCustomerByCpf(cpf: string): Promise<Customer | undefined> {
    const [customer] = await db.select().from(customers).where(eq(customers.cpf, cpf));
    return customer;
  }

  async getAllPlans(): Promise<Plan[]> {
    return await db.select().from(plans).where(eq(plans.isActive, true));
  }

  async getPlanById(id: number): Promise<Plan | undefined> {
    const [plan] = await db.select().from(plans).where(eq(plans.id, id));
    return plan;
  }

  async createSubscription(insertSubscription: InsertSubscription): Promise<Subscription> {
    const [subscription] = await db
      .insert(subscriptions)
      .values(insertSubscription)
      .returning();
    return subscription;
  }

  async getSubscriptionById(id: number): Promise<Subscription | undefined> {
    const [subscription] = await db.select().from(subscriptions).where(eq(subscriptions.id, id));
    return subscription;
  }

  async updateSubscriptionStatus(id: number, status: string): Promise<Subscription | undefined> {
    const [subscription] = await db
      .update(subscriptions)
      .set({ paymentStatus: status })
      .where(eq(subscriptions.id, id))
      .returning();
    return subscription;
  }

  async createDigitalCard(insertCard: InsertDigitalCard): Promise<DigitalCard> {
    const [card] = await db
      .insert(digitalCards)
      .values(insertCard)
      .returning();
    return card;
  }

  async getDigitalCardBySubscription(subscriptionId: number): Promise<DigitalCard | undefined> {
    const [card] = await db.select().from(digitalCards).where(eq(digitalCards.subscriptionId, subscriptionId));
    return card;
  }

  // Admin management methods
  async createAdminUser(insertAdmin: InsertAdminUser): Promise<AdminUser> {
    const hashedPassword = await bcrypt.hash(insertAdmin.password, 10);
    const [admin] = await db
      .insert(adminUsers)
      .values({ ...insertAdmin, password: hashedPassword })
      .returning();
    return admin;
  }

  async getAdminByUsername(username: string): Promise<AdminUser | undefined> {
    const [admin] = await db.select().from(adminUsers).where(eq(adminUsers.username, username));
    return admin;
  }

  async verifyAdminPassword(username: string, password: string): Promise<boolean> {
    const admin = await this.getAdminByUsername(username);
    if (!admin) return false;
    return await bcrypt.compare(password, admin.password);
  }

  // WhatsApp conversion tracking methods
  async createWhatsappConversion(insertConversion: InsertWhatsappConversion): Promise<WhatsappConversion> {
    const [conversion] = await db
      .insert(whatsappConversions)
      .values(insertConversion)
      .returning();
    return conversion;
  }

  async getAllWhatsappConversions(): Promise<WhatsappConversion[]> {
    return await db.select().from(whatsappConversions).orderBy(whatsappConversions.createdAt);
  }

  async getWhatsappConversionsByDateRange(startDate: Date, endDate: Date): Promise<WhatsappConversion[]> {
    return await db
      .select()
      .from(whatsappConversions)
      .where(
        and(
          gte(whatsappConversions.createdAt, startDate),
          lte(whatsappConversions.createdAt, endDate)
        )
      )
      .orderBy(whatsappConversions.createdAt);
  }
}

export const storage = new DatabaseStorage();