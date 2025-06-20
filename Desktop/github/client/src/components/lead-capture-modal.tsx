import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { X, Phone, User, Mail } from "lucide-react";
import { useMutation } from "@tanstack/react-query";
import { whatsappApi } from "@/lib/api";
import { useToast } from "@/hooks/use-toast";
import { formatPhone } from "@/lib/utils";
import { generateWhatsAppUrl, openWhatsApp } from "@/lib/device-detection";

const leadCaptureSchema = z.object({
  name: z.string().min(2, "Nome deve ter pelo menos 2 caracteres"),
  email: z.string().email("Email deve ter um formato válido"),
  phone: z.string().optional().or(z.literal("")),
});

type LeadCaptureData = z.infer<typeof leadCaptureSchema>;

interface LeadCaptureModalProps {
  isOpen: boolean;
  onClose: () => void;
  buttonType: 'plan_subscription' | 'doctor_appointment' | 'enterprise_quote';
  planName?: string;
  doctorName?: string;
  whatsappPhone: string;
  whatsappMessage: string;
}

export default function LeadCaptureModal({
  isOpen,
  onClose,
  buttonType,
  planName,
  doctorName,
  whatsappPhone,
  whatsappMessage
}: LeadCaptureModalProps) {
  const { toast } = useToast();
  const [showFallbackButton, setShowFallbackButton] = useState(false);
  const [fallbackWhatsappUrl, setFallbackWhatsappUrl] = useState("");
  
  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
    watch
  } = useForm<LeadCaptureData>({
    resolver: zodResolver(leadCaptureSchema),
    mode: "onChange",
    defaultValues: {
      name: "",
      email: "",
      phone: ""
    }
  });

  const phoneValue = watch("phone");

  const trackConversionMutation = useMutation({
    mutationFn: async (data: LeadCaptureData) => {
      try {
        const formData = {
          buttonType,
          planName,
          doctorName,
          name: data.name,
          email: data.email,
          phone: data.phone || '',
        };
        
        console.log('🚀 Enviando dados:', formData);
        const response = await fetch(`${import.meta.env.VITE_API_URL}/track-whatsapp`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(formData),
        });

        if (!response.ok) {
          const errorData = await response.json().catch(() => ({ message: 'Erro desconhecido' }));
          throw new Error(errorData.message || 'Erro ao registrar conversão');
        }

        return await response.json();
      } catch (error) {
        console.error('Erro ao registrar conversão:', error);
        throw error;
      }
    },
    onSuccess: (data) => {
      // Limpa formulário e fecha modal
      reset();
      onClose();
      
      // Redireciona para WhatsApp com máxima compatibilidade
      if (data?.data?.whatsappUrl) {
        // Usa URL do backend se disponível
        try {
          window.location.href = data.data.whatsappUrl;
        } catch (error) {
          window.open(data.data.whatsappUrl, '_blank');
        }
      } else {
        // Fallback: gera e abre WhatsApp do lado do cliente
        let message = '';
        
        if (buttonType === 'plan_subscription') {
          message = `Olá! Meu nome é ${watch('name')} e tenho interesse no plano ${planName}.\n\n` +
                   `📱 Telefone: ${watch('phone') || 'Não informado'}\n` +
                   `📧 Email: ${watch('email')}\n\n` +
                   `Gostaria de saber mais detalhes sobre os benefícios e como contratar.`;
        } else if (buttonType === 'doctor_appointment') {
          message = `Olá! Meu nome é ${watch('name')} e gostaria de agendar uma consulta com ${doctorName}.\n\n` +
                   `📱 Telefone: ${watch('phone') || 'Não informado'}\n` +
                   `📧 Email: ${watch('email')}\n\n` +
                   `Qual a disponibilidade para atendimento?`;
        } else {
          message = `Olá! Meu nome é ${watch('name')} e represento uma empresa interessada nos planos corporativos.\n\n` +
                   `📱 Telefone: ${watch('phone') || 'Não informado'}\n` +
                   `📧 Email: ${watch('email')}\n\n` +
                   `Gostaria de receber uma proposta personalizada para nossa equipe.`;
        }
        
        openWhatsApp('5516993247676', message);
      }
    }
  });



  const onSubmit = async (data: LeadCaptureData) => {
    try {
      console.log('🚀 Iniciando envio dos dados:', data);
      
      // Registra a conversão no sistema
      const result = await trackConversionMutation.mutateAsync(data);
      console.log('✅ Conversão registrada com sucesso:', result);
      
      // Usa a URL do WhatsApp retornada pelo servidor
      const whatsappUrl = result.data?.whatsappUrl;
      console.log('🔗 URL do WhatsApp recebida:', whatsappUrl);
      
      if (!whatsappUrl) {
        console.error('❌ URL do WhatsApp não foi gerada');
        throw new Error('URL do WhatsApp não foi gerada');
      }
      
      toast({
        title: "Sucesso!",
        description: "Dados registrados! Abrindo WhatsApp...",
      });
      
      console.log('🌐 Abrindo WhatsApp Web diretamente...');
      
      // Fecha modal e limpa formulário
      onClose();
      reset();
      
      // Cria um link temporário e clica nele para evitar CSP
      const link = document.createElement('a');
      link.href = whatsappUrl;
      link.target = '_blank';
      link.rel = 'noopener noreferrer';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      console.log('✅ WhatsApp Web aberto');
      
    } catch (error) {
      console.error('❌ Erro completo no onSubmit:', error);
      
      // Log detalhado do erro
      if (error instanceof Error) {
        console.error('Nome do erro:', error.name);
        console.error('Mensagem do erro:', error.message);
        console.error('Stack trace:', error.stack);
      }
      
      toast({
        title: "Erro",
        description: error instanceof Error ? error.message : "Não foi possível processar sua solicitação. Tente novamente.",
        variant: "destructive",
      });
    }
  };



  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md mx-auto animate-in fade-in-0 zoom-in-95 duration-200 max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          {/* Header */}
          <div className="flex items-center justify-between mb-6">
            <div>
              <h3 className="text-xl font-bold text-gray-900">
                Quase lá!
              </h3>
              <p className="text-gray-600 text-sm mt-1">
                Preencha seus dados para continuar
              </p>
            </div>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 transition-colors p-2 rounded-full hover:bg-gray-100"
            >
              <X size={20} />
            </button>
          </div>

          {/* Context Info */}
          <div className="bg-[#00B894]/5 border border-[#00B894]/20 rounded-lg p-4 mb-6">
            <div className="flex items-center gap-2 text-[#00B894] text-sm font-medium">
              {buttonType === 'plan_subscription' && (
                <>
                  <span>📋</span>
                  <span>Plano: {planName}</span>
                </>
              )}
              {buttonType === 'doctor_appointment' && (
                <>
                  <span>👨‍⚕️</span>
                  <span>Consulta: {doctorName}</span>
                </>
              )}
              {buttonType === 'enterprise_quote' && (
                <>
                  <span>🏢</span>
                  <span>Cotação Empresarial</span>
                </>
              )}
            </div>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            {/* Nome */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Nome completo
              </label>
              <div className="relative">
                <User size={18} className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                <input
                  {...register("name")}
                  type="text"
                  placeholder="Digite seu nome completo"
                  className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#00B894] focus:border-transparent outline-none transition-all"
                />
              </div>
              {errors.name && (
                <p className="text-red-500 text-sm mt-1">{errors.name.message}</p>
              )}
            </div>

            {/* Email */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Email
              </label>
              <div className="relative">
                <Mail size={18} className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                <input
                  {...register("email")}
                  type="email"
                  placeholder="Digite seu email"
                  className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#00B894] focus:border-transparent outline-none transition-all"
                />
              </div>
              {errors.email && (
                <p className="text-red-500 text-sm mt-1">{errors.email.message}</p>
              )}
            </div>

            {/* Telefone */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Telefone/WhatsApp
              </label>
              <div className="relative">
                <Phone size={18} className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                <input
                  {...register("phone")}
                  type="tel"
                  placeholder="(11) 99999-9999"
                  className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#00B894] focus:border-transparent outline-none transition-all"
                />
              </div>

            </div>

            {/* Buttons */}
            <div className="flex gap-3 pt-4">
              <button
                type="button"
                onClick={onClose}
                className="flex-1 py-3 px-4 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors font-medium"
              >
                Cancelar
              </button>
              <button
                type="submit"
                disabled={trackConversionMutation.isPending}
                className="flex-1 py-3 px-4 bg-[#00B894] text-white rounded-lg hover:bg-[#009d7f] transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {trackConversionMutation.isPending ? "Processando..." : "Continuar"}
              </button>
            </div>
          </form>

          {/* Fallback WhatsApp Button for iOS Safari */}
          {showFallbackButton && (
            <div className="mt-6 p-4 bg-green-50 border border-green-200 rounded-lg">
              <p className="text-sm text-green-800 mb-3 text-center">
                Clique no botão abaixo para abrir o WhatsApp:
              </p>
              <button
                onClick={() => {
                  window.location.href = fallbackWhatsappUrl;
                  setShowFallbackButton(false);
                  reset();
                  onClose();
                }}
                className="w-full py-3 px-4 bg-green-500 hover:bg-green-600 text-white rounded-lg font-medium flex items-center justify-center gap-2 transition-colors"
              >
                <span>💬</span>
                Abrir WhatsApp
              </button>
            </div>
          )}

          {/* Privacy Note */}
          <p className="text-xs text-gray-500 text-center mt-4">
            Seus dados são protegidos e utilizados apenas para contato sobre nossos serviços.
          </p>
        </div>
      </div>
    </div>
  );
}