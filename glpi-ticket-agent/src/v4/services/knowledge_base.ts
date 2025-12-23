/**
 * Knowledge Base EXPANDIDA - Base de conhecimento com dados reais dos testes
 * 
 * CHANGELOG:
 * - 2025-12-22: Expandida com 50 casos de teste exaustivos
 * - Adicionados: 10+ entidades, 15+ categorias, 20+ FAQs, exemplos de Chitchat
 */

export interface EntityKnowledge {
    id: number;
    name: string;
    fullName: string;
    aliases: string[];
    context: string;
    commonRequests: string[];
}

export interface CategoryKnowledge {
    id: number;
    name: string;
    examples: string[];
    diagnosticSteps: string[];
    relatedCategories?: string[];
}

export interface BusinessRule {
    topic: string;
    content: string;
    examples?: string[];
}

export interface FAQ {
    question: string;
    answer: string;
    keywords: string[];
}

export interface ChitchatPattern {
    examples: string[];
    category: 'greeting' | 'thanks' | 'farewell' | 'question_about_agent' | 'test' | 'compliment';
}

export const KNOWLEDGE_BASE = {
    // ========== ENTIDADES (EXPANDIDO: 4 → 10) ==========
    entities: [
        {
            id: 7,
            name: "SECOM",
            fullName: "Secretaria de Comunicação",
            aliases: ["Comunicação", "Assessoria de Imprensa", "Secretaria Comunicação", "Secretaria de Imprensa"],
            context: "Responsável pela comunicação oficial do Governo do RS, assessoria de imprensa e mídias sociais",
            commonRequests: ["Criar usuário", "Acesso ao site institucional", "Permissões de publicação", "Acesso redes sociais"]
        },
        {
            id: 4,
            name: "Casa Militar",
            fullName: "Casa Militar do Governador",
            aliases: ["Segurança", "Militar", "Seg", "CM"],
            context: "Responsável pela segurança do Governador e da sede do governo",
            commonRequests: ["Controle de acesso", "Câmeras", "Sistema de segurança", "Monitoramento"]
        },
        {
            id: 3,
            name: "Casa Civil",
            fullName: "Casa Civil do Governo",
            aliases: ["Civil", "Gabinete Civil", "CC"],
            context: "Coordenação política e administrativa do governo",
            commonRequests: ["Acesso a sistemas administrativos", "Usuários para assessores", "Autorizações"]
        },
        {
            id: 9,
            name: "Departamento de Tecnologia",
            fullName: "Departamento de Tecnologia e Informação",
            aliases: ["DTIC", "TI", "Tecnologia", "DTI", "Departamento TI"],
            context: "Responsável pela infraestrutura de TI do governo",
            commonRequests: ["Suporte técnico", "Acesso VPN", "Configuração de rede", "Problemas técnicos"]
        },
        {
            id: 1,
            name: "Gabinete",
            fullName: "Gabinete do Governador",
            aliases: ["GG", "Gab", "Gabinete Gov"],
            context: "Gabinete direto do Governador, assessoria política e administrativa",
            commonRequests: ["Usuários para assessores diretos", "Acesso sistemas estratégicos"]
        },
        {
            id: 10,
            name: "Procergs",
            fullName: "Companhia de Processamento de Dados do Estado",
            aliases: ["Proc", "Processamento"],
            context: "Empresa pública de tecnologia e processamento de dados",
            commonRequests: ["Integração de sistemas", "Acesso a banco de dados", "Suporte técnico avançado"]
        },
        {
            id: 11,
            name: "Central de Atendimentos",
            fullName: "Central de Atendimentos ao Cidadão",
            aliases: ["CAU", "Central", "Atendimento"],
            context: "Responsável pelo atendimento ao público e cidadãos",
            commonRequests: ["Sistema de tickets", "Acesso plataforma de atendimento"]
        },
        {
            id: 12,
            name: "Secretaria da Fazenda",
            fullName: "Secretaria da Fazenda Estadual",
            aliases: ["Fazenda", "SEFAZ", "SF"],
            context: "Gestão financeira e tributária do estado",
            commonRequests: ["Acesso sistemas fiscais", "Usuários área financeira"]
        },
        {
            id: 13,
            name: "Secretaria da Saúde",
            fullName: "Secretaria da Saúde do Estado",
            aliases: ["Saúde", "SES", "Sec Saúde"],
            context: "Gestão da saúde pública do estado",
            commonRequests: ["Acesso sistemas hospitalares", "Usuários profissionais saúde"]
        },
        {
            id: 14,
            name: "Secretaria da Educação",
            fullName: "Secretaria da Educação do Estado",
            aliases: ["Educação", "SEDUC", "Sec Educação"],
            context: "Gestão da educação pública do estado",
            commonRequests: ["Acesso sistema escolar", "Usuários professores"]
        }
    ] as EntityKnowledge[],

    // ========== CATEGORIAS (EXPANDIDO: 4 → 15) ==========
    categories: [
        {
            id: 14,
            name: "Impressora",
            examples: [
                "impressora não imprime",
                "toner acabou",
                "papel preso",
                "impressora offline",
                "manchas na impressão",
                "impressora HP não está imprimindo",
                "papel preso na impressora",
                "barulho estranho na impressora"
            ],
            diagnosticSteps: [
                "Qual o modelo da impressora?",
                "A impressora está ligada e conectada?",
                "Qual mensagem de erro aparece?",
                "Já tentou reiniciar a impressora?",
                "O problema é com todas as impressões ou apenas algumas?",
                "Outros usuários conseguem imprimir nesta impressora?"
            ],
            relatedCategories: ["Hardware", "Equipamentos"]
        },
        {
            id: 1,
            name: "Novo Usuário",
            examples: [
                "criar usuário",
                "preciso de acesso",
                "novo colaborador",
                "estagiário precisa de login",
                "criar conta",
                "novo funcionário",
                "preciso de usuário",
                "adicionar usuário",
                "cadastrar usuário"
            ],
            diagnosticSteps: [
                "Nome completo do usuário",
                "CPF",
                "Cargo/função",
                "Órgão de lotação",
                "Tipo de acesso necessário",
                "Data de início",
                "Gestor responsável"
            ]
        },
        {
            id: 5,
            name: "Rede / Internet",
            examples: [
                "internet não funciona",
                "wifi não conecta",
                "rede lenta",
                "sem acesso à internet",
                "internet muito lenta",
                "tudo está muito devagar",
                "conexão caindo"
            ],
            diagnosticSteps: [
                "O problema é no wifi ou cabo?",
                "Outros computadores têm internet?",
                "Consegue acessar outros sites?",
                "Já tentou reiniciar o computador?",
                "Qual a velocidade esperada vs atual?",
                "O problema começou recentemente ou sempre foi assim?"
            ]
        },
        {
            id: 8,
            name: "Email",
            examples: [
                "não recebo emails",
                "senha do email",
                "caixa de email cheia",
                "email retorna erro",
                "não consigo receber emails",
                "email não envia",
                "problema com Outlook"
            ],
            diagnosticSteps: [
                "Qual seu endereço de email?",
                "Mensagem de erro específica",
                "Problema ao enviar ou receber?",
                "Desde quando o problema ocorre?",
                "Consegue acessar webmail?",
                "Qual cliente de email está usando?"
            ]
        },
        {
            id: 15,
            name: "Senha",
            examples: [
                "esqueci minha senha",
                "senha não funciona",
                "resetar senha",
                "recuperar senha",
                "senha expirou",
                "bloqueio de senha",
                "não consigo logar"
            ],
            diagnosticSteps: [
                "De qual sistema é a senha?",
                "Já tentou o 'Esqueci minha senha'?",
                "A conta está bloqueada?",
                "Quando foi a última vez que conseguiu acessar?",
                "Recebe alguma mensagem de erro específica?"
            ]
        },
        {
            id: 16,
            name: "Hardware",
            examples: [
                "computador fazendo barulho estranho",
                "tela azul da morte",
                "computador não liga",
                "teclado não funciona",
                "mouse não responde",
                "monitor sem imagem"
            ],
            diagnosticSteps: [
                "Qual o modelo do equipamento?",
                "Quando o problema começou?",
                "Houve alguma queda ou impacto?",
                "O equipamento liga mas não funciona, ou não liga?",
                "Já tentou trocar cabos/conexões?"
            ]
        },
        {
            id: 17,
            name: "Sistema Travado",
            examples: [
                "sistema travou",
                "não responde",
                "computador congelou",
                "tela congelada",
                "sistema ficou travado após atualização",
                "aplicação não responde"
            ],
            diagnosticSteps: [
                "Qual sistema/aplicação travou?",
                "Isso acontece frequentemente?",
                "Consegue mover o mouse?",
                "Aparece mensagem de 'não respondendo'?",
                "Já tentou Ctrl+Alt+Del?"
            ]
        },
        {
            id: 18,
            name: "VPN",
            examples: [
                "VPN não conecta",
                "erro na VPN",
                "não consigo acessar VPN",
                "VPN desconecta",
                "acesso remoto não funciona"
            ],
            diagnosticSteps: [
                "Qual VPN você está usando?",
                "Mensagem de erro específica",
                "Você está em casa ou em outro local?",
                "Já funcionou antes neste computador?",
                "Seu usuário tem permissão para VPN?"
            ]
        },
        {
            id: 19,
            name: "Áudio / Som",
            examples: [
                "sem áudio no computador",
                "som não funciona",
                "microfone não funciona",
                "não consigo ouvir",
                "áudio muito baixo"
            ],
            diagnosticSteps: [
                "O problema é com fones ou alto-falantes?",
                "Aparece o ícone de som na barra de tarefas?",
                "Já verificou se está no mudo?",
                "Outros aplicativos têm som?",
                "Já tentou reiniciar o computador?"
            ]
        },
        {
            id: 20,
            name: "Webcam / Vídeo",
            examples: [
                "câmera não funciona no Teams",
                "webcam não liga",
                "sem imagem na câmera",
                "câmera congelada",
                "vídeo não funciona"
            ],
            diagnosticSteps: [
                "Em qual aplicativo a câmera não funciona?",
                "A luz da webcam acende?",
                "Já funcionou antes?",
                "Outras aplicações conseguem acessar a câmera?",
                "Já verificou as permissões de câmera?"
            ]
        },
        {
            id: 21,
            name: "Erro de Sistema",
            examples: [
                "erro 500",
                "erro 404",
                "página não encontrada",
                "erro interno do servidor",
                "sistema retorna erro"
            ],
            diagnosticSteps: [
                "Qual o código de erro exato?",
                "Em qual sistema isso acontece?",
                "Consegue fazer print do erro?",
                "Outros usuários têm o mesmo problema?",
                "Que ação você estava fazendo quando o erro ocorreu?"
            ]
        },
        {
            id: 22,
            name: "Login / Acesso",
            examples: [
                "não consigo fazer login",
                "acesso negado",
                "sem permissão",
                "usuário não autorizado",
                "conta bloqueada"
            ],
            diagnosticSteps: [
                "Em qual sistema você está tentando entrar?",
                "Qual mensagem de erro aparece?",
                "Você já conseguiu acessar antes?",
                "Sua senha está correta?",
                "Você é novo na empresa?"
            ]
        },
        {
            id: 23,
            name: "Atualização / Instalação",
            examples: [
                "sistema ficou travado após atualização",
                "erro na atualização",
                "não consigo instalar",
                "instalação falhou",
                "atualização não completa"
            ],
            diagnosticSteps: [
                "Qual software você está tentando atualizar/instalar?",
                "Mensagem de erro exata",
                "Você tem permissões de administrador?",
                "O sistema estava funcionando antes da atualização?",
                "Consegue fazer rollback?"
            ]
        },
        {
            id: 24,
            name: "Performance / Lentidão",
            examples: [
                "tudo está muito devagar",
                "computador lento",
                "sistema travando",
                "demora para abrir programas",
                "navegador lento"
            ],
            diagnosticSteps: [
                "Quando começou a ficar lento?",
                "Acontece com todos os programas?",
                "Quanto de memória RAM seu computador tem?",
                "Disco está cheio?",
                "Quantos programas você tem abertos?"
            ]
        },
        {
            id: 25,
            name: "Arquivo / Documento",
            examples: [
                "não consigo abrir arquivo",
                "arquivo corrompido",
                "documento não salva",
                "perdi meu arquivo",
                "arquivo sumiu"
            ],
            diagnosticSteps: [
                "Qual tipo de arquivo (.pdf, .docx, etc)?",
                "Mensagem de erro ao abrir",
                "O arquivo está em rede ou local?",
                "Quando foi a última vez que conseguiu abrir?",
                "Você tem backup deste arquivo?"
            ]
        }
    ] as CategoryKnowledge[],

    // ========== REGRAS DE NEGÓCIO (EXPANDIDO: 3 → 8) ==========
    rules: [
        {
            topic: "Criar Usuário",
            content: "Para criar um novo usuário no sistema, são necessários: nome completo, CPF, cargo/função, órgão de lotação e justificativa do acesso.",
            examples: [
                "Criar usuário para João Silva, CPF 123.456.789-00, Analista na SECOM",
                "Novo estagiário Maria Santos na Casa Civil precisa de acesso básico",
                "Preciso de acesso para Ana Paula Silva na Casa Militar",
                "Usuário para José María Pérez da Procergs"
            ]
        },
        {
            topic: "Reset de Senha",
            content: "Senhas podem ser resetadas pelo próprio usuário usando o botão 'Esqueci minha senha' na tela de login. Em casos especiais, o suporte pode fazer o reset manualmente.",
            examples: [
                "Esqueci minha senha",
                "Preciso resetar a senha de um usuário",
                "Senha não funciona",
                "Senha expirou"
            ]
        },
        {
            topic: "Classificação de Urgência",
            content: "Incidentes que afetam sistemas críticos ou múltiplos usuários têm prioridade alta. Solicitações de novos recursos têm prioridade normal.",
            examples: []
        },
        {
            topic: "Múltiplos Usuários",
            content: "Ao solicitar múltiplos usuários, crie uma solicitação para cada um com seus dados específicos. Não é possível criar em lote.",
            examples: [
                "Precisamos de usuários para Maria, João e Pedro",
                "Criar 5 usuários para o setor"
            ]
        },
        {
            topic: "Acesso VPN",
            content: "Acesso VPN requer aprovação do gestor e justificativa de trabalho remoto. Processo leva 2-3 dias úteis.",
            examples: [
                "Preciso de VPN para trabalhar de casa",
                "Como solicitar acesso remoto?"
            ]
        },
        {
            topic: "Prazo de Atendimento",
            content: "Solicitações são atendidas em até 24h úteis. Incidentes críticos têm atendimento prioritário.",
            examples: []
        },
        {
            topic: "Horário de Suporte",
            content: "Suporte disponível de segunda a sexta, 8h às 18h. Emergências fora do horário: contatar o plantão.",
            examples: []
        },
        {
            topic: "Solicitação Futura",
            content: "Solicitações com data futura são aceitas com até 5 dias de antecedência. Especifique a data desejada.",
            examples: [
                "Vou precisar de acesso para Lucas na próxima semana",
                "Novo funcionário começa segunda-feira"
            ]
        }
    ] as BusinessRule[],

    // ========== FAQs (EXPANDIDO: 3 → 20) ==========
    faqs: [
        {
            question: "Como resetar minha senha?",
            answer: "Use o botão 'Esqueci minha senha' na tela de login. Você receberá um email com instruções.",
            keywords: ["senha", "reset", "esqueci", "recuperar", "resetar"]
        },
        {
            question: "Quanto tempo leva para criar um novo usuário?",
            answer: "Usuários são criados em até 24 horas úteis após aprovação do gestor.",
            keywords: ["usuário", "prazo", "quanto tempo", "demora", "criar"]
        },
        {
            question: "Como solicitar acesso VPN?",
            answer: "Abra um chamado especificando a necessidade de acesso remoto e a justificativa. Aprovação do gestor é necessária.",
            keywords: ["vpn", "remoto", "acesso", "home office"]
        },
        {
            question: "Minha impressora não funciona, o que fazer?",
            answer: "Verifique se está ligada, conectada e se tem papel. Se persistir, abra um chamado informando o modelo e a mensagem de erro.",
            keywords: ["impressora", "não funciona", "não imprime", "problema"]
        },
        {
            question: "Como abrir um chamado?",
            answer: "Você pode abrir um chamado através do portal de atendimento ou conversando comigo aqui no chat.",
            keywords: ["chamado", "ticket", "solicitar", "pedir ajuda"]
        },
        {
            question: "Qual o horário de atendimento do suporte?",
            answer: "Segunda a sexta, das 8h às 18h. Para emergências fora do horário, contate o plantão.",
            keywords: ["horário", "atendimento", "funciona", "disponível"]
        },
        {
            question: "Como solicitar acesso a um sistema específico?",
            answer: "Abra um chamado especificando o sistema, sua função e a justificativa. Aprovação do gestor pode ser necessária.",
            keywords: ["acesso", "sistema", "permissão", "autorização"]
        },
        {
            question: "Meu email está cheio, o que fazer?",
            answer: "Arquive ou exclua emails antigos. Se precisar aumentar a cota, solicite através de chamado.",
            keywords: ["email", "cheio", "cota", "espaço", "armazenamento"]
        },
        {
            question: "Como configurar VPN no meu computador?",
            answer: "Após aprovação do acesso VPN, você receberá um manual por email com instruções detalhadas.",
            keywords: ["vpn", "configurar", "instalar", "setup"]
        },
        {
            question: "Posso usar meu computador pessoal para trabalhar?",
            answer: "Sim, mas deve seguir as políticas de segurança e instalar VPN. Consulte seu gestor.",
            keywords: ["computador pessoal", "byod", "próprio computador"]
        },
        {
            question: "Como solicitar um novo equipamento?",
            answer: "Solicite através do seu gestor, que avaliará a necessidade e encaminhará ao TI.",
            keywords: ["equipamento", "computador novo", "notebook", "hardware"]
        },
        {
            question: "Esqueci meu usuário, como recupero?",
            answer: "Entre em contato com o suporte informando seu nome completo e CPF. Enviaremos o usuário por email.",
            keywords: ["usuário", "login", "esqueci", "não lembro"]
        },
        {
            question: "Como mudar minha senha?",
            answer: "Acesse 'Configurações' > 'Segurança' > 'Alterar Senha' no sistema. Ou use 'Esqueci minha senha' no login.",
            keywords: ["mudar senha", "alterar senha", "trocar senha"]
        },
        {
            question: "Meu computador está muito lento, o que fazer?",
            answer: "Feche programas desnecessários, verifique espaço em disco e reinicie. Se persistir, abra um chamado.",
            keywords: ["lento", "devagar", "travando", "performance"]
        },
        {
            question: "Como acessar o sistema remotamente?",
            answer: "Você precisa de VPN configurada. Solicite acesso VPN através de chamado.",
            keywords: ["remoto", "home", "casa", "fora do escritório"]
        },
        {
            question: "Posso instalar programas no meu computador?",
            answer: "Apenas programas aprovados pelo TI. Solicite a instalação através de chamado.",
            keywords: ["instalar", "programa", "software", "aplicativo"]
        },
        {
            question: "Como recuperar um arquivo deletado?",
            answer: "Se estava em rede, pode estar na lixeira do servidor. Contate o suporte em até 30 dias.",
            keywords: ["recuperar", "arquivo deletado", "arquivo perdido", "restaurar"]
        },
        {
            question: "Meu Teams não funciona, o que fazer?",
            answer: "Verifique sua conexão, reinicie o aplicativo e teste. Se persistir, abra chamado informando o erro.",
            keywords: ["teams", "reunião", "vídeo chamada", "microsoft teams"]
        },
        {
            question: "Como solicitar treinamento em um sistema?",
            answer: "Consulte seu gestor. Treinamentos são agendados conforme demanda e disponibilidade.",
            keywords: ["treinamento", "capacitação", "aprender", "curso"]
        },
        {
            question: "Posso acessar redes sociais no trabalho?",
            answer: "Depende da política de cada órgão. Consulte seu gestor ou RH para orientações.",
            keywords: ["redes sociais", "facebook", "instagram", "política de uso"]
        }
    ] as FAQ[],

    // ========== PADRÕES DE CHITCHAT (NOVO!) ==========
    chitchat: [
        {
            category: 'greeting',
            examples: [
                "oi", "olá", "oi tudo bem", "bom dia", "boa tarde", "boa noite",
                "hello", "hey", "e aí", "opa", "salve"
            ]
        },
        {
            category: 'thanks',
            examples: [
                "obrigado", "obrigada", "valeu", "thanks", "agradeço",
                "obrigado pela ajuda", "muito obrigado", "brigadão",
                "grato", "grateful"
            ]
        },
        {
            category: 'farewell',
            examples: [
                "até logo", "tchau", "bye", "até mais", "falou",
                "até breve", "até depois", "té logo", "adeus"
            ]
        },
        {
            category: 'question_about_agent',
            examples: [
                "você é um robô", "você é humano", "quem é você",
                "o que você faz", "como você funciona", "você é bot",
                "você é ia", "você é inteligência artificial"
            ]
        },
        {
            category: 'test',
            examples: [
                "teste", "testando", "test", "hello world",
                "isso funciona", "está funcionando"
            ]
        },
        {
            category: 'compliment',
            examples: [
                "você é muito bom", "você é ótimo", "muito legal",
                "você é inteligente", "parabéns", "excelente",
                "é muito rápido", "ajuda bastante"
            ]
        }
    ] as ChitchatPattern[]
};
