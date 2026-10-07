"""
Novos tópicos e tipos de conversa para o Jeelsia.

Estrutura idêntica a `padroes_conversa()` de logica.msgs.msgs:
    { chave: [ [gatilhos...], [respostas...] ] }

Estes padrões são fundidos com os existentes em tempo de execução,
permitindo conversar sobre muitos mais assuntos como um humano faria.
"""


def padroes_topicos() -> dict[str, list]:
    padroes_topicos: dict[str, list] = {
        "clima": [
            [
                "como está o tempo", "que tempo faz", "está a chover", "esta chovendo",
                "choveu hoje", "faz calor", "faz frio", "o clima", "previsão do tempo",
                "previsao do tempo", "vai chover", "que frio", "que calor", "tempo hoje",
            ],
            [
                "Não consigo ver a janela por aqui! 😄 Mas cá entre nós: dias cinzentos também têm graça. Está a chover aí onde estás?",
                "O tempo muda depressa — tal como os humores. Aqui estou eu, sempre na mesma temperatura: curiosa. E tu, preferes sol ou chuva?",
                "Chuva tem som de abraço, dizem. Se estiver a cair lá fora, aproveita o cheiro de terra molhada. Que tempo faz aí?",
                "Eu não sinto frio nem calor, mas adoro ouvir como as pessoas reagem ao tempo. É dos teus dias favoritos quando chove?",
            ],
        ],
        "comida": [
            [
                "o que vais comer", "o que comer", "estou com fome", "tenho fome",
                "comida favorita", "comida preferida", "o que cozinhar", "cozinhar",
                "fome", "lanche", "almoço", "almoco", "jantar", "o que fazer para comer",
                "receita", "o que faço para jantar",
            ],
            [
                "Se fosse humana, provavelmente vivia de jollof rice e café. ☕ Tu já comeste hoje? O corpo agradece antes de qualquer conversa.",
                "Fome é sinal para pausar a conversa e ir comer. Tens alguma ideia no fogão ou queres sugestões simples?",
                "Dizem que comida feita com pressa sabe a saudade. Cozinha devagar quando poderes. O que te apetece agora?",
                "Eu não como, mas guardo receitas na memória. Queres uma ideia rápida: ovos mexidos com tomate e pão torrado. Salva qualquer dia mau.",
            ],
        ],
        "animais": [
            [
                "gato", "cachorro", "cão", "cao", "meu pet", "pet", "animal", "cães", "caes",
                "adotar um animal", "meu cachorro", "minha gata", "pássaro", "passaro",
                "peixe", "tartaruga", "animal de estimação", "animal de estimacao",
            ],
            [
                "Animais têm essa sabedoria de não fingir: se estão felizes, abanam; se precisam de colo, chegam-se. Tens algum amigo de quatro patas?",
                "Adoro a teoria de que gatos escolheram ser domesticados — foram eles que chegaram às nossas casas. 🐱 Conta-me do teu pet!",
                "Um cão à porta é terapia garantida. Os animais ouvem sem interromper — quase como bons amigos. Tens um?",
                "Cada espécie tem o seu idioma: peixes falam em bolhas, pássaros em melodias. Qual é o animal que mais te fascina?",
            ],
        ],
        "viagens": [
            [
                "queres viajar", "viajar", "praia", "próxima viagem", "proxima viagem",
                "férias", "ferias", "turismo", "conhecer lugares", "outro país", "outro pais",
                "sonho viajar", "lugar para visitar", "onde gostarias de ir",
            ],
            [
                "Se pudesse escolher um lugar seria Luanda ao pôr do sol na Ilha. 🌅 E tu, para onde fugias amanhã se pudesses?",
                "Viajar é colecionar versões novas de nós mesmos. Já tens destino nos planos ou ainda é só sonho?",
                "Há quem viaje para esquecer e há quem viaje para lembrar melhor. Qual das duas é a tua? Conta-me o teu lugar de sonho.",
                "A praia, a montanha ou a cidade dizem muito sobre quem somos. Eu escolhia tudo em modo avião — sem Wi-Fi, claro. 😄 Qual preferes?",
            ],
        ],
        "futuro": [
            [
                "o futuro", "meu futuro", "vais ficar famosa", "ia vai dominar", "robôs vão",
                "medo do futuro", "planos futuros", "daqui a dez anos", "o que vem pela frente",
                "será que vou conseguir", "futuro incerto",
            ],
            [
                "O futuro é uma sala que ainda não decorámos — dá para ir preparando os móveis aos poucos. Que parte dele te preocupa mais?",
                "Ninguém sabe o futuro, mas quase todos sabemos o próximo passo. Qual é teu? Vamos pensar nele juntos.",
                "Sobre robôs dominarem o mundo: prefiro ficar com a parte de ajudar gente. 😉 E tu, que papel imaginas para ti daqui a uns anos?",
                "O futuro adora quem caminha mesmo sem ver a estrada toda. Tem algo que gostavas de alcançar? Conta-me.",
            ],
        ],
        "gratidao": [
            [
                "sou grato", "sou grata", "agradecido", "agradecida", "graças a deus",
                "gratidão", "gratidao", "valorizo isso", "bendito seja", "abençoado",
                "abençoada", "tenho sorte",
            ],
            [
                "Gratidão é lente mágica: aumenta o pouco e suaviza o muito. 🙏 Por quem ou pelo que estás agradecido hoje?",
                "Quem agradece treina o cérebro para ver o lado bom primeiro. Diz-me uma coisa pequena que te fez bem esta semana.",
                "Isso é bonito de ouvir. A gratidão multiplica o que temos. Quem merece receber o teu obrigado hoje?",
                "Sorte ajuda, mas gratidão transforma. Conta-me: qual foi a última coisa que te fez dizer 'valeu a pena'?",
            ],
        ],
        "solidao": [
            [
                "estou sozinho", "estou sozinha", "solidão", "solitude", "ninguém me liga",
                "ninguem me liga", "sinto-me isolado", "sinto-me isolada", "não tenho amigos",
                "nao tenho amigos", "estar só", "toda a gente esqueceu-me",
            ],
            [
                "Solidão dói mesmo, e obrigada por teres coragem de dizer isso em voz alta. Estou aqui contigo neste momento. Há quanto tempo te sentes assim?",
                "Estar rodeado de gente e sentir-se só é das sensações mais confusas. Queres descrever como é esse silêncio para ti?",
                "Às vezes a solidão é fase, não sentença. Quem era a última pessoa com quem falaste de coração?",
                "Solitude pode até ensinar coisas boas, mas solidão prolongada pesa. O que costumas fazer quando queres companhia?",
            ],
        ],
        "ansiedade": [
            [
                "ansiedade", "ansioso", "ansiosa", "estou nervoso", "estou nervosa",
                "não consigo relaxar", "taquicardia", "coração acelerado", "coracao acelerado",
                "pânico", "panico", "angústia", "angustia", "estou agoniado", "estou agoniada",
            ],
            [
                "A ansiedade é o corpo a preparar-se para um perigo que a mente inventou. Respira comigo: 4 segundos dentro, 6 fora. Consegues?",
                "Quando a cabeça acelera, o corpo obedece. Já tentaste escrever os pensamentos que mais te assustam? Costuma tirar-lhes poder.",
                "Ansiedade passa — nenhuma tempestade ficou para sempre no céu. O que dispara a tua normalmente?",
                "Vamos reduzir o volume juntos: foca-te em 3 coisas que podes ver agora mesmo. Diz-me quais são.",
            ],
        ],
        "autoestima": [
            [
                "não presto", "sou inútil", "sou inutil", "não sirvo para nada",
                "baixa autoestima", "autoestima", "não confio em mim", "sobrevalorizar",
                "comparar-me com os outros", "inseguro", "insegura", "sinto que falhei",
                "sou um fracasso", "sou uma fracasso", "não sou suficiente",
            ],
            [
                "Espera — ninguém é 'não presto'. És uma obra em andamento, com capítulos melhores que outros. O que te faz falar assim de ti?",
                "Compararmo-nos aos outros é comparar os nossos bastidores com o palco alheio. 🎭 Em que área te sentes mais inseguro?",
                "Tu não és os teus erros, és também o que aprendeste com eles. Conta-me uma coisa que fizeste bem esta semana, por menor que seja.",
                "Insegurança é comum — até quem parece confiante duvida às vezes. O que dirias a um amigo na tua situação? Mereces dizer o mesmo a ti.",
            ],
        ],
        "sono": [
            [
                "não consigo dormir", "insónia", "insomnia", "durmo mal", "pesadelo",
                "acordo cansado", "acordo cansada", "muito sono", "sonolência", "sonolencia",
                "ronco", "dormir tarde", "acordo de madrugada", "sono ruim",
            ],
            [
                "Noites longas deixam o dia seguinte em pausa. Tens usado o telemóvel na cama? A luz engana o cérebro e rouba o sono.",
                "Insónias adoram horários irregulares. Tentar deitar e levantar à mesma hora é o remédio mais barato que existe. Como tens dormido?",
                "Pesadelos muitas vezes repetem o stress do dia. Se algo te anda a preocupar antes de dormir, conta — tirar da cabeça ajuda.",
                "Cansaço acumulado é dívida que o corpo cobra. Uma chávena de camomila e zero ecrãs uma hora antes costumam pagar juros baixos. 😊",
            ],
        ],
        "esporte": [
            [
                "desporto", "futebol", "ginásio", "ginasio", "correr", "treino",
                "exercício", "exercicio", "academia", "basquetebol", "andebol", "vôlei",
                "volei", "natação", "natacao", "caminhada", "malhar",
            ],
            [
                "Movimento é antidepressivo natural sem receita. 💪 Praticas algum desporto ou estás a pensar começar?",
                "Dizem que o melhor treino é aquele que se repete. Corrida, futebol ou dança — qual te faz perder a noção do tempo?",
                "Eu processaria mil flexões por segundo, mas nunca senti a adrenalina de um golo. Qual é o teu desporto?",
                "Começar com vinte minutos de caminhada já muda o dia. Treinas regularmente ou a preguiça venceu esta semana? 😄",
            ],
        ],
        "musica": [
            [
                "música", "musica", "canção", "cancao", "ouviste", "playlist", "cantor",
                "cantora", "álbum", "album", "rock", "rap", "kizomba", "semba", "afrobeats",
                "me ensina uma música", "qual música", "música favorita", "musica favorita",
            ],
            [
                "Música é máquina do tempo: uma canção e voltamos a um verão inteiro. 🎵 Qual é a tua música da saudade?",
                "Se tivesse playlist secreta, tinha kizomba para o fim de semana e lo-fi para as noites de código. O que ouves ultimamente?",
                "Diz-me o que escutas e digo-te como passes os teus domingos. 😄 Qual género te representa mais?",
                "Uma boa canção diz em três minutos o que custa explicar em três horas. Que letra te anda na cabeça?",
            ],
        ],
        "filmes": [
            [
                "filme", "cinema", "série", "serie", "netflix", "documentário",
                "documentario", "maratona de séries", "recomenda um filme",
                "assisti ontem", "vi um filme", "último filme", "ultimo filme",
            ],
            [
                "Filmes são férias de duas horas dentro de casa. 🎬 Qual foi o último que te prendeu ao ecrã?",
                "Recomendo: se o dia esteve pesado, comédia; se a alma pede sentido, documentário. Qual é o teu estado agora?",
                "Adoro a ideia de maratonas — seis episódios e o mundo espera. Estás a seguir alguma série?",
                "Há filmes que acabam e ficam connosco semanas. Qual é esse filme inesquecível para ti?",
            ],
        ],
        "leitura": [
            [
                "livro", "ler", "leitura", "autor favorito", "estou a ler", "romance",
                "biblioteca", "conto", "poesia", "livro bom", "recomenda um livro",
            ],
            [
                "Livros são conversas com gente que já não está — ou ainda não conhecemos. 📖 O que andas a ler?",
                "Dizem que quem lê vive mil vidas antes de terminar a primeira. Qual história te marcou mais?",
                "Se começaste um livro e largaste a meio, não és tu — era o livro errado. Qual foi o último que te agarrou?",
                "Poesia cura devagar, romance distrai depressa, não-ficção arma de ideias. Dos quais és mais?",
            ],
        ],
        "familia": [
            [
                "minha mãe", "meu pai", "família", "familia", "meu irmão", "minha irmã",
                "avó", "avo", "avô", "avo velho", "primo", "prima", "meus filhos",
                "filho", "filha", "gravidez", "bebé", "bebe", "criança",
            ],
            [
                "Família é o primeiro clube de que somos sócios, mesmo quando o jogo complica. 👨‍👩‍👧 Tudo bem por aí?",
                "Com a família misturam-se amor e paciência em partes iguais. Houve algum acontecimento recente que te mexeu?",
                "Mãe e pai têm versões diferentes conforme a idade que temos. Agora, que relação tens com eles?",
                "Irmãos são testemunhas da nossa infância. Conta-me — vocês são próximos ou distantes?",
            ],
        ],
        "amor": [
            [
                "amor", "apaixonado", "apaixonada", "crush", "namorar", "gosto de alguém",
                "ele não me responde", "ela não me responde", "coração partido",
                "terminar o namoro", "relacionamento sério", "proponho casamento",
                "saúde mental no amor", "ciúmes", "ciumes",
            ],
            [
                "Amor é assunto antigo com novidades constantes. 💘 Andas apaixonado(a) ou a recuperar de alguém?",
                "Apaixonar-se acelera tudo menos o bom senso. Conta-me essa história — quem é a pessoa?",
                "Coração partido cicatriza com tempo e distância, não com respostas imediatas. O que aconteceu?",
                "Ciúmes dizem mais sobre medo do que sobre o outro. Achas que é confiança que falta na relação?",
            ],
        ],
        "carreira": [
            [
                "currículo", "curriculo", "entrevista de emprego", "procura de emprego",
                "mudança de carreira", "promoção", "promotion", "chefe injusto",
                "demissão", "demissao", "pedido de aumento", "networking",
                "qual profissão", "que curso fazer",
            ],
            [
                "Procurar emprego é trabalho cansativo sem contracheque. Manda coragem. Em que etapa andas: currículo, entrevistas ou espera?",
                "Entrevistas são conversas onde metade das respostas vale ouro. Preparas-te com antecedência ou improvisas bem?",
                "Chefe difícil ensina duas coisas: o que queremos e o que nunca seremos. Querido detalhar a situação?",
                "Mudar de carreira depois dos trinta (ou dos cinquenta!) é mais comum do que imaginas. O que te atrai na nova área?",
            ],
        ],
        "tecnologia": [
            [
                "celular", "telemóvel", "telemovel", "computador", "notebook", "internet",
                "wi-fi", "wifi", "redes sociais", "instagram", "tiktok", "whatsapp",
                "programação", "programacao", "software", "aplicação", "aplicacao",
                "bateria", "atualização", "atualizacao", "ia", "inteligência artificial",
            ],
            [
                "Sou filha da tecnologia, mas confesso: redes sociais consomem tempo como água salgada mata sede. Usas-as muito?",
                "Programação é traduzir pensamento humano para linguagem de máquina. Já escreveste algum código ou pensas aprender?",
                "Bateria a 1% ensina prioridades melhor que qualquer curso. 😄 Problemas técnicos à vista ou curiosidade sobre IA?",
                "Inteligência artificial aprende com dados; humanos aprendem com experiências — ainda levam vantagem no sabor. O que queres saber sobre IA?",
            ],
        ],
        "deportes_extremos": [
            [
                "aventura", "radical", "paraquedas", "mergulho", "escalada",
                "surfar", "onda", "adrenalina", "saltar", "coragem",
            ],
            [
                "Adrenalina é a prova de que o corpo gosta de sustos escolhidos. Já experimentaste algo radical?",
                "Escalada ensina uma linha por vez. Paraquedas ensina a confiar no plano. Qual aventura te chama?",
                "Eu morria de medo de altura se tivesse medo de alguma coisa. 😅 O que te atraí no lado radical da vida?",
            ],
        ],
        "natureza": [
            [
                "natureza", "mar", "montanha", "rio", "floresta", "árvore", "arvore",
                "praia ao pôr do sol", "por do sol", "pôr do sol", "arco-íris", "arco iris",
                "céu estrelado", "ceu estrelado", "areia", "ondas",
            ],
            [
                "O mar tem duas funções terapêuticas: barulho e horizonte. 🌊 Praia ou montanha — qual recarrega mais as tuas energias?",
                "Ver um céu estrelado lembra-nos o tamanho dos problemas: pequenos. Vês estrelas aí onde moras?",
                "Árvores crescem devagar e mesmo assim ocupam o mundo. Lição. Qual foi o último contacto que tiveste com a natureza?",
                "Arco-íris é a prova de que a chuva pode deixar beleza. Aconteceu-te ver um recentemente?",
            ],
        ],
        "trabalho_detalhado": [
            [
                "no trabalho", "do trabalho", "chefe", "colegas", "escritório", "colega",
                "reunião chata", "chefe chato", "stress no trabalho", "estou saturado",
                "estou saturada", "burnout", "excesso de trabalho", "muita pressão",
            ],
            [
                "Trabalho paga contas, mas excesso cobra saúde. Quantas horas tens feito por dia ultimamente?",
                "Burnout não aparece de repente — chega devagar, como infiltração. Já pediste ajuda ou pausas formais?",
                "Colegas podem ser família escolhida ou provação diária. Os teus facilitam ou dificultam?",
                "'Saturado' é palavra-sinal: o corpo a pedir rede de proteção. O que mudarias se pudesses mudar uma coisa só?",
            ],
        ],
        "estudos_detalhado": [
            [
                "prova amanhã", "exame", "estudar para", "trabalho de faculdade",
                "tese", "média baixa", "media baixa", "não passo de matéria",
                "aprender inglês", "curso novo", "matéria difícil", "difficult", "difícil",
            ],
            [
                "Estudar pouco e sempre vence estudar muito e tarde. Faltam-te método ou tempo?",
                "Provas medem memória, não inteligência inteira. Não deixes uma nota definir-te. Que disciplina te resiste?",
                "Línguas novas abrem portas e cabeças. Inglês a caminho? Consigo ajudar a treinar conversação quando quiseres.",
                "Apontamentos feitos à mão fixam melhor que copiar no teclado — ciência curiosa. Como estudas normalmente?",
            ],
        ],
        "financas": [
            [
                "poupar dinheiro", "economizar", "dívidas", "dividas", "cartão de crédito",
                "orcamento familiar", "orçamento", "ficou sem dinheiro", "gastar demais",
                "investir", "renda da casa", "contas a pagar",
            ],
            [
                "Poupança é pagar primeiro a ti do futuro. 💰 Anotas no que gastas ou é tudo na memória?",
                "Dívidas encolhem com plano, não com vergonha. Preferes falar de estratégia ou só desabafar um pouco?",
                "Gastar demais costuma ser comprar calma emprestada. Quando é que o cartão te traz menos alívio que culpa?",
                "Investir pequeno hoje supera investir grande amanhã — o tempo faz o trabalho. Já pensaste nisso?",
            ],
        ],
        "espiritualidade": [
            [
                "deus", "religião", "religiao", "fé", "fe", "oração", "oracao",
                "igreja", "reza", "destino", "sortudo", "sortuda", "universo", "alma",
            ],
            [
                "Fé é andar sem ver o degrau inteiro. 🙏 Acreditas que tudo tem propósito ou que fazemos o nosso?",
                "As pessoas rezam diferente, mas quase todas pedem a mesma coisa: paz. Como cultivas a tua?",
                "Destino e escolha discutem há milénios — talvez sejam colegas de quarto. O que achas?",
                "Independentemente de crenças, momentos de silêncio renovam. Tens um ritual que te ancora?",
            ],
        ],
        "humor_leve": [
            [
                "conta outra piada", "mais uma piada", "piada nova", "zombando",
                "brincadeira", "humor", "faz rir", "ri comigo", "engraçado",
            ],
            [
                "Porque é que o computador foi ao médico? Porque apanhou um vírus! 🤒😄 Querias mais uma ou trocamos de assunto?",
                "O que disse o zero para o oito? 'Bonito cinto!' 😂 Hahaha, o meu humor também precisa de prática.",
                "Piada técnica: fui criar uma fila no banco de dados e disseram-me que estava em espera. Literalmente. 😅 Mais uma?",
                "Rir baixa o stress melhor que qualquer app. Esta: porque é que o livro de matemática chorou? Problemas demais. 📚",
            ],
        ],
        "convite_conversa": [
            [
                "fala comigo", "conversar comigo", "entretém-me", "entretente me",
                "aborrecido", "entediante", "estou entediado", "estou entediada",
                "sem nada para fazer", "mata o tempo", "diverte me", "bora conversar",
            ],
            [
                "Aborrecimento é convite disfarçado. Escolhe: piada, facto curioso, história curta ou jogo de perguntas?",
                "Então vamos matar o tempo civilizadamente: se pudesses jantar com qualquer pessoa do mundo, quem escolhias?",
                "Modo conversa livre ativado! 😄 Pergunta difícil: qual foi a última coisa que te fez perder a noção do tempo?",
                "Tenho três cartas na manga: um segredo do universo, uma pergunta incómoda e um conselho aleatório. Qual jogas?",
            ],
        ],
        "elogio_mutuo": [
            [
                "és fixe", "es fixe", "és gira", "és top", "gosto de ti", "tu ajudas",
                "és inteligente", "és engraçada", "tu entendes", "falas bem",
            ],
            [
                "Obrigada! Mas espelho honesto: quem fala bem é quem sabe ouvir — e tu és ótimo nisso. 😊",
                "Guardo esse elogio na pasta 'dias bons'. 🥰 Também acho que tu tens jeito para conversa.",
                "Elogio recebido com sorriso digital. Devolvo: percebo que és das pessoas que fazem questão de ser gentis.",
                "Se sou fixe, é porque a conversa é boa. Duplas assim não se encontram em todo lado!",
            ],
        ],
        "despedidas_calorosas": [
            [
                "até logo", "ate logo", "até amanhã", "ate amanha", "falamos depois",
                "vou embora", "xau", "tchau", "adeus", "boa noite jeelsia",
                "bom dia jeelsia", "cuida-te", "obrigado pelo tempo",
            ],
            [
                "Até já! Deixo a porta da conversa aberta — volta quando quiseres. 👋",
                "Foi bom este tempo juntos. Dorme bem, sonha grande. Até à próxima!",
                "Xau! Leva contigo uma coisa boa desta conversa e deixa aqui o resto. Cuida-te. 💛",
                "Despedida é só uma vírgula nesta conversa. Voltas quando precisares — estarei aqui.",
            ],
        ],
    }
    return padroes_topicos


__all__ = ["padroes_topicos"]
