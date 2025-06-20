import { motion } from "framer-motion";
import { useState } from "react";
import { Plus, Sparkles } from "lucide-react";

// Estrutura moderna para empresas parceiras
const parceiros = [
  { nome: "Silasgás Ultragaz", desconto: "10%", categoria: "Energia & Gás", icon: "🔥", cor: "#FF6B6B" },
  { nome: "Óticas Carol", desconto: "20%", categoria: "Saúde Visual", icon: "👁️", cor: "#4ECDC4" },
  { nome: "Fiducia Eletro", desconto: "10%", categoria: "Tecnologia", icon: "⚡", cor: "#45B7D1" },
  { nome: "Evolução Centro", desconto: "Especial", categoria: "Bem-estar", icon: "🏥", cor: "#96CEB4" },
  { nome: "Pronto Vet", desconto: "15%", categoria: "Pet Care", icon: "🐾", cor: "#FFEAA7" },
  { nome: "Reabilitar Neuroped", desconto: "Especial", categoria: "Fisioterapia", icon: "🏃‍♂️", cor: "#DDA0DD" },
  { nome: "Corpo em Harmonia", desconto: "Especial", categoria: "Fitness", icon: "🧘‍♀️", cor: "#98D8C8" },
  { nome: "Drogaven", desconto: "Especial", categoria: "Farmácia", icon: "💊", cor: "#F7DC6F" },
  { nome: "Hospital Malzoni", desconto: "Especial", categoria: "Saúde", icon: "🏥", cor: "#BB8FCE" },
  { nome: "Dom Pedro", desconto: "15%", categoria: "Alimentação", icon: "🥬", cor: "#85C1E9" },
  { nome: "Magia do Sorriso", desconto: "20%", categoria: "Odontologia", icon: "😁", cor: "#F8C471" },
  { nome: "Lab 7", desconto: "30%", categoria: "Diagnósticos", icon: "🔬", cor: "#82E0AA" }
];

export default function ModernPartnersSection() {
  const [showAll, setShowAll] = useState(false);
  const displayedPartners = showAll ? parceiros : parceiros.slice(0, 8);

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: { staggerChildren: 0.1 }
    }
  };

  const itemVariants = {
    hidden: { y: 20, opacity: 0 },
    visible: {
      y: 0,
      opacity: 1,
      transition: { duration: 0.5 }
    }
  };

  return (
    <section className="py-20 bg-gradient-to-br from-slate-50 via-white to-blue-50 relative overflow-hidden">
      {/* Background Effects */}
      <div className="absolute inset-0">
        <div className="absolute top-20 left-10 w-72 h-72 bg-gradient-to-r from-[#00B894]/10 to-[#0984E3]/10 rounded-full blur-3xl"></div>
        <div className="absolute bottom-20 right-10 w-96 h-96 bg-gradient-to-r from-[#0984E3]/10 to-[#00B894]/10 rounded-full blur-3xl"></div>
      </div>

      <div className="container mx-auto px-4 relative">
        {/* Header */}
        <motion.div
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          variants={containerVariants}
          className="text-center mb-16"
        >
          <motion.div
            variants={itemVariants}
            className="inline-flex items-center gap-2 bg-white/80 backdrop-blur-sm px-6 py-3 rounded-full border border-[#00B894]/20 mb-6"
          >
            <Sparkles className="w-5 h-5 text-[#00B894]" />
            <span className="text-gray-600 font-medium">Rede Premium</span>
          </motion.div>

          <motion.h2
            variants={itemVariants}
            className="text-4xl md:text-5xl font-bold mb-6"
          >
            <span className="bg-gradient-to-r from-[#00B894] via-[#00d2a0] to-[#0984E3] bg-clip-text text-transparent">
              Parceiros Exclusivos
            </span>
          </motion.h2>

          <motion.p
            variants={itemVariants}
            className="text-xl text-gray-600 max-w-3xl mx-auto"
          >
            Descontos e benefícios especiais em uma rede cuidadosamente selecionada de empresas locais
          </motion.p>
        </motion.div>

        {/* Partners Grid */}
        <motion.div
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          variants={containerVariants}
          className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-6 gap-4 md:gap-6 mb-12"
        >
          {displayedPartners.map((parceiro, index) => (
            <motion.div
              key={parceiro.nome}
              variants={itemVariants}
              className="group relative"
            >
              {/* Card Principal */}
              <div className="relative bg-white/80 backdrop-blur-sm rounded-3xl p-6 shadow-lg hover:shadow-2xl transition-all duration-500 transform hover:-translate-y-3 border border-white/50 overflow-hidden">
                
                {/* Efeito de brilho */}
                <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-1000"></div>
                
                {/* Badge de desconto */}
                <div className="absolute -top-3 -right-3 bg-gradient-to-r from-[#00B894] to-[#00d2a0] text-white px-3 py-1 rounded-full text-xs font-bold shadow-lg z-10 animate-pulse">
                  {parceiro.desconto}
                </div>
                
                {/* Conteúdo */}
                <div className="relative z-10 text-center">
                  {/* Ícone com cor dinâmica */}
                  <div 
                    className="w-20 h-20 mx-auto rounded-full flex items-center justify-center mb-4 group-hover:scale-110 transition-transform duration-300 shadow-lg"
                    style={{ 
                      background: `linear-gradient(135deg, ${parceiro.cor}20, ${parceiro.cor}10)`,
                      border: `2px solid ${parceiro.cor}30`
                    }}
                  >
                    <span className="text-3xl filter drop-shadow-sm">{parceiro.icon}</span>
                  </div>
                  
                  {/* Nome */}
                  <h4 className="font-bold text-gray-800 mb-2 text-sm leading-tight group-hover:text-[#00B894] transition-colors duration-300">
                    {parceiro.nome}
                  </h4>
                  
                  {/* Categoria */}
                  <div className="inline-flex items-center px-3 py-1 bg-gray-100/80 text-gray-700 rounded-full text-xs font-medium group-hover:bg-[#00B894]/10 group-hover:text-[#00B894] transition-all duration-300">
                    {parceiro.categoria}
                  </div>
                  
                  {/* Barra de progresso animada */}
                  <div className="mt-4 w-full h-1 bg-gray-200 rounded-full overflow-hidden">
                    <div 
                      className="h-full rounded-full transform scale-x-0 group-hover:scale-x-100 transition-transform duration-700 origin-left"
                      style={{ background: `linear-gradient(90deg, ${parceiro.cor}, ${parceiro.cor}80)` }}
                    ></div>
                  </div>
                </div>
              </div>
            </motion.div>
          ))}
        </motion.div>

        {/* Botão Ver Mais */}
        {!showAll && parceiros.length > 8 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center"
          >
            <button
              onClick={() => setShowAll(true)}
              className="group relative bg-gradient-to-r from-[#00B894] to-[#00d2a0] text-white px-10 py-4 rounded-2xl font-semibold hover:from-[#009d7f] hover:to-[#00B894] transition-all duration-300 shadow-lg hover:shadow-2xl transform hover:-translate-y-1 flex items-center gap-3 mx-auto"
            >
              <span>Ver Todos os Parceiros</span>
              <div className="w-6 h-6 bg-white/20 rounded-full flex items-center justify-center group-hover:rotate-180 transition-transform duration-300">
                <Plus size={16} />
              </div>
            </button>
          </motion.div>
        )}
      </div>
    </section>
  );
}