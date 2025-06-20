export default function HowItWorksSection() {
  const steps = [
    {
      number: 1,
      title: "Escolha seu Plano",
      description: "Selecione o plano que melhor se adequa às suas necessidades"
    },
    {
      number: 2,
      title: "Efetue o Pagamento",
      description: "Pague com segurança através de PIX, cartão ou boleto"
    },
    {
      number: 3,
      title: "Receba seu Cartão",
      description: "Cartão digital gerado automaticamente com QR Code único"
    },
    {
      number: 4,
      title: "Aproveite os Benefícios",
      description: "Use em mais de 1000 empresas parceiras e economize"
    }
  ];

  return (
    <section id="como-funciona" className="py-20 bg-white">
      <div className="container mx-auto px-4">
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold text-[#636E72] mb-6">
            Como <span className="gradient-text">Funciona?</span>
          </h2>
          <p className="text-xl text-[#636E72] max-w-3xl mx-auto">
            Em poucos passos você já estará aproveitando todos os benefícios do Cartão + Vidah
          </p>
        </div>

        <div className="grid md:grid-cols-4 gap-8">
          {steps.map((step, index) => (
            <div key={index} className="text-center group">
              <div className="w-20 h-20 gradient-bg rounded-full flex items-center justify-center mx-auto mb-6 text-white text-2xl font-bold group-hover:scale-110 transition-transform">
                {step.number}
              </div>
              <h3 className="text-xl font-bold text-[#636E72] mb-4">{step.title}</h3>
              <p className="text-[#636E72]">{step.description}</p>
              
              {/* Connection line (hidden on mobile) */}
              {index < steps.length - 1 && (
                <div className="hidden md:block absolute top-10 left-1/2 w-full h-0.5 bg-gradient-to-r from-[#00B894] to-[#0984E3] opacity-30 transform translate-y-full"></div>
              )}
            </div>
          ))}
        </div>

        {/* Additional info */}
        <div className="mt-16 text-center">
          <div className="bg-gradient-to-r from-[#00B894]/10 to-[#0984E3]/10 rounded-2xl p-8 max-w-4xl mx-auto">
            <h3 className="text-2xl font-bold text-[#636E72] mb-4">
              Processo 100% Digital
            </h3>
            <p className="text-[#636E72] text-lg">
              Todo o processo é realizado online de forma segura e rápida. 
              Após a confirmação do pagamento, você recebe seu cartão digital imediatamente 
              e pode começar a usar os benefícios na mesma hora.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}
