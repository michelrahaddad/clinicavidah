import { useState } from "react";
import { X, Lock, CreditCard, Smartphone, FileText } from "lucide-react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Button } from "@/components/ui/button";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Label } from "@/components/ui/label";
import { useToast } from "@/hooks/use-toast";
import { subscriptionApi } from "@/lib/api";
import { formatCurrency, formatCPF, formatPhone } from "@/lib/utils";
import type { SelectedPlan, SubscriptionRequest } from "@shared/types";

// CPF validation function
function validateCPF(cpf: string): boolean {
  const cleaned = cpf.replace(/[^\d]/g, '');
  
  if (cleaned.length !== 11 || /^(\d)\1{10}$/.test(cleaned)) {
    return false;
  }
  
  let sum = 0;
  for (let i = 0; i < 9; i++) {
    sum += parseInt(cleaned.charAt(i)) * (10 - i);
  }
  let remainder = 11 - (sum % 11);
  if (remainder === 10 || remainder === 11) remainder = 0;
  if (remainder !== parseInt(cleaned.charAt(9))) return false;
  
  sum = 0;
  for (let i = 0; i < 10; i++) {
    sum += parseInt(cleaned.charAt(i)) * (11 - i);
  }
  remainder = 11 - (sum % 11);
  if (remainder === 10 || remainder === 11) remainder = 0;
  if (remainder !== parseInt(cleaned.charAt(10))) return false;
  
  return true;
}

interface CheckoutModalProps {
  plan: SelectedPlan;
  onClose: () => void;
}

const checkoutSchema = z.object({
  name: z.string().min(2, "Nome deve ter pelo menos 2 caracteres"),
  email: z.string().email("Email inválido"),
  cpf: z.string().refine(validateCPF, "CPF inválido"),
  phone: z.string().min(10, "Telefone inválido"),
  paymentMethod: z.enum(['pix', 'credit', 'boleto']),
});

type CheckoutFormData = z.infer<typeof checkoutSchema>;

export default function CheckoutModal({ plan, onClose }: CheckoutModalProps) {
  const [isProcessing, setIsProcessing] = useState(false);
  const { toast } = useToast();
  const queryClient = useQueryClient();

  const form = useForm<CheckoutFormData>({
    resolver: zodResolver(checkoutSchema),
    defaultValues: {
      name: "",
      email: "",
      cpf: "",
      phone: "",
      paymentMethod: "pix",
    },
  });

  const watchedPaymentMethod = form.watch("paymentMethod");

  const createSubscriptionMutation = useMutation({
    mutationFn: async (data: CheckoutFormData) => {
      const requestData = {
        customer: {
          name: data.name,
          email: data.email,
          cpf: data.cpf.replace(/\D/g, ''),
          phone: data.phone.replace(/\D/g, ''),
        },
        planId: plan.id,
        paymentMethod: data.paymentMethod,
        installments: data.paymentMethod === 'pix' ? 1 : 12,
      };

      return await subscriptionApi.create(requestData);
    },
    onSuccess: (data) => {
      toast({
        title: "Pagamento realizado com sucesso!",
        description: "Seu cartão digital foi gerado e enviado por email.",
      });
      queryClient.invalidateQueries({ queryKey: ['/api/plans'] });
      onClose();
      
      // Show digital card or redirect to success page
      console.log('Subscription created:', data);
    },
    onError: (error: any) => {
      toast({
        title: "Erro no pagamento",
        description: error.message || "Ocorreu um erro ao processar o pagamento. Tente novamente.",
        variant: "destructive",
      });
    },
  });

  const onSubmit = async (data: CheckoutFormData) => {
    setIsProcessing(true);
    try {
      await createSubscriptionMutation.mutateAsync(data);
    } finally {
      setIsProcessing(false);
    }
  };

  const getPricingInfo = () => {
    const annualPrice = typeof plan.annualPrice === 'number' ? plan.annualPrice : parseFloat(String(plan.annualPrice));
    const adhesionFee = typeof plan.adhesionFee === 'number' ? plan.adhesionFee : parseFloat(String(plan.adhesionFee));

    switch (watchedPaymentMethod) {
      case 'pix':
        const discountedPrice = annualPrice * 0.9;
        return {
          planPrice: discountedPrice,
          total: discountedPrice + adhesionFee,
          installments: 1,
          adhesionFee: adhesionFee,
          description: "À vista com 10% de desconto"
        };
      case 'credit':
        const creditMonthly = plan.type === 'individual' ? 24.90 : 34.90;
        return {
          planPrice: creditMonthly * 12,
          total: (creditMonthly * 12) + adhesionFee,
          installments: 12,
          adhesionFee: adhesionFee,
          description: `12x de R$ ${creditMonthly.toFixed(2)}`
        };
      case 'boleto':
        const boletoMonthly = plan.type === 'individual' ? 27.90 : 37.90;
        return {
          planPrice: boletoMonthly * 12,
          total: (boletoMonthly * 12) + adhesionFee,
          installments: 12,
          adhesionFee: adhesionFee,
          description: `12x de R$ ${boletoMonthly.toFixed(2)}`
        };
      default:
        return {
          planPrice: annualPrice,
          total: annualPrice + adhesionFee,
          installments: 1,
          adhesionFee: adhesionFee,
          description: "Pagamento único"
        };
    }
  };

  const pricingInfo = getPricingInfo();

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-3xl p-8 max-w-md w-full max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-6">
          <h3 className="text-2xl font-bold text-[#636E72]">Finalizar Compra</h3>
          <Button
            variant="ghost"
            size="icon"
            onClick={onClose}
            className="text-[#636E72] hover:text-[#00B894]"
          >
            <X size={24} />
          </Button>
        </div>

        {/* Plan Summary */}
        <div className="bg-gray-50 rounded-2xl p-6 mb-6">
          <div className="flex justify-between items-center">
            <div>
              <h4 className="font-semibold text-[#636E72]">Plano {plan.name}</h4>
              <p className="text-sm text-[#636E72]">Acesso completo aos benefícios</p>
              <p className="text-sm text-[#636E72] mt-1">{pricingInfo.description}</p>
            </div>
            <div className="text-right">
              <div className="text-xl font-bold text-[#00B894]">
                {formatCurrency(pricingInfo.planPrice)}
              </div>
              <div className="text-sm text-[#636E72]">
                + {formatCurrency(pricingInfo.adhesionFee || 0)} adesão
              </div>
              <div className="text-lg font-bold text-[#636E72] mt-1 border-t pt-1">
                Total: {formatCurrency(pricingInfo.total)}
              </div>
            </div>
          </div>
        </div>

        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
            {/* Payment Method Selection */}
            <FormField
              control={form.control}
              name="paymentMethod"
              render={({ field }) => (
                <FormItem>
                  <FormLabel className="font-semibold text-[#636E72]">Forma de Pagamento</FormLabel>
                  <FormControl>
                    <RadioGroup
                      onValueChange={field.onChange}
                      defaultValue={field.value}
                      className="space-y-3"
                    >
                      <div className="flex items-center space-x-3 p-4 border-2 rounded-xl cursor-pointer hover:border-[#00B894] transition-colors">
                        <RadioGroupItem value="pix" id="pix" />
                        <Label htmlFor="pix" className="flex-1 cursor-pointer">
                          <div className="flex items-center">
                            <Smartphone className="w-5 h-5 mr-3 text-[#00B894]" />
                            <div>
                              <div className="font-medium">PIX (10% desconto)</div>
                              <div className="text-sm text-[#636E72]">
                                {formatCurrency(pricingInfo.planPrice)} + {formatCurrency(pricingInfo.adhesionFee || 0)}
                              </div>
                            </div>
                          </div>
                        </Label>
                      </div>
                      
                      <div className="flex items-center space-x-3 p-4 border-2 rounded-xl cursor-pointer hover:border-[#00B894] transition-colors">
                        <RadioGroupItem value="credit" id="credit" />
                        <Label htmlFor="credit" className="flex-1 cursor-pointer">
                          <div className="flex items-center">
                            <CreditCard className="w-5 h-5 mr-3 text-[#0984E3]" />
                            <div>
                              <div className="font-medium">Cartão de Crédito</div>
                              <div className="text-sm text-[#636E72]">
                                12x R$ {plan.type === 'individual' ? '24,90' : '34,90'} + {formatCurrency(pricingInfo.adhesionFee || 0)}
                              </div>
                            </div>
                          </div>
                        </Label>
                      </div>
                      
                      <div className="flex items-center space-x-3 p-4 border-2 rounded-xl cursor-pointer hover:border-[#00B894] transition-colors">
                        <RadioGroupItem value="boleto" id="boleto" />
                        <Label htmlFor="boleto" className="flex-1 cursor-pointer">
                          <div className="flex items-center">
                            <FileText className="w-5 h-5 mr-3 text-[#636E72]" />
                            <div>
                              <div className="font-medium">Boleto Bancário</div>
                              <div className="text-sm text-[#636E72]">
                                12x R$ {plan.type === 'individual' ? '27,90' : '37,90'} + {formatCurrency(pricingInfo.adhesionFee || 0)}
                              </div>
                            </div>
                          </div>
                        </Label>
                      </div>
                    </RadioGroup>
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            {/* Customer Information */}
            <div className="space-y-4">
              <FormField
                control={form.control}
                name="name"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Nome Completo</FormLabel>
                    <FormControl>
                      <Input
                        {...field}
                        placeholder="Seu nome completo"
                        className="form-input"
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="email"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>E-mail</FormLabel>
                    <FormControl>
                      <Input
                        {...field}
                        type="email"
                        placeholder="seu@email.com"
                        className="form-input"
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <div className="grid grid-cols-2 gap-4">
                <FormField
                  control={form.control}
                  name="cpf"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>CPF</FormLabel>
                      <FormControl>
                        <Input
                          {...field}
                          placeholder="000.000.000-00"
                          className="form-input"
                          onChange={(e) => {
                            const formattedCPF = formatCPF(e.target.value);
                            field.onChange(formattedCPF);
                          }}
                          maxLength={14}
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="phone"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Telefone</FormLabel>
                      <FormControl>
                        <Input
                          {...field}
                          placeholder="(11) 99999-9999"
                          className="form-input"
                          onChange={(e) => {
                            const formattedPhone = formatPhone(e.target.value);
                            field.onChange(formattedPhone);
                          }}
                          maxLength={15}
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>
            </div>

            <Button
              type="submit"
              className="w-full bg-[#00B894] text-white py-4 rounded-full font-semibold hover:bg-[#009d7f] transition-colors"
              disabled={isProcessing || createSubscriptionMutation.isPending}
            >
              {isProcessing || createSubscriptionMutation.isPending ? (
                <div className="flex items-center">
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                  Processando...
                </div>
              ) : (
                'Finalizar Pagamento'
              )}
            </Button>

            <div className="text-xs text-[#636E72] text-center flex items-center justify-center">
              <Lock className="w-3 h-3 mr-1" />
              Pagamento 100% seguro e criptografado
            </div>
          </form>
        </Form>
      </div>
    </div>
  );
}
