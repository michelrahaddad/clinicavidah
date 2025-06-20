import { TrendingUp, Users, MessageCircle, Stethoscope } from "lucide-react";

export default function BenefitsSection() {
  const stats = [
    { value: "100+", label: "Parceiros em Ibitinga e região" },
    { value: "50K+", label: "Clientes Satisfeitos" },
    { value: "30%", label: "Economia Média" },
    { value: "100%", label: "Suporte Humanizado" }
  ];

  return (
    <section id="beneficios" className="py-20 bg-white">
      <div className="container mx-auto px-4">
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold text-[#636E72] mb-6">
            Por que escolher o <span className="gradient-text">Cartão + Vidah?</span>
          </h2>
          <p className="text-xl text-[#636E72] max-w-3xl mx-auto">
            Mais de 17 empresas parceiras oferecendo descontos exclusivos para você e sua família.
          </p>
        </div>

        {/* Stats Section */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-8 text-center mb-16">
          {stats.map((stat, index) => (
            <div key={index} className="space-y-2">
              <div className="text-3xl md:text-4xl font-bold gradient-text">{stat.value}</div>
              <div className="text-[#636E72]">{stat.label}</div>
            </div>
          ))}
        </div>

        {/* Additional Benefits */}
        <div className="mt-16 grid md:grid-cols-3 gap-8">
          <div className="text-center p-6">
            <TrendingUp className="w-12 h-12 text-[#00B894] mx-auto mb-4" />
            <h4 className="font-semibold text-[#636E72] mb-2">✅ Mais de 100 parceiros em Ibitinga e região</h4>
            <p className="text-sm text-[#636E72]">Aproveite descontos em clínicas, farmácias, óticas e muito mais.</p>
          </div>
          <div className="text-center p-6">
            <Stethoscope className="w-12 h-12 text-[#00B894] mx-auto mb-4" />
            <h4 className="font-semibold text-[#636E72] mb-2">🩺 Saúde acessível de verdade</h4>
            <p className="text-sm text-[#636E72]">Consultas médicas e odontológicas com preços reduzidos em locais de confiança.</p>
          </div>
          <div className="text-center p-6">
            <MessageCircle className="w-12 h-12 text-[#00B894] mx-auto mb-4" />
            <h4 className="font-semibold text-[#636E72] mb-2">💬 Suporte quando você mais precisar</h4>
            <p className="text-sm text-[#636E72]">Fale com a gente sempre que tiver dúvidas — atendimento rápido e humanizado.</p>
          </div>
        </div>
      </div>
    </section>
  );
}
