import { pgTable, text, serial, integer, boolean, timestamp, decimal } from "drizzle-orm/pg-core";
import { createInsertSchema } from "drizzle-zod";
import { z } from "zod";
import { relations } from "drizzle-orm";

export const users = pgTable("users", {
  id: serial("id").primaryKey(),
  username: text("username").notNull().unique(),
  password: text("password").notNull(),
});

export const customers = pgTable("customers", {
  id: serial("id").primaryKey(),
  name: text("name").notNull(),
  email: text("email").notNull().unique(),
  cpf: text("cpf").notNull().unique(),
  phone: text("phone").notNull(),
  createdAt: timestamp("created_at").defaultNow().notNull(),
});

export const plans = pgTable("plans", {
  id: serial("id").primaryKey(),
  name: text("name").notNull(),
  type: text("type").notNull(), // 'individual', 'familiar', 'empresarial'
  annualPrice: decimal("annual_price", { precision: 10, scale: 2 }).notNull(),
  monthlyPrice: decimal("monthly_price", { precision: 10, scale: 2 }),
  adhesionFee: decimal("adhesion_fee", { precision: 10, scale: 2 }).notNull(),
  maxDependents: integer("max_dependents").default(0),
  description: text("description"),
  features: text("features").array(),
  isActive: boolean("is_active").default(true),
  createdAt: timestamp("created_at").defaultNow().notNull(),
  updatedAt: timestamp("updated_at").defaultNow().notNull(),
});

export const subscriptions = pgTable("subscriptions", {
  id: serial("id").primaryKey(),
  customerId: integer("customer_id").references(() => customers.id).notNull(),
  planId: integer("plan_id").references(() => plans.id).notNull(),
  paymentMethod: text("payment_method").notNull(), // 'pix', 'credit', 'boleto'
  paymentStatus: text("payment_status").notNull().default('pending'), // 'pending', 'paid', 'failed'
  totalAmount: decimal("total_amount", { precision: 10, scale: 2 }).notNull(),
  installments: integer("installments").notNull().default(1),
  createdAt: timestamp("created_at").defaultNow().notNull(),
  expiresAt: timestamp("expires_at").notNull(),
});

export const digitalCards = pgTable("digital_cards", {
  id: serial("id").primaryKey(),
  subscriptionId: integer("subscription_id").references(() => subscriptions.id).notNull(),
  cardNumber: text("card_number").notNull().unique(),
  qrCode: text("qr_code").notNull(),
  isActive: boolean("is_active").default(true),
  createdAt: timestamp("created_at").defaultNow().notNull(),
});

export const adminUsers = pgTable("admin_users", {
  id: serial("id").primaryKey(),
  username: text("username").notNull().unique(),
  password: text("password").notNull(),
  email: text("email").notNull().unique(),
  isActive: boolean("is_active").default(true),
  createdAt: timestamp("created_at").defaultNow().notNull(),
});

export const whatsappConversions = pgTable("whatsapp_conversions", {
  id: serial("id").primaryKey(),
  phone: text("phone"),
  name: text("name"),
  email: text("email"),
  buttonType: text("button_type").notNull(), // 'plan_subscription', 'doctor_appointment', 'enterprise_quote'
  planName: text("plan_name"),
  doctorName: text("doctor_name"),
  ipAddress: text("ip_address"),
  userAgent: text("user_agent"),
  createdAt: timestamp("created_at").defaultNow().notNull(),
});

export const insertCustomerSchema = createInsertSchema(customers).pick({
  name: true,
  email: true,
  cpf: true,
  phone: true,
});

export const insertSubscriptionSchema = createInsertSchema(subscriptions).pick({
  customerId: true,
  planId: true,
  paymentMethod: true,
  totalAmount: true,
  installments: true,
  expiresAt: true,
});

export const insertDigitalCardSchema = createInsertSchema(digitalCards).pick({
  subscriptionId: true,
  cardNumber: true,
  qrCode: true,
});

export const insertAdminUserSchema = createInsertSchema(adminUsers).pick({
  username: true,
  password: true,
  email: true,
});

export const insertWhatsappConversionSchema = createInsertSchema(whatsappConversions).pick({
  phone: true,
  name: true,
  email: true,
  buttonType: true,
  planName: true,
  doctorName: true,
  ipAddress: true,
  userAgent: true,
});

export type InsertCustomer = z.infer<typeof insertCustomerSchema>;
export type Customer = typeof customers.$inferSelect;
export type InsertSubscription = z.infer<typeof insertSubscriptionSchema>;
export type Subscription = typeof subscriptions.$inferSelect;
export type InsertDigitalCard = z.infer<typeof insertDigitalCardSchema>;
export type DigitalCard = typeof digitalCards.$inferSelect;
export type Plan = typeof plans.$inferSelect;
export type InsertUser = z.infer<typeof insertUserSchema>;
export type User = typeof users.$inferSelect;
export type InsertAdminUser = z.infer<typeof insertAdminUserSchema>;
export type AdminUser = typeof adminUsers.$inferSelect;
export type InsertWhatsappConversion = z.infer<typeof insertWhatsappConversionSchema>;
export type WhatsappConversion = typeof whatsappConversions.$inferSelect;

export const insertUserSchema = createInsertSchema(users).pick({
  username: true,
  password: true,
});
