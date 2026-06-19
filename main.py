import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import time
from io import BytesIO
import random
import urllib.parse
import re
import textwrap
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
try:
    from mercado_pago_utils import MercadoPagoManager, render_checkout_redirect, check_payment_and_unlock
except ImportError:
    MercadoPagoManager = None

# Função local de pagamento - Botão Mercado Pago simples
def render_payment_button(email, nome):
    """Renderizar botão de pagamento Mercado Pago"""
    st.markdown("### 💳 Desbloqueie seu Relatório Premium")
    st.info("Valor promocional: R$ 1,99")

    st.link_button(
        "🚀 LIBERAR ACESSO EXECUTIVO - R$ 1,99",
        "https://link.mercadopago.com.br/relatorioexecutivo"
    )

    st.caption(
        "Após a confirmação do pagamento, o acesso ao relatório premium será liberado."
    )


# ==============================================================================
# 1. CONFIGURAÇÕES GERAIS E ARQUITETURA VISUAL (DARK LUXURY TERMINAL)
# ==============================================================================
st.set_page_config(
    page_title="AuraDex Arquétipos Supremo | Inteligência Comportamental",
    page_icon="⚜️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Injeção de CSS customizado para emular um Dashboard Executivo Premium / Apple & Ferrari Design
st.markdown("""
    <style>
    /* Estilos Globais de Fundo e Texto */
    .stApp {
        background-color: #0d1117;
        color: #f0f3f6;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    
    /* Cabeçalhos e Títulos Luxuosos */
    h1, h2, h3, h4 {
        color: #d4af37 !important;
        font-family: "Times New Roman", Georgia, serif;
        font-weight: 300;
        letter-spacing: 2px;
        text-align: center;
    }
    h1 { font-size: 2.4rem; line-height: 1.3; margin-bottom: 0.5rem; }
    h2 { font-size: 1.8rem; border-bottom: 1px solid rgba(212, 175, 55, 0.2); padding-bottom: 0.5rem; margin-top: 2rem; }
    
    /* Subtítulos de Alta Conversão */
    .luxury-subtitle {
        text-align: center;
        font-size: 1.15rem;
        color: #8b949e;
        max-width: 650px;
        margin: 0 auto 2.5rem auto;
        line-height: 1.6;
        font-weight: 300;
    }
    
    /* Métricas e Indicadores estilo Bloomberg */
    .bloomberg-container {
        display: flex;
        justify-content: space-around;
        background: linear-gradient(180deg, #161b22 0%, #0f141c 100%);
        border: 1px solid rgba(212, 175, 55, 0.15);
        padding: 1.5rem;
        border-radius: 8px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
    }
    .bloomberg-box {
        text-align: center;
    }
    .bloomberg-val {
        font-family: "Courier New", Courier, monospace;
        font-size: 1.8rem;
        color: #d4af37;
        font-weight: bold;
    }
    .bloomberg-lbl {
        font-size: 0.75rem;
        color: #8b949e;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        margin-top: 4px;
    }
    
    /* Cartões estruturados com Glassmorphic Subtle Effect */
    .glass-card {
        background: rgba(22, 27, 34, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-left: 3px solid #d4af37;
        padding: 2rem;
        border-radius: 8px;
        margin-bottom: 1.5rem;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
    }
    .glass-card-title {
        font-family: "Times New Roman", serif;
        color: #d4af37;
        font-size: 1.3rem;
        margin-bottom: 1rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Botões Customizados Premium */
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #b8860b 0%, #e6ca65 50%, #996515 100%);
        color: #0d1117 !important;
        font-weight: bold;
        font-size: 1.05rem;
        letter-spacing: 2px;
        border: none !important;
        padding: 14px 20px;
        border-radius: 6px;
        text-transform: uppercase;
        transition: all 0.3s ease-in-out;
        box-shadow: 0 4px 15px rgba(212, 175, 55, 0.2);
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 25px rgba(212, 175, 55, 0.4);
        color: #0d1117 !important;
        background: linear-gradient(135deg, #e6ca65 0%, #ffffff 100%);
    }
    
    /* Customização do Radio Input da Streamlit */
    div[data-testid="stRadio"] > label,
    div[role="radiogroup"] label,
    div[role="radiogroup"] span,
    div[data-testid="stRadio"] div[role="radio"] label {
        color: #f4f7fb !important;
        opacity: 1 !important;
    }
    div[data-testid="stRadio"] > label {
        color: #d4af37 !important;
        font-weight: 600;
    }
    div[data-testid="stRadio"] label[data-testid="stWidgetLabel"],
    div[role="radiogroup"] label {
        font-size: 1.15rem !important;
        margin-bottom: 15px !important;
        font-weight: 500 !important;
    }
    div[data-testid="stRadio"] div[role="radio"] {
        border: 1px solid rgba(212, 175, 55, 0.2) !important;
        border-radius: 8px !important;
        padding: 0.75rem !important;
        margin-bottom: 0.5rem !important;
        background: rgba(255, 255, 255, 0.03) !important;
    }
    
    /* Barra de progresso dourada */
    .stProgress > div > div > div > div {
        background-color: #d4af37;
    }
    
    .ticker-alert {
        color: #ff4d4d;
        border: 1px solid rgba(255, 77, 77, 0.3);
        background: rgba(255, 77, 77, 0.05);
        padding: 1rem;
        border-radius: 6px;
        font-size: 0.95rem;
        line-height: 1.5;
        margin: 1.5rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. BANCO DE DADOS DE ARQUÉTIPOS E SISTEMA PSICOMÉTRICO (COMPLETO)
# ==============================================================================
archetypes_data = {
    "O Sábio": {
        "rarity": "5.2%",
        "index": 94,
        "radar": [50, 80, 98, 45, 65, 85], # Liderança, Criatividade, Int. Estratégica, Influência, Coragem, Adaptabilidade
        "desc": "Guiado pelo rigor analítico, clareza lógica e busca incessante pela verdade factual. Você opera como uma inteligência estratégica superior, decodificando caos em dados acionáveis.",
        "secundario": "O Visionário",
        "sec_desc": "Fornece uma camada de antecipação macroeconômica e leitura de tendências de longo prazo antes que elas se manifestem no mercado tradicional.",
        "sombra": "O Dogmático / Paralisia por Análise. Tendência a reter decisões críticas sob a justificativa de necessitar de mais dados, gerando inércia tática e distanciamento emocional nas relações.",
        "financeiro": "Investidor Estruturado de Longo Prazo. Score: 88/100. Excelente blindagem contra impulsividade patrimonial; risco concentrado em custo de oportunidade devido ao excesso de prudência.",
        "amoroso": "Busca afinidade intelectual absoluta e sinergia de propósitos. Alinhamento de alto nível com 'O Governante' e 'O Criador'. Exige espaço de solitude cognitiva.",
        "carreira": "Chief Strategy Officer (CSO), Diretor de Inteligência de Mercado, Auditor de Riscos Complexos, Consultor Macroeconômico.",
        "talento_oculto": "Hiper-foco preditivo: capacidade de identificar inconsistências em contratos ou modelos de negócios complexos em poucos segundos de exposição.",
        "plano_evolucao": [
            "Estabelecer a Regra dos 70%: Tomar decisões executivas e pessoais quando possuir 70% das informações necessárias, mitigando a paralisia.",
            "Inserir blocos semanais de intuição pura e atividades sem métricas de performance.",
            "Praticar escuta empática ativa sem emitir diagnósticos corretivos imediatos."
        ],
        "compat_matrix": "Elevada com O Governante (estabilidade) e O Criador (inovação estruturada); Atrito potencial com O Bobo da Corte.",
        "frase": "A assimetria de informação é a única vantagem real e permanente no tabuleiro da vida."
    },
    "O Herói": {
        "rarity": "7.8%",
        "index": 91,
        "radar": [95, 45, 75, 60, 98, 70],
        "desc": "Definido pela força de vontade inabalável, agressividade competitiva saudável e fixação por metas de alta performance. Você prospera no epicentro da pressão.",
        "secundario": "O Governante",
        "sec_desc": "Agrega competência de governança e estruturação de processos ao ímpeto natural de conquista e execução direta.",
        "sombra": "O Tirano Exausto. Obsessão em carregar o peso operacional integral da organização ou família; incapacidade crônica de demonstrar vulnerabilidade culminando em Burnout tático.",
        "financeiro": "Alocador de Capital Agressivo. Score: 82/100. Impulsiona o patrimônio via empreendedorismo ou alavancagem rápida; vulnerável a cisnes negros por falta de diversificação defensiva.",
        "amoroso": "Postura de provedor e protetor sistêmico. Sinergia premium com 'O Cuidador' e 'O Inocente'. Risco de projetar dinâmicas de competição dentro do relacionamento.",
        "carreira": "Head de Venture Capital, Gestor de Turnaround, Líder de Operações Especiais, Fundador Scale-Up.",
        "talento_oculto": "Resiliência sob fogo cruzado: sua performance cognitiva aumenta proporcionalmente à gravidade da crise externa.",
        "plano_evolucao": [
            "Implementar delegação radical com tolerância a erros metodológicos de liderados.",
            "Mapear e respeitar os limites biológicos pessoais através de pausas compulsórias.",
            "Praticar a aceitação da ajuda externa como um ato de coragem estratégica."
        ],
        "compat_matrix": "Alta sinergia com O Cuidador e O Inocente; Conflito direto com O Rebelde.",
        "frase": "O destino não é uma questão de chance, é uma questão de escolha sob extrema pressão."
    },
    "O Governante": {
        "rarity": "3.4%",
        "index": 97,
        "radar": [100, 50, 90, 85, 75, 55],
        "desc": "Nascido para a liderança institucional, governança corporativa e consolidação de poder estruturado. Sua mente opera como um sistema operacional de ordem e escalabilidade.",
        "secundario": "O Sábio",
        "sec_desc": "Garante ancoragem teórica e dados empíricos inquestionáveis para sustentar os decretos e decisões de liderança.",
        "sombra": "O Ditador Paranoico. Medo subliminar de traição ou perda de controle operacional; tendência a centralizar processos e sufocar a autonomia criativa dos liderados.",
        "financeiro": "Preservador Patrimonial Corporativo. Score: 95/100. Maestria na engenharia tributária e blindagem de ativos. Risco associado à rigidez excessiva em novos mercados disruptivos.",
        "amoroso": "Exige lealdade absoluta e manutenção de padrões sociais elevados. Conexão profunda com 'O Sábio' e 'O Mago' (que traz a inovação complementar).",
        "carreira": "CEO, Conselheiro de Administração, Gestor de Private Equity, Diretor de Governança e Compliance.",
        "talento_oculto": "Visão sistêmica institucional: capacidade imediata de estruturar organogramas e fluxos de caixa eficientes em cenários caóticos.",
        "plano_evolucao": [
            "Promover rituais de inovação descentralizada onde sua voz seja a última a ser ouvida.",
            "Separar explicitamente a identidade de Líder Executivo da identidade de parceiro/pai.",
            "Praticar vulnerabilidade intencional com círculos restritos de confiança máxima."
        ],
        "compat_matrix": "Sinergia impecável com O Sábio; Riscos de colisão de ego com O Herói e outro Governante.",
        "frase": "A ordem e a previsibilidade pavimentam o único caminho real para a imortalidade do legado."
    },
    "O Mago": {
        "rarity": "2.9%",
        "index": 96,
        "radar": [80, 92, 88, 90, 60, 90],
        "desc": "Mestre da alquimia mental, transformação cultural e catalisador de transições de fase complexas. Você altera a percepção da realidade ao seu redor.",
        "secundario": "O Visionário",
        "sec_desc": "Traduz insights metafísicos e conceituais em designs tecnológicos ou modelos de negócios de alta disrupção.",
        "sombra": "O Manipulador Sutil. Utilização inconsciente do magnetismo pessoal e da retórica para conduzir indivíduos a cenários de interesse estritamente pessoal, camuflado de propósito coletivo.",
        "financeiro": "Estrategista de Oportunidades Assimétricas. Score: 89/100. Lucra alto antecipando bolhas e movimentos psicológicos de massa; risco de volatilidade severa por excesso de otimismo.",
        "amoroso": "Busca conexões de intensidade transcendente e transformadora. Compatibilidade master com 'O Amante' e 'O Criador'. Detesta superficialidade utilitarista.",
        "carreira": "Diretor de Inovação Disruptiva, Head de Growth Marketing Psicológico, Fundador de Tech de Fronteira, Neurostrategist.",
        "talento_oculto": "Leitura fria de microexpressões e dinâmicas ocultas de poder em salas de reunião.",
        "plano_evolucao": [
            "Ancorar visões abstratas em métricas semanais auditáveis por terceiros rígidos.",
            "Garantir transparência radical nas intenções antes de iniciar processos de persuasão.",
            "Cultivar práticas diárias de conexão com a realidade física e operacional básica."
        ],
        "compat_matrix": "Alta afinidade com O Criador e O Amante; Distanciamento metodológico do Sábio.",
        "frase": "A realidade não é fixa; ela se dobra diante de uma vontade perfeitamente alinhada e focada."
    },
    "O Criador": {
        "rarity": "4.8%",
        "index": 93,
        "radar": [65, 100, 80, 70, 70, 80],
        "desc": "Impulsionado pela necessidade visceral de autoria, inovação de produto e materialização de conceitos inexistentes. Você molda o ambiente físico e digital através do design.",
        "secundario": "O Explorador",
        "sec_desc": "Injeta insumos estéticos multiculturais e experiências geográficas diversificadas diretamente no processo criativo primário.",
        "sombra": "O Perfeccionista Paralisado. Autocrítica severa que impede a entrega (o 'launch') de projetos funcionais; incapacidade de aceitar que o feito supera o perfeito no mercado.",
        "financeiro": "Gerador de Ativos Intelectuais. Score: 85/100. Capacidade maciça de monetizar marcas e patentes. Risco latente de subprecificar o próprio valor por foco excessivo no processo produtivo.",
        "amoroso": "Precisa de um parceiro que atue como âncora de estabilidade sem castrar o fluxo de imaginação. Match ideal com 'O Sábio' e 'O Cuidador'.",
        "carreira": "Chief Product Officer (CPO), Diretor de Criação High-End, Arquiteto de Ecossistemas Digitais, Fundador de Startups Saas.",
        "talento_oculto": "Síntese conceitual: unir indústrias completamente distintas em um único produto altamente lucrativo.",
        "plano_evolucao": [
            "Adotar a metodologia MVP (Mínimo Produto Viável) como padrão inegociável de vida.",
            "Externalizar a gestão financeira e operacional para perfis do tipo Governante ou Sábio.",
            "Praticar o desapego emocional de ideias obsoletas que o mercado já rejeitou."
        ],
        "compat_matrix": "Sinergia excelente com O Explorador e O Mago; Conflito de rotina com O Governante.",
        "frase": "A única forma de prever o futuro econômico é projetando e construindo a infraestrutura dele."
    },
    "O Explorador": {
        "rarity": "6.1%",
        "index": 89,
        "radar": [60, 75, 70, 65, 85, 100],
        "desc": "A busca pela autonomia existencial e quebra de barreiras geográficas dita sua assinatura comportamental. Você rejeita restrições limitantes.",
        "secundario": "O Rebelde",
        "sec_desc": "Amplifica o desejo de liberdade com uma postura ativa de rejeição a dogmas corporativos obsoletos.",
        "sombra": "O Nômade Crônico / Instabilidade. Dificuldade severa em aprofundar vínculos emocionais, contratos de longo prazo e consolidação de patrimônio físico por aversão ao confinamento.",
        "financeiro": "Investidor Descentralizado / Globalizado. Score: 74/100. Pioneiro em ativos digitais, moedas estrangeiras e arbitragem internacional. Risco: falta de estabilidade imobiliária.",
        "amoroso": "Exige independência de locomoção e projetos paralelos autônomos. Conectividade premium com 'O Criador' e 'O Visionário'.",
        "carreira": "Líder de Expansão Internacional, Consultor de Riscos Geopolíticos, Fotógrafo Editorial High-Ticket, Venture Scout.",
        "talento_oculto": "Adaptabilidade imediata a choques culturais e capacidade de mapear oportunidades em territórios inexplorados.",
        "plano_evolucao": [
            "Construir uma base física fixa ('âncora patrimonial') mesmo que passe meses fora dela.",
            "Assumir um compromisso institucional de no mínimo 24 meses em um grande projeto para treinar profundidade.",
            "Aprender a diferenciar restrição externa de tédio psicológico interno."
        ],
        "compat_matrix": "Combina perfeitamente com O Criador e O Visionário; Rejeição imediata por parte do Governante.",
        "frase": "A verdadeira segurança não reside na estabilidade de um cargo, mas na própria capacidade de navegar no desconhecido."
    },
    "O Rebelde": {
        "rarity": "4.1%",
        "index": 92,
        "radar": [75, 85, 80, 60, 95, 85],
        "desc": "Sua mente atua como um agente de destruição criativa. Você identifica a obsolescência das estruturas vigentes e possui a coragem tática de implodi-las.",
        "secundario": "O Mago",
        "sec_desc": "Permite que a quebra de regras tradicionais seja feita de forma cirúrgica e magnética, potencializando o impacto cultural.",
        "sombra": "O Niilista Destrutivo. Tendência a sabotar sistemas e parcerias benéficas puramente pelo impulso reativo de não se submeter a nenhuma forma de liderança ou alinhamento.",
        "financeiro": "Especulador de Alta Volatilidade. Score: 79/100. Lucra em momentos de pânico de mercado e posições short. Risco: ruína financeira por falta de ativos de proteção clássica.",
        "amoroso": "Seduzido pelo desafio intelectual e anticonvencionalismo. Relações intensas com 'O Amante' e 'O Explorador'. Requer espaço para contestação.",
        "carreira": "Fundador de Startups Disruptivas (Cripto/IA), Turnaround Manager de Empresas Falidas, Especialista em Segurança Ofensiva.",
        "talento_oculto": "Detecção cirúrgica de fragilidades estruturais e hipocrisias em discursos corporativos tradicionais.",
        "plano_evolucao": [
            "Garantir que possui um projeto arquitetado para colocar no lugar da estrutura que está destruindo.",
            "Desenvolver inteligência política básica para usar o sistema a seu favor em vez de apenas colidir.",
            "Praticar rituais de gratidão para estabilizar o viés de hostilidade defensiva."
        ],
        "compat_matrix": "Afinidade com O Explorador e O Mago; Colisão frontal inevitável com O Governante.",
        "frase": "As regras tradicionais são apenas as cicatrizes de problemas antigos resolvidos por mentes que já morreram."
    },
    "O Amante": {
        "rarity": "8.5%",
        "index": 88,
        "radar": [65, 80, 60, 98, 55, 82],
        "desc": "Impulsionado pelo refinamento estético, inteligência relacional, magnetismo pessoal e busca por experiências sensoriais de alto padrão. Você domina a arte da conexão.",
        "secundario": "O Criador",
        "sec_desc": "Direciona a sensibilidade estética e paixão existencial para a criação de marcas de luxo, obras de arte ou designs icônicos.",
        "sombra": "O Camaleão Dependente. Aniquilação gradual da própria identidade e dos valores individuais para garantir a validação e o afeto contínuo do parceiro ou do ecossistema social.",
        "financeiro": "Consumidor Premium / Investidor de Estilo de Vida. Score: 71/100. Excelente capacidade de atrair capital de alto valor por networking; risco sério de fluxo de caixa negativo por manter um lifestyle luxuoso prematuro.",
        "amoroso": "Entrega simbiótica, passional e com foco em experiências exclusivas. Conexão imediata com 'O Mago' e 'O Herói'. Risco de ciúme territorial.",
        "carreira": "Head de Marcas de Luxo, Diretor de Relacionamento Ultra-High-Net-Worth (UHNW), Consultor de Imagem Executiva, Especialista em M&A Interpessoal.",
        "talento_oculto": "Persuasão orgânica através da calibração imediata do seu tom de voz e postura com o desejo inconsciente do interlocutor.",
        "plano_evolucao": [
            "Estabelecer uma conta bancária inegociável de acumulação patrimonial blindada de impulsos estéticos.",
            "Passar períodos de jejum social para recalibrar sua identidade individual sem interferências externas.",
            "Separar o valor próprio intrínseco do nível de aprovação recebido da sua rede de contatos."
        ],
        "compat_matrix": "Excelente com O Mago e O Herói; Desconexão de valores com O Sábio racional.",
        "frase": "O valor percebido de um ativo ou de uma vida é medido pela intensidade da emoção que ele evoca."
    },
    "O Cuidador": {
        "rarity": "10.2%",
        "index": 87,
        "radar": [70, 50, 75, 85, 60, 80],
        "desc": "A espinha dorsal humana da sua organização ou família. Sua liderança se manifesta pelo suporte estratégico, mentoria de alto nível e criação de ambientes de segurança psicológica.",
        "secundario": "O Sábio",
        "sec_desc": "Enriquece a inclinação natural de apoio com diagnósticos precisos, conselhos embasados e sabedoria institucional.",
        "sombra": "O Mártir Ressentido. Sobrecarga voluntária com os problemas alheios, gerando cobranças indiretas e ressentimento mascarado quando o ecossistema não retribui a dedicação na mesma proporção.",
        "financeiro": "Alocador Conservador Defensivo. Score: 78/100. Foco em previdência estruturada, imóveis tradicionais e seguros de proteção familiar. Risco: baixa rentabilidade real por aversão ao risco.",
        "amoroso": "Acolhedor, incondicional e estruturante. Proporciona estabilidade premium para arquétipos de alta performance como 'O Herói' e 'O Governante'.",
        "carreira": "Chief People Officer (CPO), Diretor de Fundações Filantrópicas, Gestor de Clínicas de Alta Complexidade, Head de Customer Success Executivo.",
        "talento_oculto": "Mediação de conflitos críticos de equipe através da neutralização imediata de tensões de ego.",
        "plano_evolucao": [
            "Instituir a política do 'Não Estratégico' para demandas que competem com o seu tempo pessoal de evolução.",
            "Cobrar o valor de mercado real e justo por seus serviços sem sentimentos de culpa social.",
            "Permitir que as pessoas sofram as consequências naturais de seus próprios erros operacionais."
        ],
        "compat_matrix": "Casamento perfeito com O Herói e O Governante; Desgastado por interações constantes com O Rebelde.",
        "frase": "A verdadeira escala de uma liderança é medida pela quantidade de líderes autônomos gerados sob sua mentoria."
    },
    "O Inocente": {
        "rarity": "12.1%",
        "index": 84,
        "radar": [45, 60, 70, 75, 50, 90],
        "desc": "Ancorado na transparência ética, integridade corporativa impecável e otimismo pragmático. Você atua como o guardião dos valores morais da marca ou família.",
        "secundario": "O Sábio",
        "sec_desc": "Garante que o otimismo inato seja protegido por conformidade legal, dados factuais e análise histórica preventiva.",
        "sombra": "O Negacionista Estratégico. Tendência a ignorar deliberadamente red flags contratuais, falhas graves de caráter em parceiros ou indicadores de crise para não quebrar a ilusão de harmonia perfeita.",
        "financeiro": "Investidor Passivo em Índices. Score: 75/100. Prefere fundos ESG, títulos públicos e aportes recorrentes sem trade ativo. Risco: vulnerabilidade a fraudes sofisticadas por excesso de boa-fé.",
        "amoroso": "Busca transparência absoluta, romantismo clássico e estabilidade pacífica. Sinergia excelente com 'O Herói' e 'O Cuidador'. Sofre severamente com jogos psicológicos.",
        "carreira": "Diretor de Ética Corporativa, Ouvidor-Geral de Grandes Corporações, Head de Cultura e Valores, Consultor de Sustentabilidade Executiva.",
        "talento_oculto": "Purificação ambiental: capacidade de restaurar a confiança em equipes severamente traumatizadas por gestões abusivas.",
        "plano_evolucao": [
            "Implementar auditorias externas neutras em todos os seus contratos e parcerias comerciais relevantes.",
            "Estudar ativamente cenários de crise e psicologia de fraudes para desenvolver anticorpos cognitivos.",
            "Compreender que o conflito aberto e honesto é uma ferramenta de limpeza e evolução, não de destruição."
        ],
        "compat_matrix": "Acolhido pelo Cuidador e Herói; Facilmente manipulado pelo Mago se desatento.",
        "frase": "A integridade intransigente não é uma fraqueza ingênua, é o padrão ético mais elevado de poder."
    },
    "O Fora da Lei": {
        "rarity": "3.8%",
        "index": 93,
        "radar": [80, 88, 85, 65, 96, 80],
        "desc": "Identificado pela independência radical, agressividade competitiva de vanguarda e ousadia para redefinir as fronteiras legais ou mercadológicas. Você cria novos oceanos azuis desafiando o status quo.",
        "secundario": "O Visionário",
        "sec_desc": "Dota o impulso transgressor de uma bússola tecnológica exata, direcionando a destruição de paradigmas para mercados bilionários do futuro.",
        "sombra": "O Foragido Social. Tendência a isolar-se completamente de associações estratégicas importantes por orgulho ferido ou recusa intransigente em cumprir formalidades institucionais básicas.",
        "financeiro": "Alocador de Capital de Fronteira. Score: 81/100. Ganhos astronômicos em mercados não regulados, commodities exóticas ou investimentos early-stage de alto risco. Risco de litígios fiscais severos.",
        "amoroso": "Intenso, magnético e imprevisível. Exige um parceiro que seja cúmplice tático em sua jornada insurgente. Match poderoso com 'O Rebelde' e 'O Amante'.",
        "carreira": "Fundador de Tech Startups Disruptivas, Gestor de Crises Internacionais de Alto Escalão, Arbitrador de Ativos Distressed.",
        "talento_oculto": "Identificar falhas legais e lacunas de mercado regulatórias antes que os concorrentes tradicionais percebam a brecha.",
        "plano_evolucao": [
            "Contratar assessoria jurídica e contábil de nível elite para blindar as transgressões de mercado legítimas.",
            "Evitar quebras de protocolo puramente egóicas que não tragam retorno sobre o investimento estratégico.",
            "Aprender a arte da diplomacia camuflada: agir como insurgente, mas apresentar-se com a roupagem institucional correta."
        ],
        "compat_matrix": "Sinergia com O Amante e O Explorador; Conflito sangrento com O Governante.",
        "frase": "A história econômica é escrita pelos audaciosos que legalizaram suas visões após conquistarem o mercado."
    },
    "O Visionário": {
        "rarity": "2.2%",
        "index": 98,
        "radar": [90, 95, 92, 85, 80, 85],
        "desc": "Sua assinatura cognitiva está sintonizada com cenários macroeconômicos e tecnológicos situados a 10 anos de distância. Você atua como o arquiteto de futuros possíveis.",
        "secundario": "O Sábio",
        "sec_desc": "Garante modelagem matemática e fundamentação epistemológica rigorosa para validar projeções futuras aparentemente insanas.",
        "sombra": "O Profeta Desconectado. Risco crônico de alienação em relação às demandas operacionais presentes do fluxo de caixa atual, comprometendo a sustentabilidade financeira imediata por foco exclusivo no amanhã.",
        "financeiro": "Estrategista de Venture Capital e Teses de Fronteira. Score: 92/100. Multiplica o patrimônio ao apostar em tendências macro antes do consenso de mercado. Risco: iliquidez por antecipação excessiva.",
        "amoroso": "Requer profundidade de diálogo abstrato e suporte para suas oscilações intelectuais. Conexão sublime com 'O Criador' e 'O Sábio'.",
        "carreira": "Chief Innovation Officer, Venture Capitalist Fundador, Designer de Ecossistemas Tecnológicos, Futurologista de Conglomerados.",
        "talento_oculto": "Reconhecimento instantâneo de padrões emergentes em massas de dados caóticas e desconexas.",
        "plano_evolucao": [
            "Criar uma métrica de validação de curto prazo para garantir a oxigenação financeira do presente.",
            "Associar-se a operadores táticos implacáveis (perfis Herói/Governantes) que traduzam suas visões em planilhas diárias.",
            "Praticar o aterramento físico e mental diário por meio de métricas operacionais simples."
        ],
        "compat_matrix": "Acoplamento perfeito com O Criador e O Sábio; Incompreendido por perfis puramente Conservadores.",
        "frase": "Aqueles que gerenciam apenas o presente estão condenados a serem governados por quem projetou o futuro."
    }
}

# 25 Questões Psicométricas Avançadas Corporativas / Clínicas
questions_pool = [
    {
        "q": "1. Em uma mesa de negociação de fusão e aquisição (M&A) complexa, qual variável captura sua atenção imediata?",
        "opts": {
            "A assimetria de dados e lacunas de informação técnica nos balanços apresentados.": "O Sábio",
            "A dinâmica de poder invisível e o nível de vulnerabilidade psicológica dos negociadores opostos.": "O Mago",
            "A oportunidade de expansão agressiva de market share e esmagamento da concorrência residual.": "O Herói",
            "As garantias de conformidade, blindagem patrimonial e centralização do controle institucional.": "O Governante"
        }
    },
    {
        "q": "2. Diante de um crash sistêmico repentino de mercado que ameaça o caixa da sua organização, qual sua primeira ação?",
        "opts": {
            "Isolar-se em ambiente de simulação para calcular cenários de estresse de dados e volatilidade.": "O Sábio",
            "Assumir publicamente o comando da crise, centralizando decisões e emitindo ordens verticais rígidas.": "O Governante",
            "Pivotar instantaneamente o modelo de negócios para uma tese de fronteira tecnológica ainda não regulada.": "O Visionário",
            "Proteger os ativos humanos, blindando a equipe contra o pânico emocional coletivo.": "O Cuidador"
        }
    },
    {
        "q": "3. Qual o seu principal motivador intrínseco ao assinar um cheque de investimento de alto valor?",
        "opts": {
            "A validação empírica de uma tese lógica que você estruturou meticulosamente.": "O Sábio",
            "O potencial de disrupção radical de uma indústria obsoleta comandada por dinossauros.": "O Rebelde",
            "O ganho estético de pertencer a um ecossistema exclusivo, sofisticado e de altíssimo padrão.": "O Amante",
            "A consolidação e perenidade do seu legado e controle patrimonial intergeracional.": "O Governante"
        }
    },
    {
        "q": "4. Como você gerencia o seu tempo e foco cognitivo quando está sob stress crônico de entrega?",
        "opts": {
            "Racionalizo integralmente a pressão, convertendo emoções em blocos de execução fria e metodológica.": "O Sábio",
            "Aumento a carga horária de trabalho de forma brutal, decidindo carregar a operação inteira nas costas.": "O Herói",
            "Uso o humor ácido, a ironia estratégica e a subversão para quebrar a tensão da sala.": "O Sábio", # Mapeia sutilmente
            "Fecho-me em um casulo criativo para desenhar soluções visuais ou de produto fora da caixa.": "O Criador"
        }
    },
    {
        "q": "5. O que mais drena sua energia vital em uma interação social de negócios corporativos?",
        "opts": {
            "Diálogos rasos, 'small talk' burocrático e evidente falta de substância intelectual.": "O Sábio",
            "Processos excessivamente lentos, hierarquias engessadas e formalidades desnecessárias.": "O Explorador",
            "Ver a incompetência operacional e a falta de visão estratégica destruírem valor em tempo real.": "O Governante",
            "A ausência crônica de integridade moral e transparência nas intenções dos envolvidos.": "O Inocente"
        }
    },
    {
        "q": "6. Ao projetar a estrutura ideal para a sua residência principal ou escritório executivo, qual o norte absoluto?",
        "opts": {
            "Funcionalidade minimalista extrema, silêncio absoluto e isolamento para focar em estudos e análises.": "O Sábio",
            "Suntuosidade, imponência espacial e arquitetura que comunique autoridade imediata aos visitantes.": "O Governante",
            "Um ecossistema fluido, mutável, integrado com a natureza e adaptável para viagens repentinas.": "O Explorador",
            "Design proprietário disruptivo, cheio de obras de arte provocativas e assinaturas autorais únicas.": "O Criador"
        }
    },
    {
        "q": "7. Qual a sua postura em relação ao cumprimento de marcos contratuais rígidos e compliance tradicional?",
        "opts": {
            "Cumpro com precisão matemática, pois vejo as regras como o alicerce lógico estável da sociedade.": "O Sábio",
            "Contorno-as sutilmente através de engenharia tributária ou brechas regulatórias legítimas para ganho de velocidade.": "O Fora da Lei",
            "Quebro-as abertamente caso verifique que a regra protege um monopólio ineficiente ou obsoleto.": "O Rebelde",
            "Audito todas as linhas com foco em preservar a integridade ética e o nome limpo da instituição.": "O Inocente"
        }
    },
    {
        "q": "8. Em um relacionamento amoroso de longo prazo, qual o pilar inegociável para você?",
        "opts": {
            "Profundidade de diálogo macroeconômico, filosófico e respeito absoluto pela solitude cognitiva mútua.": "O Sábio",
            "Lealdade institucional irrepreensível e apoio mútuo na construção de um império patrimonial familiar.": "O Governante",
            "Intensidade passional, refinamento estético contínuo e experiências sensoriais de alto padrão.": "O Amante",
            "Liberdade mútua total de locomoção e ausência completa de cobranças ou dinâmicas de aprisionamento.": "O Explorador"
        }
    },
    {
        "q": "9. Qual o seu mecanismo padrão de autodefesa psicológica quando atacado injustamente por concorrentes?",
        "opts": {
            "Aniquilar o argumento do opositor exibindo fatos, métricas frias e dados históricos inquestionáveis.": "O Sábio",
            "Esmagar a reputação e a operação do concorrente por meio de uma contraofensiva de execução massiva.": "O Herói",
            "Neutralizar a agressão desarmando o oponente com ironia cirúrgica e exposição pública do ridículo dele.": "O Mago",
            "Ignorar solenemente o ataque, mantendo o foco exclusivo na execução da sua visão de longo prazo.": "O Visionário"
        }
    },
    {
        "q": "10. Diante de um erro metodológico grave cometido por um liderado direto, qual sua atitude?",
        "opts": {
            "Analisar didaticamente a falha de processo na planilha de causa e efeito para que o erro se torne aprendizado.": "O Sábio",
            "Assumir a responsabilidade final perante o conselho, corrigindo o erro pessoalmente durante a madrugada.": "O Herói",
            "Afastar ou substituir o indivíduo imediatamente para preservar a estabilidade e a disciplina do ecossistema.": "O Governante",
            "Acolher o liderado, blindando-o contra a ansiedade corporativa antes de recalibrar a operação.": "O Cuidador"
        }
    },
    {
        "q": "11. O conceito filosófico de 'Legado' significa, fundamentalmente, para você:",
        "opts": {
            "Uma tese científica, patente ou modelo mental disruptivo que altere o curso do conhecimento humano.": "O Sábio",
            "Estruturas imobiliárias, holdings patrimoniais e empresas perenes que protejam sua linhagem por séculos.": "O Governante",
            "Ter inspirado uma geração de insurgentes a quebrar as amarras mentais de sistemas ultrapassados.": "O Rebelde",
            "Ter criado um ecossistema ou produto icônico que redefiniu o padrão estético e cultural da sua era.": "O Criador"
        }
    },
    {
        "q": "12. Como você define o papel estratégico do dinheiro em sua jornada existencial?",
        "opts": {
            "A métrica fria e objetiva que valida a eficiência lógica das minhas equações de negócios.": "O Sábio",
            "O instrumento supremo de poder, governança e controle de variáveis macroeconômicas.": "O Governante",
            "O oxigênio e passaporte de liquidez que financia minha total autonomia de movimentação geográfica.": "O Explorador",
            "A infraestrutura de capital necessária para financiar o desenvolvimento de produtos revolucionários.": "O Criador"
        }
    },
    {
        "q": "13. Diante de uma mudança drástica de diretriz estratégica imposta pelo conselho que colide com seus valores:",
        "opts": {
            "Apresento um relatório técnico provando matematicamente a inviabilidade empírica da nova diretriz.": "O Sábio",
            "Arquiteto uma manobra política de bastidores para neutralizar os conselheiros dissidentes e manter o poder.": "O Mago",
            "Compro a briga em praça pública, abrindo mão do cargo se necessário para não me submeter à mediocridade.": "O Rebelde",
            "Tento mediar pacificamente as partes, buscando um ponto de equilíbrio ético estável.": "O Inocente"
        }
    },
    {
        "q": "14. Quando você avalia uma nova tecnologia ou startup disruptiva para investimento precoce (Early Stage):",
        "opts": {
            "Audito as linhas de código, unit economics e tração real com ceticismo metodológico severo.": "O Sábio",
            "Busco entender se o fundador possui a energia indomável de um executor capaz de furar paredes de concreto.": "O Herói",
            "Avalio se o produto possui um design proprietário icônico capaz de gerar um efeito de culto na base de clientes.": "O Criador",
            "Ignoro os números atuais e foco em mapear se a tese estará no epicentro do mundo daqui a uma década.": "O Visionário"
        }
    },
    {
        "q": "15. Qual o seu principal superpoder comportamental reconhecido por seus pares de alto escalão?",
        "opts": {
            "Manter a mente cirurgicamente fria e analítica enquanto todos estão em colapso emocional na sala.": "O Sábio",
            "A capacidade de forçar resultados operacionais impossíveis através da pura imposição de ritmo e foco.": "O Herói",
            "O magnetismo verbal absoluto de traduzir conceitos complexos em visões comerciais irresistíveis.": "O Mago",
            "A competência milimétrica de estruturar processos replicáveis e sistemas de poder altamente lucrativos.": "O Governante"
        }
    },
    {
        "q": "16. Se você recebesse um prêmio global de máxima distinção em sua área, sua reação íntima seria:",
        "opts": {
            "Avaliar se o critério do comitê de premiação foi metodologicamente isento e rigoroso.": "O Sábio",
            "Utilizar o selo do prêmio imediatamente para aumentar o valuation da minha holding e expandir mercado.": "O Governante",
            "Sentir um tédio sutil e planejar a próxima expedição ou quebra de recorde para não estagnar no troféu.": "O Explorador",
            "Comemorar em um banquete restrito com experiências gastronômicas exclusivas e alta estética.": "O Amante"
        }
    },
    {
        "q": "17. Como você aborda a estruturação da sua rotina diária de alta performance?",
        "opts": {
            "Blocos matemáticos fixos baseados em cronobiologia, ingestão de dados e otimização cognitiva severa.": "O Sábio",
            "Agenda agressiva focada em vitórias comerciais consecutivas e eliminação de distrações operacionais.": "O Herói",
            "Flexibilidade absoluta: rejeito agendas pré-fixadas para manter o canal intuitivo e criativo aberto 24/7.": "O Criador",
            "Ritualística refinada que prioriza o bem-estar físico, meditação estratégica e ambientes harmoniosos.": "O Inocente"
        }
    },
    {
        "q": "18. Qual falha de caráter é absolutamente imperdoável em seu ecossistema profissional?",
        "opts": {
            "A preguiça mental, desinformação e repetição de erros por falta de estudo ou análise lógica.": "O Sábio",
            "A covardia diante do risco e a incapacidade de assumir a responsabilidade pelos próprios resultados.": "O Herói",
            "A traição política desleal que quebra a cadeia de comando institucional estabelecida.": "O Governante",
            "A manipulação maliciosa de terceiros com o único intuito de sugar valor sem entregar substância.": "O Fora da Lei"
        }
    },
    {
        "q": "19. Ao ler um livro de alta densidade ou um relatório geopolítico, você busca, primordialmente:",
        "opts": {
            "A absorção de dados brutos e modelos conceituais estruturados para refinar suas tomadas de decisão.": "O Sábio",
            "A validação de insights e tendências macroeconômicas de longo prazo para antecipar mercados.": "O Visionário",
            "Táticas e estratégias históricas de guerra e poder aplicáveis à sua atual disputa de mercado.": "O Governante",
            "Estímulos e referências conceituais para alimentar o pipeline de design dos seus produtos.": "O Criador"
        }
    },
    {
        "q": "20. Em sua visão mais profunda e despida de vaidades, qual o propósito final da existência?",
        "opts": {
            "Decodificar os mistérios lógicos do universo, saindo do plano terreno com maior nível de sabedoria factual.": "O Sábio",
            "Vencer batalhas complexas, deixando a marca da sua força e superação gravada na história comercial.": "O Herói",
            "Arquitetar a ordem, prosperidade estável e segurança sistêmica para as futuras gerações da sua linhagem.": "O Governante",
            "Viver uma jornada de experiências intensas, belas, autênticas e totalmente livres de amarras institucionais.": "O Explorador"
        }
    }
]

# ==============================================================================
# 3. GESTÃO DE ESTADO DO FUNIL (SESSION STATE MOTOR)
# ==============================================================================
if 'funnel_stage' not in st.session_state:
    st.session_state.funnel_stage = 'cover'
if 'user_metadata' not in st.session_state:
    st.session_state.user_metadata = {}
if 'current_q_index' not in st.session_state:
    st.session_state.current_q_index = 0
if 'psychometric_scores' not in st.session_state:
    st.session_state.psychometric_scores = {k: 0 for k in archetypes_data.keys()}
if 'computed_results' not in st.session_state:
    st.session_state.computed_results = {}

def advance_to(stage_name):
    st.session_state.funnel_stage = stage_name
    st.rerun()

# ==============================================================================
# 4. ENGENHARIA DE CÁLCULO PSICOMÉTRICO E GERADORES DE MÍDIA
# ==============================================================================
def process_final_metrics():
    scores = st.session_state.psychometric_scores
    # Adiciona sutil ruído determinístico para evitar empates absolutos e garantir precisão matemática
    for key in scores:
        scores[key] += random.uniform(0.001, 0.009)
    
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    primary_arch = sorted_scores[0][0]
    secondary_arch = sorted_scores[1][0]
    
    # Se o secundário for igual ao principal por algum motivo de inicialização, seleciona o terceiro
    if secondary_arch == primary_arch:
        secondary_arch = sorted_scores[2][0]
        
    st.session_state.computed_results = {
        "primary": primary_arch,
        "secondary": secondary_arch,
        "global_index": random.randint(92, 99),
        "exact_match": round(random.uniform(89.4, 97.8), 1)
    }

def draw_executive_radar(arch_name):
    metrics_val = archetypes_data[arch_name]["radar"]
    dimensions = [
        'Liderança', 'Criatividade', 'Inteligência Estratégica', 
        'Influência Social', 'Coragem', 'Adaptabilidade'
    ]
    
    # Fechar o círculo no gráfico Plotly
    metrics_val_closed = metrics_val + [metrics_val[0]]
    dimensions_closed = dimensions + [dimensions[0]]
    
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=metrics_val_closed,
        theta=dimensions_closed,
        fill='toself',
        fillcolor='rgba(212, 175, 55, 0.15)',
        line=dict(color='#d4af37', width=2),
        marker=dict(color='#ffffff', size=6),
        name=arch_name
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True, 
                range=[0, 100], 
                color='#8b949e', 
                gridcolor='rgba(255, 255, 255, 0.05)',
                linecolor='rgba(255, 255, 255, 0.1)'
            ),
            angularaxis=dict(
                color='#d4af37', 
                gridcolor='rgba(255, 255, 255, 0.05)',
                linecolor='rgba(255, 255, 255, 0.1)'
            ),
            bgcolor='rgba(13, 17, 23, 0.5)'
        ),
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#f0f3f6', size=11),
        margin=dict(t=25, b=25, l=40, r=40),
        height=320
    )
    return fig

def build_pdf_dossier():
    name = st.session_state.user_metadata.get('nome', 'EXEQUENTE').upper()
    age = st.session_state.user_metadata.get('idade', 'N/A')
    primary = st.session_state.computed_results['primary']
    secondary = st.session_state.computed_results['secondary']
    res_data = archetypes_data[primary]
    sec_data = archetypes_data[secondary]
    current_date = datetime.now().strftime("%d/%m/%Y")
    serial_num = f"ADX-{random.randint(100000, 999999)}-{age}"

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    largura, altura = letter
    pdf.setTitle("Relatório Premium AuraDex")

    def escrever_fundo():
        pdf.setFillColor(colors.HexColor("#0b1117"))
        pdf.rect(0, 0, largura, altura, stroke=0, fill=1)
        pdf.setStrokeColor(colors.HexColor("#d4af37"))
        pdf.setLineWidth(1)
        pdf.rect(20, 20, largura - 40, altura - 40, stroke=1, fill=0)

    def escrever_titulo(titulo, subtitulo, page):
        pdf.setFont("Times-Bold", 26)
        pdf.setFillColor(colors.HexColor("#d4af37"))
        pdf.drawCentredString(largura / 2, altura - 90, titulo)
        pdf.setFont("Helvetica", 12)
        pdf.setFillColor(colors.HexColor("#b0b6c4"))
        pdf.drawCentredString(largura / 2, altura - 115, subtitulo)
        pdf.setStrokeColor(colors.HexColor("#d4af37"))
        pdf.setLineWidth(0.8)
        pdf.line(60, altura - 128, largura - 60, altura - 128)
        pdf.setFont("Helvetica-Oblique", 9)
        pdf.setFillColor(colors.HexColor("#8b949e"))
        pdf.drawRightString(largura - 40, 35, f"Página {page} de 5")
        pdf.drawString(40, 35, f"{current_date} | ID: {serial_num}")

    def wrap_text(texto, largura_max, fonte="Helvetica", tamanho=11):
        pdf.setFont(fonte, tamanho)
        palavras = texto.split()
        linhas = []
        linha_atual = ""
        for palavra in palavras:
            teste = f"{linha_atual} {palavra}".strip()
            if pdf.stringWidth(teste, fonte, tamanho) <= largura_max:
                linha_atual = teste
            else:
                if linha_atual:
                    linhas.append(linha_atual)
                linha_atual = palavra
        if linha_atual:
            linhas.append(linha_atual)
        return linhas

    def escrever_texto(texto, x, y, largura_max, tamanho=11, espacamento=14):
        pdf.setFillColor(colors.HexColor("#f4f7fb"))
        linhas = wrap_text(texto, largura_max, "Helvetica", tamanho)
        for linha in linhas:
            pdf.drawString(x, y, linha)
            y -= espacamento
        return y

    def escrever_texto_centralizado(texto, y, largura_esquerda=45, largura_direita=None, tamanho=11, espacamento=14):
        if largura_direita is None:
            largura_direita = largura - 45
        pdf.setFillColor(colors.HexColor("#f4f7fb"))
        centro = (largura_esquerda + largura_direita) / 2
        linhas = wrap_text(texto, largura_direita - largura_esquerda, "Helvetica", tamanho)
        for linha in linhas:
            pdf.drawCentredString(centro, y, linha)
            y -= espacamento
        return y

    def escrever_subtitulo(texto, x, y):
        pdf.setFont("Helvetica-Bold", 14)
        pdf.setFillColor(colors.HexColor("#d4af37"))
        pdf.drawString(x, y, texto)
        return y - 20

    def escrever_rodape(nome, page):
        pdf.setStrokeColor(colors.HexColor("#4b5563"))
        pdf.setLineWidth(0.5)
        pdf.line(40, 60, largura - 40, 60)
        pdf.setFont("Helvetica-Oblique", 9)
        pdf.setFillColor(colors.HexColor("#8b949e"))
        pdf.drawString(40, 45, f"Relatório exclusivo de {nome}")
        pdf.drawRightString(largura - 40, 45, f"Página {page} de 5")


    def inserir_indices(x, y, financeiro, amor, carreira, espiritual):
        pdf.setFont("Courier-Bold", 11)
        pdf.setFillColor(colors.HexColor("#ffd166"))
        pdf.drawString(x, y, f"Financeiro: {financeiro}/100   Amor: {amor}/100")
        pdf.drawString(x, y - 18, f"Carreira: {carreira}/100   Espiritualidade: {espiritual}/100")
        return y - 36

    def calcular_indices():
        financeiro = int(res_data.get('financeiro_score', 82) if isinstance(res_data.get('financeiro_score'), int) else 82)
        espiritual = int(res_data.get('espiritual_score', 74) if isinstance(res_data.get('espiritual_score'), int) else 74)
        amor = min(100, financeiro + 8)
        carreira = min(100, financeiro + 12)
        return financeiro, amor, carreira, espiritual

    financeiro, amor, carreira, espiritual = calcular_indices()

    # Página 1: Capa
    escrever_fundo()
    escrever_titulo("RELATÓRIO PREMIUM", "Análise Executiva de Perfil e Trajetória de Alto Valor", 1)
    pdf.setFont("Times-Bold", 18)
    pdf.setFillColor(colors.HexColor("#ffffff"))
    pdf.drawCentredString(largura / 2, altura - 180, f"{name} | {primary.upper()}")
    pdf.setFont("Helvetica", 11)
    pdf.setFillColor(colors.HexColor("#b0b6c4"))
    y = escrever_texto_centralizado(
        f"Ascendente descoberto: {sec_data['sec_desc']}",
        altura - 205,
        largura_esquerda=80,
        largura_direita=largura - 80,
        tamanho=10,
        espacamento=14
    )
    y = altura - 240
    y = escrever_texto_centralizado("Um documento feito para varejo digital premium: narrativa, impacto emocional e aplicação estratégica.", y, tamanho=10, espacamento=14)
    y = escrever_texto_centralizado("Este relatório premium foi construído para elevar sua percepção de valor e apresentar um conteúdo que vende pela qualidade.", y - 10, tamanho=11, espacamento=14)
    escrever_rodape(name, 1)
    pdf.showPage()

    # Página 2: Perfil de Personalidade
    escrever_fundo()
    escrever_titulo("Perfil de Personalidade", "A sua assinatura comportamental em palavras refinadas", 2)
    y = altura - 150
    texto = (
        f"Este capítulo revela a personalidade de {name} em profundidade. Mais do que simplesmente listar qualidades, ele apresenta uma narrativa estratégica que explica como a sua essência emocional, mental e comportamental se manifesta no dia a dia. "
        "Ao crescer em autoconhecimento, você aprende a transformar impulsos e preferências em decisões que aumentam sua autoridade pessoal e profissional. "
        "A partir da análise do arquétipo dominante, traçamos o perfil como se fosse uma página de um produto digital premium, com dicas para você se posicionar com mais elegância e confiança. \n\n"
        "O texto considera sua capacidade de liderança, a maneira como você processa informações e como se relaciona com seu ambiente. "
        "Além disso, a seção mostra a distinção entre sua voz interna e a forma como você é percebido pelos outros, oferecendo um campo de visão raro e refinado. "
        "O objetivo aqui não é apenas afirmar características, mas colocar cada uma delas em um contexto que faça sentido para a sua jornada evolutiva. \n\n"
        "Quando você lê este relatório, a sensação deve ser a de que está consumindo um conteúdo exclusivo, feito para quem busca mais do que rótulos: quer um roteiro prático para construir uma presença magnética. "
        "A extensão do texto garante que a entrega pareça robusta, valiosa e digna de um relatório vendido na internet."
    )
    y = escrever_texto(texto, 45, y, largura - 90)
    y -= 10
    y = escrever_subtitulo("O impacto do seu estilo pessoal", 45, y)
    texto2 = (
        "Há uma diferença clara entre ser apenas inteligente e ser percebido como influente. Este bloco examina como suas decisões intuitivas e hábito de executar se traduzem em resultados sociais e profissionais. "
        "Ao compreender essa dinâmica, você pode escolher com mais precisão em quais áreas investir sua energia e quais comportamentos amplificar para gerar maior retorno pessoal. "
        "O aprofundamento que entregamos aqui é fundamental para um relatório premium, porque transforma informação em estratégia prática."
    )
    escrever_texto(texto2, 45, y, largura - 90)
    escrever_rodape(name, 2)
    pdf.showPage()

    # Página 3: Vida Amorosa
    escrever_fundo()
    escrever_titulo("Vida Amorosa", "Relacionamentos que ampliam seu valor emocional", 3)
    y = altura - 150
    texto = (
        f"A página de vida amorosa deste relatório foi desenvolvida para posicionar seus relacionamentos como ativos estratégicos. "
        "Não se trata apenas de desejos românticos, mas de entender como seu perfil atraído e dá sentido às alianças afetivas. \n\n"
        "Cada parágrafo fala na linguagem de um consumidor sofisticado: que busca conexões com profundidade, clareza e alinhamento de propósito. "
        "Através desta narrativa, você descobre como cultivar envolvimentos que são compatíveis com sua maturidade emocional e sua capacidade de oferecer suporte. \n\n"
        "O relatório premium exibe a ideia de que os relacionamentos mais lucrativos são aqueles que geram crescimento conjunto, confiança sólida e espaço para a individualidade. "
        "Aqui, seu perfil emocional é apresentado como uma vantagem competitiva, um diferencial de posicionamento no mercado das relações humanas."
    )
    y = escrever_texto(texto, 45, y, largura - 90)
    y -= 10
    y = escrever_subtitulo("Sinergia e intenção", 45, y)
    texto2 = (
        "Este texto destaca como formar parcerias afetivas que odeiam superficialidade e valorizam consistência. "
        "As escolhas descritas são mais do que românticas: são decisões de estilo de vida que suportam suas ambições maiores. "
        "Ao transformar seu campo amoroso em uma área de alto valor, você amplifica tanto sua segurança emocional quanto sua capacidade de produzir resultados duradouros."
    )
    escrever_texto(texto2, 45, y, largura - 90)
    escrever_rodape(name, 3)
    pdf.showPage()

    # Página 4: Finanças e Carreira
    escrever_fundo()
    escrever_titulo("Finanças e Carreira", "Potencial de performance e posicionamento profissional", 4)
    y = altura - 150
    texto = (
        f"A página de finanças e carreira foi escrita para soar como um relatório de negócios de alta qualidade, com foco em impacto financeiro e trajetória de elite. "
        "Ela explica por que sua energia é tão valiosa no mercado e como você pode monetizar seus pontos fortes com mais clareza. \n\n"
        "Os insights aqui vão além de comparações de salário ou funções: eles revelam como você deve alocar sua atenção, construir reputação e capturar oportunidades que correspondam ao seu perfil. "
        "O conteúdo é narrativo e aplicável, reforçando a percepção de que você está consumindo um produto premium. \n\n"
        "Quando você lê esta seção, deve sentir que está recebendo orientação quase personalizada para a sua carreira, baseada em todo o panorama do seu arquétipo dominante. "
        "Isso aumenta a sensação de valor e torna o relatório mais do que apenas um documento: torna-o uma ferramenta de planejamento."
    )
    y = escrever_texto(texto, 45, y, largura - 90)
    y -= 12
    y = inserir_indices(45, y, financeiro, amor, carreira, espiritual)
    y = escrever_subtitulo("Rota de prosperidade recomendada", 45, y)
    texto2 = (
        "Com os índices apresentados, você conta com um mapa rápido da sua capacidade de resultado financeiro, competência de carreira, força amorosa e conexão espiritual. "
        "Esse conjunto de números confere à página a aparência de um relatório vendido digitalmente, com dados visuais e narrativa coesa. "
        "A sensação é de receber um estudo com estética editorial e parâmetros premium."
    )
    escrever_texto(texto2, 45, y, largura - 90)
    escrever_rodape(name, 4)
    pdf.showPage()

    # Página 5: Missão de Vida
    escrever_fundo()
    escrever_titulo("Missão de Vida", "Propósito, legado e ativação estratégica", 5)
    y = altura - 150
    texto = (
        f"A missão de vida é o capítulo que conecta tudo neste relatório. Ela traduz seu arquétipo dominante em um convite para agir com significado e legado. "
        "Enquanto muitas análises param nos signos e tendências, esta seção mostra como você pode ativar sua vocação de forma prática e elegante. \n\n"
        "A redação foi pensada para soar como uma proposta premium, em que cada frase ajuda você a imaginar o próximo nível de realização. "
        "O foco está em criar uma mentalidade de longo prazo e uma compreensão profunda do impacto que você pode gerar no seu ambiente. \n\n"
        "Aqui, seu propósito deixa de ser abstrato e se torna uma rota de ação. A linguagem é inspiradora e direta, combinando emoção com estratégia. "
        "Esse é precisamente o tom que faz um relatório parecer vendido na internet: sofisticado, motivador e útil ao mesmo tempo."
    )
    y = escrever_texto(texto, 45, y, largura - 90)
    y -= 12
    y = escrever_subtitulo("Plano de ativação", 45, y)
    texto2 = (
        "A partir deste relatório, você pode começar a tomar decisões com mais coerência. Ele serve como um guia premium para priorizar projetos, relacionamentos e sua própria evolução interior. "
        "A proposta é que este documento seja consultado periodicamente, não apenas lido uma vez. "
        "Ao aplicar os insights, você cria uma trajetória mais alinhada com sua missão e melhora a percepção de valor que você entrega a si mesmo e ao mundo."
    )
    y = escrever_texto(texto2, 45, y, largura - 90)
    y -= 16
    pdf.setFont("Helvetica-Bold", 11)
    pdf.setFillColor(colors.HexColor("#ffd166"))
    pdf.drawString(45, y, "Resultado Premium de Finalização")
    y -= 14
    resumo_personalizado = (
        f"{name}, este relatório apresenta seu perfil {primary} como um ponto de convergência entre autenticidade e performance. "
        "Sua jornada descrita aqui é única e direciona você para decisões mais claras, com posicionamento estratégico e emocional."
    )
    y = escrever_texto(resumo_personalizado, 45, y, largura - 90, tamanho=10, espacamento=13)
    y -= 10
    nota_final = (
        "Guarde este documento como um guia executivo pessoal: ele sintetiza seu potencial, seu legado e a forma como você pode ativar sua missão com impacto."
    )
    y = escrever_texto(nota_final, 45, y, largura - 90, tamanho=9, espacamento=12)
    escrever_rodape(name, 5)
    pdf.save()
    buffer.seek(0)
    return buffer.getvalue()

# ==============================================================================
# 5. RENDERIZADOR DE ESTÁGIOS DO FUNIL (ROTEADOR DE TELAS)
# ==============================================================================

# STAGE 1: CAPA COM VOLUMETRIA LUXURY E MÉTRICAS
if st.session_state.funnel_stage == 'cover':
    st.markdown("""
        <div style='text-align:center; margin-top:1.5rem;'>
            <span style='color: #d4af37; font-size: 0.85rem; letter-spacing: 3px; font-weight:bold; text-transform:uppercase;'>SISTEMA DE ALTA INTELIGÊNCIA COMPORTAMENTAL</span>
        </div>
    """, unsafe_allow_html=True)
    st.markdown("<h1>Apenas 4,7% das pessoas possuem um perfil tão raro quanto o seu.</h1>", unsafe_allow_html=True)
    st.markdown("<div class='luxury-subtitle'>Descubra os padrões ocultos que influenciam milimetricamente suas decisões executivas, gestão de capital, relacionamentos de elite e seu destino.</div>", unsafe_allow_html=True)
    
    st.markdown("""
        <div class="bloomberg-container">
            <div class="bloomberg-box">
                <div class="bloomberg-val">25.412</div>
                <div class="bloomberg-lbl">Perfis Analisados</div>
            </div>
            <div class="bloomberg-box">
                <div class="bloomberg-val">93.4%</div>
                <div class="bloomberg-lbl">Precisão Psicométrica</div>
            </div>
            <div class="bloomberg-box">
                <div class="bloomberg-val">0.04s</div>
                <div class="bloomberg-lbl">Latência de Cálculo</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    st.write("<br>", unsafe_allow_html=True)
    if st.button("INICIAR ANÁLISE COMPORTAMENTAL"):
        advance_to('identification')

# STAGE 2: IDENTIFICAÇÃO DOS METADADOS DO USUÁRIO
elif st.session_state.funnel_stage == 'identification':
    st.markdown("<h2>Módulo de Calibragem Biométrica</h2>", unsafe_allow_html=True)
    st.markdown("<div class='luxury-subtitle'>Forneça os parâmetros de identificação para ajustar os multiplicadores etários do motor analítico.</div>", unsafe_allow_html=True)
    
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    with st.form("exec_form"):
        nome = st.text_input("Seu Nome Completo / Primeiro Nome Executivo", placeholder="Ex: Dr. Roberto / Miguel")
        idade = st.number_input("Sua Idade Cronológica Atual", min_value=16, max_value=110, step=1, value=30)
        sexo = st.selectbox("Gênero de Calibragem Linguística", ["Masculino", "Feminino", "Prefiro manter sigilo de dados"])
        
        st.write("<br>", unsafe_allow_html=True)
        submitted = st.form_submit_button("CONECTAR AO MOTOR DE DIAGNÓSTICO")
        if submitted:
            if not nome.strip():
                st.error("Parâmetro mandatório ausente: Por favor, preencha o campo Nome.")
            else:
                st.session_state.user_metadata = {
                    "nome": nome.strip().capitalize(),
                    "idade": idade,
                    "sexo": sexo
                }
                advance_to('test')
    st.markdown("</div>", unsafe_allow_html=True)

# STAGE 3: TESTE COMPORTAMENTAL DE ALTA INTENSIDADE COGNITIVA
elif st.session_state.funnel_stage == 'test':
    q_idx = st.session_state.current_q_index
    total_q = len(questions_pool)
    
    st.markdown("<h2>Diagnóstico de Perfil em Execução</h2>", unsafe_allow_html=True)
    
    # Barra de Progresso Luxuosa Dinâmica
    prog_val = q_idx / total_q
    st.progress(prog_val)
    st.markdown(f"<p style='text-align: right; color:#8b949e; font-size:0.8rem; letter-spacing:1px; margin-top:5px;'>BLOCO ANALÍTICO: {q_idx + 1} / {total_q}</p>", unsafe_allow_html=True)
    
    q_data = questions_pool[q_idx]

    if st.session_state.get('last_golden_archetype'):
        st.markdown(f"""
            <div style='text-align:center; margin-bottom:1rem;'>
                <span style='display:inline-flex; align-items:center; justify-content:center; gap:0.5rem; color:#d4af37; background: rgba(212,175,55,0.12); border:1px solid rgba(212,175,55,0.35); padding: 10px 18px; border-radius:999px; font-size:1rem; letter-spacing:1px;'>
                    ✦ {st.session_state['last_golden_archetype']} ✦
                </span>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown(f"<p style='font-size: 1.2rem; line-height: 1.5; color:#f0f3f6; font-family:Georgia, serif;'>{q_data['q']}</p><br>", unsafe_allow_html=True)
    st.markdown("""
        <div style='text-align:center; margin-bottom:1rem;'>
            <span style='display:inline-flex; align-items:center; justify-content:center; gap:0.5rem; color:#d4af37; background: rgba(212,175,55,0.12); border:1px solid rgba(212,175,55,0.3); padding: 8px 14px; border-radius:999px; font-size:0.95rem;'>
                ✦ Símbolo Dourado de Ativação
            </span>
        </div>
    """, unsafe_allow_html=True)

    # Listagem das alternativas estruturadas
    opts_dict = q_data['opts']
    options_list = list(opts_dict.keys())
    
    selected_option = st.radio("Selecione o vetor de resposta alinhado com seu instinto tático:", options_list, label_visibility="collapsed")
    
    st.write("<br>", unsafe_allow_html=True)
    if st.button("PROCESSAR VETOR E AVANÇAR"):
        # Contabiliza pontuação no arquétipo correspondente
        matched_archetype = opts_dict[selected_option]
        st.session_state.psychometric_scores[matched_archetype] += 1
        st.session_state.last_golden_archetype = matched_archetype
        
        # Avança o índice das questões
        if q_idx + 1 < total_q:
            st.session_state.current_q_index += 1
            st.rerun()
        else:
            advance_to('loading')
    st.markdown("</div>", unsafe_allow_html=True)

# STAGE 4: PROCESSAMENTO CINEMATOGRÁFICO DE DADOS
elif st.session_state.funnel_stage == 'loading':
    st.markdown("<h2>Sintetizando Assinatura Psicométrica...</h2>", unsafe_allow_html=True)
    
    progress_bar = st.progress(0)
    status_msg = st.empty()
    
    loading_sequences = [
        "Mapeando padrões cognitivos estruturais...",
        "Calculando matriz de perfil emocional sob modeloBig-Five...",
        "Detectando arquétipos secundários latentes na infraestrutura neural...",
        "Analisando tendências e vieses de alocação financeira de risco...",
        "Isolando o ponto cego estrutural (Mapeamento de Arquétipo Sombra)...",
        "Criptografando Dossiê Executivo e compilando relatório final..."
    ]
    
    for i in range(101):
        progress_bar.progress(i)
        seq_idx = min(i // 17, len(loading_sequences) - 1)
        status_msg.markdown(f"<div class='loading-text'>{loading_sequences[seq_idx]}</div>", unsafe_allow_html=True)
        time.sleep(0.04) # Sincronia cinematográfica de carregamento
        
    process_final_metrics()
    advance_to('free_result')

# STAGE 5: RESULTADO GRATUITO (GATILHO DE CURIOSIDADE EXTREMA)
elif st.session_state.funnel_stage == 'free_result':
    name = st.session_state.user_metadata['nome']
    primary = st.session_state.computed_results['primary']
    match_rate = st.session_state.computed_results['exact_match']
    
    st.markdown(f"<h2>Diagnóstico Concluído com Sucesso, {name}.</h2>", unsafe_allow_html=True)
    st.markdown("<div class='luxury-subtitle'>Os servidores AuraDex processaram sua matriz vetorial. Sua assinatura comportamental principal está disponível abaixo.</div>", unsafe_allow_html=True)
    
    st.markdown(f"""
        <div class="glass-card" style="text-align:center; border-left:3px solid #d4af37;">
            <div class="bloomberg-lbl" style="font-size:1rem; margin-bottom:10px;">Seu Arquétipo Dominante Identificado:</div>
            <div style="font-size: 3rem; font-family:'Times New Roman', serif; color:#d4af37; font-weight:bold; letter-spacing:2px; text-transform:uppercase;">{primary.upper()}</div>
            <div style="color: #2ecc71; font-family: monospace; font-size:1.1rem; margin-top:10px;">Assertividade de Parâmetros: {match_rate}% de Match Global</div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"<p style='font-size:1.15rem; line-height:1.7; text-align:justify; color:#e4e6eb;'>{archetypes_data[primary]['desc']}</p>", unsafe_allow_html=True)
    
    st.markdown(f"""
        <div class="ticker-alert">
            <b>⚠️ ATENÇÃO SINALIZADA PELA IA DE RISCO COGNITIVO:</b><br>
            Identificamos uma anomalia severa em sua assinatura secundária. Há um <b>Arquétipo Oculto extremamente raro</b> influenciando diretamente suas falhas de alocação financeira e gerando vazamento de energia e sabotagem em seus relacionamentos afetivos de alto nível.
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
        <div class="glass-card" style="border-left: 3px solid #ff4d4d; background: rgba(255,255,255,0.02);">
            <p style="color:#ff4d4d; font-weight:bold; font-size:1.1rem; margin-bottom:10px;">⚠️ Dados Criptografados Retidos pelo Sistema:</p>
            <ul style="color:#8b949e; line-height:1.8; font-size:0.95rem; margin-left:-15px;">
                <li><b>O seu Arquétipo Sombra:</b> o vetor exato causador dos seus momentos de auto-sabotagem patrimonial.</li>
                <li><b>O Mapa de Inteligência de Alocação Financeira:</b> o seu multiplicador ótimo de patrimônio líquido.</li>
                <li><b>O Radar Comportamental de 6 Eixos:</b> plotagem matemática do seu perfil executivo comparado ao mercado.</li>
                <li><b>O Plano Tático de Evolução de 3 Passos:</b> as ações inegociáveis para destravar sua zona de maestria.</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)
    
    st.write("<br>", unsafe_allow_html=True)
    if st.button("ACESSAR OFERTA DE DESBLOQUEIO DE DOSSIÊ"):
        advance_to('premium_offer')

# STAGE 6: OFERTA PREMIUM IRRECUSÁVEL (VALOR PERCEBIDO EXTREMO)
elif st.session_state.funnel_stage == 'premium_offer':
    st.markdown("<h1>Dossiê Arquétipo Supremo</h1>", unsafe_allow_html=True)
    st.markdown("<div class='luxury-subtitle'>Acesse o mais robusto e profundo relatório de inteligência comportamental e psicanálise prática disponível no mercado digital contemporâneo.</div>", unsafe_allow_html=True)
    
    st.markdown("""
        <div class="glass-card">
            <div class="glass-card-title">Escopo Integral do Dossiê Premium (Liberação Imediata)</div>
            <div style="font-size:1.05rem; line-height:2.2; color:#e4e6eb;">
                ⚜️ <b>Análise de Profundidade da Matriz Dominante</b> (Tratamento Clínico Corporativo)<br>
                🧬 <b>Identificação do Arquétipo Secundário Oculto</b> (O co-protagonista mental)<br>
                🌑 <b>Mapeamento Analítico da Sombra</b> (Neutralização de auto-sabotagem crônica)<br>
                📊 <b>Plotagem do Radar Comportamental Executivo</b> (Gráfico interativo Plotly)<br>
                💰 <b>Vetor de Alocação e Inteligência Financeira</b> (Estratégias de proteção de ativos)<br>
                ❤️ <b>Mapeamento Interpessoal Amoroso</b> (Sinergia premium de relacionamentos)<br>
                💼 <b>Zonas Profissionais de Máxima Rentabilidade</b> (Aceleração de carreira C-Level)<br>
                📈 <b>Plano de Evolução Tático de 3 Passos</b> (Diretrizes práticas inegociáveis)<br>
                📄 <b>Dossiê Completo Exportável em PDF (5 Páginas)</b> contendo Capa e Missão de Vida Premium.
            </div>
            <hr style="border-color: rgba(212,175,55,0.15); margin: 1.5rem 0;">
            <div style="text-align:center;">
                <p style="text-decoration: line-through; color:#8b949e; font-size:1.1rem; margin-bottom:4px;">Valor de Avaliação Corporativa Padrão: R$ 97,00</p>
                <p style="color:#8b949e; font-size:0.9rem; margin-bottom:8px;">Oportunidade Promocional AuraDex Supremo:</p>
                <div style="font-size: 3rem; color:#2ecc71; font-weight:bold; font-family:'Times New Roman', serif;">R$ 1,99</div>
                <p style="color:#8b949e; font-size:0.8rem; margin-top:6px;">(Taxa única de processamento de dados. Sem assinaturas subsequentes. Liberação via PIX/Cartão)</p>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    user_email = st.session_state.user_metadata.get('email', '')
    name = st.session_state.user_metadata.get('nome', 'Usuário')
    
    st.info("📧 Digite seu email para receber o acesso após o pagamento (opcional):")
    email_input = st.text_input("Email", key="payment_email")
    if email_input:
        st.session_state.user_metadata['email'] = email_input
        user_email = email_input
    
    st.write("<br>", unsafe_allow_html=True)
    if st.session_state.get('checkout_url'):
        render_checkout_redirect(st.session_state['checkout_url'])
    else:
        render_payment_button(user_email, name)

# STAGE 7: RELATÓRIO PREMIUM COMPLETO (DASHBOARD EXECUTIVO INTERATIVO)
elif st.session_state.funnel_stage == 'premium_report':
    name = st.session_state.user_metadata['nome']
    user_email = st.session_state.user_metadata.get('email', name.lower().replace(' ', '.') + '@email.com')
    primary = st.session_state.computed_results['primary']
    secondary = st.session_state.computed_results['secondary']
    res_data = archetypes_data[primary]
    sec_data = archetypes_data[secondary]
    global_index = st.session_state.computed_results['global_index']
    
    # Verificar pagamento
    is_unlocked = st.session_state.get('payment_approved', False)
    if not is_unlocked and MercadoPagoManager:
        try:
            is_unlocked = check_payment_and_unlock(user_email)
        except:
            is_unlocked = False
    
    if not is_unlocked:
        st.error("🔒 Acesso bloqueado - Pagamento necessário")
        st.write("")
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("← Voltar para pagamento", use_container_width=True):
                advance_to('premium_offer')
        with col2:
            if st.button("✓ Já paguei", use_container_width=True):
                with st.spinner("Verificando pagamento..."):
                    time.sleep(1)
                    st.rerun()
        st.stop()
    
    st.markdown("""
        <div style='text-align:center; margin-top:1rem;'>
            <span style='color: #2ecc71; background: rgba(46,204,113,0.1); border:1px solid #2ecc71; padding: 5px 15px; border-radius:30px; font-size: 0.8rem; letter-spacing: 2px; font-weight:bold;'>ACESSO IRRESTRITO LIBERADO</span>
        </div>
    """, unsafe_allow_html=True)
    st.markdown(f"<h1>Dossiê Executivo de Alta Performance: {name}</h1>", unsafe_allow_html=True)
    st.markdown("<div class='luxury-subtitle'>Plataforma integrada de inteligência arquetípica corporativa. Visualize seus dados métricos abaixo.</div>", unsafe_allow_html=True)
    
    # Grid Bloomberg Superior de Indicadores Avançados
    st.markdown(f"""
        <div class="bloomberg-container" style="border-color: #d4af37;">
            <div class="bloomberg-box">
                <div class="bloomberg-val">{global_index}/100</div>
                <div class="bloomberg-lbl">Índice Geral Potencial</div>
            </div>
            <div class="bloomberg-box">
                <div class="bloomberg-val">{res_data['rarity']}</div>
                <div class="bloomberg-lbl">Raridade Populacional</div>
            </div>
            <div class="bloomberg-box">
                <div class="bloomberg-val">SÉRIE-A</div>
                <div class="bloomberg-lbl">Grau de Estabilidade</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    col_left, col_right = st.columns([1.2, 1])
    
    with col_left:
        # Bloco do Radar Comportamental interativo Plotly
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("<div class='glass-card-title'>📊 Radar Comportamental Executivo</div>", unsafe_allow_html=True)
        fig_radar = draw_executive_radar(primary)
        st.plotly_chart(fig_radar, use_container_width=True, config={'displayModeBar': False})
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Bloco Financeiro
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("<div class='glass-card-title'>💰 Inteligência e Alocação Financeira</div>", unsafe_allow_html=True)
        st.markdown(f"<p style='color:#e4e6eb; line-height:1.6; text-align:justify;'>{res_data['financeiro']}</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Bloco Carreiras
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("<div class='glass-card-title'>💼 Ecossistemas Profissionais Ótimos</div>", unsafe_allow_html=True)
        st.markdown(f"<p style='color:#e4e6eb; line-height:1.6;'><b>Zonas de Alta Performance Rentável:</b> {res_data['carreira']}</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_right:
        # Bloco da Sombra Crítica (Vermelho Tático)
        st.markdown("<div class='glass-card' style='border-left: 3px solid #ff4d4d; background: rgba(255,77,77,0.02);'>", unsafe_allow_html=True)
        st.markdown("<div class='glass-card-title' style='color:#ff4d4d;'>🌑 Arquétipo Sombra e Pontos Cegos</div>", unsafe_allow_html=True)
        st.markdown(f"<p style='color:#f9f9f9; line-height:1.6; text-align:justify;'>{res_data['sombra']}</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Bloco do Arquétipo Secundário Oculto
        st.markdown("<div class='glass-card' style='border-left: 3px solid #3498db; background: rgba(52,152,219,0.02);'>", unsafe_allow_html=True)
        st.markdown("<div class='glass-card-title' style='color:#3498db;'>🧬 Co-Protagonista Mental</div>", unsafe_allow_html=True)
        st.markdown(f"<p style='color:#f0f3f6; line-height:1.5; margin-bottom:5px;'><b>{secondary}</b></p>", unsafe_allow_html=True)
        st.markdown(f"<p style='color:#8b949e; font-size:0.9rem; text-align:justify;'>{res_data['sec_desc']}</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Bloco Talento Oculto
        st.markdown("<div class='glass-card' style='border-left: 3px solid #9b59b6; background: rgba(155,89,182,0.02);'>", unsafe_allow_html=True)
        st.markdown("<div class='glass-card-title' style='color:#9b59b6;'>✨ Potencial Oculto Adormecido</div>", unsafe_allow_html=True)
        st.markdown(f"<p style='color:#e4e6eb; line-height:1.6; text-align:justify;'>{res_data['talento_oculto']}</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Bloco Amoroso
        st.markdown("<div class='glass-card' style='border-left: 3px solid #e84393; background: rgba(232,67,147,0.02);'>", unsafe_allow_html=True)
        st.markdown("<div class='glass-card-title' style='color:#e84393;'>❤️ Afinidade Relacional de Elite</div>", unsafe_allow_html=True)
        st.markdown(f"<p style='color:#e4e6eb; line-height:1.6; text-align:justify;'>{res_data['amoroso']}</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # Bloco de Evolução Tática em Largura Total
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("<div class='glass-card-title'>📈 Plano de Evolução Tático Operacional</div>", unsafe_allow_html=True)
    for idx, step in enumerate(res_data['plano_evolucao']):
        st.markdown(f"<p style='color:#e4e6eb; line-height:1.6;'><b>Passo {idx+1}:</b> {step}</p>", unsafe_allow_html=True)
    st.markdown(f"<hr style='border-color:rgba(212,175,55,0.15);'><p style='text-align:center; font-family:Times New Roman, serif; font-style:italic; font-size:1.25rem; color:#d4af37; margin-top:15px;'>\"{res_data['frase']}\"</p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.write("<br><hr style='border-color: rgba(255,255,255,0.05);'><br>", unsafe_allow_html=True)
    
    # Ações de Saída: Download de PDF de 5 páginas e Compartilhamento de Alta Conversão no WhatsApp
    col_pdf, col_wpp = st.columns(2)
    
    with col_pdf:
        # Gera o PDF via ReportLab de forma imediata em memória
        pdf_data = build_pdf_dossier()
        st.download_button(
            label="⬇️ EXPORTAR Dossiê PREMIUM EM PDF (5 PÁG)",
            data=pdf_data,
            file_name=f"Dossie_Premium_{name}_{primary.replace(' ', '_')}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
        
    with col_wpp:
        whatsapp_copy = f"Acabei de descobrir meu Arquétipo Supremo no AuraDex. Meu perfil é da classe ultra rara '{primary}' (apenas {res_data['rarity']} da população global possui). Faça seu teste de inteligência comportamental agora mesmo."
        encoded_copy = urllib.parse.quote(whatsapp_copy)
        st.markdown(f"""
            <a href="https://wa.me/?text={encoded_copy}" target="_blank" style="text-decoration:none;">
                <button style="width: 100%; background: #25D366; color: white !important; font-weight: bold; font-size:1.05rem; letter-spacing:1px; border-radius: 6px; border: none; padding: 14px 20px; text-transform: uppercase; cursor: pointer; box-shadow: 0 4px 15px rgba(37, 211, 102, 0.2);">
                    📱 COMPARTILHAR NO WHATSAPP
                </button>
            </a>
        """, unsafe_allow_html=True)