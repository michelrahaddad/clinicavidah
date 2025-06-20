import { useState } from "react";
import { Plus, Minus } from "lucide-react";

export default function FaqSection() {
  const [openItems, setOpenItems] = useState<number[]>([]);

  const faqs = [
    {
      question: "Como funciona o cartão digital?",
      answer: "O cartão digital é gerado automaticamente após o pagamento e contém um QR Code único para você usar nos estabelecimentos parceiros. Ele fica disponível no seu celular e pode ser usado imediatamente."
    },
    {
      question: "Posso cancelar a qualquer momento?",
      answer: "Sim, você pode cancelar seu plano a qualquer momento através do nosso suporte ou área do cliente. O cancelamento é simples e pode ser feito online."
    },
    {
      question: "Quantos estabelecimentos parceiros existem?",
      answer: "Temos mais de 20 empresas parceiras em todo o Brasil, incluindo farmácias, restaurantes, academias, clínicas médicas, supermercados e muito mais. A rede está em constante expansão."
    },
    {
      question: "O plano familiar inclui quantas pessoas?",
      answer: "O plano familiar cobre o titular e até 4 dependentes, totalizando 5 pessoas com acesso aos benefícios. Todos recebem cartões digitais individuais."
    },
    {
      question: "Como uso os descontos?",
      answer: "Basta apresentar seu cartão digital (QR Code) no estabelecimento parceiro. O desconto é aplicado automaticamente no momento da compra. Alguns parceiros também aceitam o número do cartão."
    },
    {
      question: "Qual a economia média?",
      answer: "Nossos clientes economizam em média 30% em produtos e serviços. A economia varia conforme o uso e os estabelecimentos frequentados, mas muitos clientes recuperam o valor da anuidade em poucos meses."
    },
    {
      question: "O pagamento é seguro?",
      answer: "Sim, utilizamos tecnologia de criptografia de ponta e seguimos todos os protocolos de segurança bancária. Seus dados estão 100% protegidos e nunca são armazenados nos nossos servidores."
    },
    {
      question: "Posso usar o cartão em todo o Brasil?",
      answer: "Sim, o Cartão + Vidah é válido em todo território nacional. Nossa rede de parceiros está presente nas principais cidades do país, e você pode consultar os estabelecimentos pelo nosso app."
    }
  ];

  const toggleItem = (index: number) => {
    setOpenItems(prev => 
      prev.includes(index) 
        ? prev.filter(item => item !== index)
        : [...prev, index]
    );
  };

  return (
    <section id="faq" className="py-20 bg-gray-50">
      <div className="container mx-auto px-4">
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold text-[#636E72] mb-6">
            Perguntas <span className="gradient-text">Frequentes</span>
          </h2>
          <p className="text-xl text-[#636E72] max-w-3xl mx-auto">
            Tire suas dúvidas sobre o Cartão + Vidah e seus benefícios
          </p>
        </div>

        <div className="max-w-4xl mx-auto space-y-4">
          {faqs.map((faq, index) => {
            const isOpen = openItems.includes(index);
            
            return (
              <div 
                key={index}
                className="bg-white rounded-2xl p-6 hover:shadow-lg transition-all cursor-pointer"
                onClick={() => toggleItem(index)}
              >
                <div className="flex justify-between items-center">
                  <h3 className="text-lg font-semibold text-[#636E72] pr-4">
                    {faq.question}
                  </h3>
                  <div className="text-[#00B894] flex-shrink-0">
                    {isOpen ? <Minus size={24} /> : <Plus size={24} />}
                  </div>
                </div>
                
                {isOpen && (
                  <div className="mt-4 text-[#636E72] leading-relaxed animate-slide-up">
                    {faq.answer}
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {/* Contact CTA */}
        <div className="mt-16 text-center">
          <div className="bg-white rounded-2xl p-8 max-w-2xl mx-auto shadow-lg">
            <h3 className="text-2xl font-bold text-[#636E72] mb-4">
              Ainda tem dúvidas?
            </h3>
            <p className="text-[#636E72] mb-6">
              Nossa equipe está pronta para ajudar você com qualquer questão sobre o Cartão + Vidah
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <button 
                onClick={() => {
                  const message = "Olá! Tenho algumas dúvidas sobre o Cartão + Vidah";
                  const whatsappUrl = `https://wa.me/5516993247676?text=${encodeURIComponent(message)}`;
                  window.open(whatsappUrl, '_blank');
                }}
                className="bg-[#00B894] text-white px-6 py-3 rounded-full font-semibold hover:bg-[#009d7f] transition-colors"
              >
                Falar no WhatsApp
              </button>
              <button 
                onClick={() => window.location.href = 'mailto:cartaomaisvidah@gmail.com?subject=Dúvidas sobre o Cartão + Vidah'}
                className="border-2 border-[#0984E3] text-[#0984E3] px-6 py-3 rounded-full font-semibold hover:bg-[#0984E3] hover:text-white transition-colors"
              >
                Enviar E-mail
              </button>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
