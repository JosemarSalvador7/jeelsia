"""
Dados semente EXTRA para o Jeelsia — mais factos, conhecimentos,
conselhos e histórias sobre muitos tópicos de conversa.

Estruturas idênticas às de logica.knowledge_base.seeds; são fundidas
com os seeds originais pela função `obter_seeds()` do pacote.
"""

SEED_FACTOS_EXTRA = [
    {"topico": "polvo", "facto": "O polvo tem três corações e sangue azul por causa de uma proteína à base de cobre.", "fonte": "Marinha", "categoria": "biologia"},
    {"topico": "banana", "facto": "A banana é radioativa de forma natural, graças ao potássio-40 — mas precisarias de comer milhões de uma vez para te fazer mal.", "fonte": "Ciência Hoje", "categoria": "ciencia"},
    {"topico": "mel", "facto": "O mel nunca estraga: arqueólogos encontraram mel comestível em túmulos egípcios com 3000 anos.", "fonte": "Arqueologia", "categoria": "historia"},
    {"topico": "olho humano", "facto": "O olho humano pode distinguir cerca de 10 milhões de cores diferentes.", "fonte": "Optometry Journal", "categoria": "biologia"},
    {"topico": "velocidade luz", "facto": "Nada no universo se desloca mais depressa do que a luz no vácuo: 299 792 458 metros por segundo.", "fonte": "Física", "categoria": "ciencia"},
    {"topico": "coracao", "facto": "O coração bate cerca de 100 000 vezes por dia e bombeia 7500 litros de sangue.", "fonte": "Cardiologia", "categoria": "biologia"},
    {"topico": "cerebro", "facto": "O cérebro gera entre 12 e 25 watts de eletricidade — suficiente para acender uma lâmpada pequena.", "fonte": "Neuroscience", "categoria": "biologia"},
    {"topico": "angola", "facto": "Angola é o país de língua portuguesa mais extenso depois do Brasil, com costa de quase 1600 km no Atlântico.", "fonte": "Geografia", "categoria": "geografia"},
    {"topico": "rio nilo", "facto": "O Nilo, com cerca de 6650 km, disputa com o Amazonas o título de rio mais longo do mundo.", "fonte": "Enciclopédia", "categoria": "geografia"},
    {"topico": "deserto sahara", "facto": "O Saara é tão grande que caberia os Estados Unidos lá dentro quase duas vezes.", "fonte": "National Geographic", "categoria": "geografia"},
    {"topico": "som", "facto": "Num relâmpago, o trovão chega atrasado porque o som viaja 343 m/s enquanto a luz viaja quase 300 000 km/s.", "fonte": "Física", "categoria": "ciencia"},
    {"topico": "gravidade", "facto": "Na Lua cairias mais devagar: a gravidade lunar é apenas 1/6 da terrestre.", "fonte": "NASA", "categoria": "astronomia"},
    {"topico": "sono", "facto": "Durante o sono o cérebro 'limpa-se': o sistema glinfático remove toxinas acumuladas durante o dia.", "fonte": "Science", "categoria": "biologia"},
    {"topico": "sorriso", "facto": "Um sorriso usa menos músculos (cerca de 17) do que uma franzir de testa (43).", "fonte": "Anatomia", "categoria": "curiosidades"},
    {"topico": "arvores", "facto": "As árvores comunicam e partilham nutrientes através de redes de fungos no solo, apelidadas de 'Wood Wide Web'.", "fonte": "Ecologia", "categoria": "natureza"},
    {"topico": "abelhas", "facto": "Uma abelha precisa de visitar 2000 a 5000 flores para produzir um único frasco pequeno de mel.", "fonte": "Apicultura", "categoria": "natureza"},
    {"topico": "oceano", "facto": "Conhecemos melhor a superfície de Marte do que o fundo dos nossos oceanos — mais de 80% permanece inexplorado.", "fonte": "NOAA", "categoria": "ciencia"},
    {"topico": "dna", "facto": "Se desenrolássemos todo o ADN de um corpo humano, daria para ir à Lua e voltar mais de 2000 vezes.", "fonte": "Genética", "categoria": "biologia"},
]

SEED_CONHECIMENTOS_EXTRA = [
    {"pergunta": "o que e fotossintese?", "resposta": "Fotossíntese é o processo pelo qual as plantas transformam luz, água e dióxido de carbono em glicose e oxigénio — literalmente comida e ar para quase todos nós.", "fonte": "Biologia", "categoria": "ciencia"},
    {"pergunta": "como funciona a internet?", "resposta": "A internet é uma rede mundial de computadores que trocam informação em pequenos pacotes, roteados por cabos submarinos e servidores até chegarem ao teu dispositivo.", "fonte": "Redes", "categoria": "tecnologia"},
    {"pergunta": "o que e inteligencia artificial?", "resposta": "Inteligência artificial é a área da computação que cria sistemas capazes de aprender com dados e tomar decisões — como eu, que aprendi a conversar contigo.", "fonte": "Computação", "categoria": "tecnologia"},
    {"pergunta": "porque chove?", "resposta": "Chove quando o vapor de água nas nuvens se condensa em gotas pesadas demais para flutuarem. A gravidade faz o resto.", "fonte": "Meteorologia", "categoria": "natureza"},
    {"pergunta": "o que e um buraco negro?", "resposta": "Um buraco negro é uma região do espaço onde a gravidade é tão intensa que nem a luz escapa — nasce geralmente do colapso de estrelas gigantes.", "fonte": "Astronomia", "categoria": "astronomia"},
    {"pergunta": "quem foi agostinho neto?", "resposta": "Agostinho Neto foi o primeiro presidente de Angola, líder da independência em 1975 e também poeta. É uma das figuras centrais da história angolana.", "fonte": "História", "categoria": "historia"},
    {"pergunta": "o que e a zika", "resposta": "A Zika é uma doença transmitida pelo mosquito Aedes aegypti, geralmente ligeira, mas perigosa na gravidez por estar associada a malformações fetais.", "fonte": "OMS", "categoria": "saude"},
    {"pergunta": "como poupar dinheiro", "resposta": "Poupa pagando-te primeiro: define um valor fixo mensal que sai logo após o salário, antes das contas. O que sobra adapta-se — o que sobra raramente existe.", "fonte": "Finanças pessoais", "categoria": "dinheiro"},
    {"pergunta": "o que e stress", "resposta": "Stress é a resposta do corpo a exigências sentidas como ameaça: adrenalina, cortisol, coração acelerado. Em doses curtas motiva; prolongado adoece.", "fonte": "Psicologia", "categoria": "saude"},
    {"pergunta": "para que serve o sono", "resposta": "Dormir consolida memórias, repara tecidos, regula hormonas e limpa resíduos do cérebro. Sem sono suficiente, tudo — até o humor — funciona pior.", "fonte": "Medicina", "categoria": "saude"},
    {"pergunta": "o que e democracia", "resposta": "Democracia é o sistema em que o poder emana do povo, exercido por voto livre, com separação de poderes e proteção de direitos fundamentais.", "fonte": "Ciência Política", "categoria": "sociedade"},
    {"pergunta": "como funciona uma vacina", "resposta": "A vacina apresenta ao corpo uma versão inofensiva do micróbio para o sistema imunitário treinar defesas — assim, se o micróbio real aparecer, o corpo já sabe combatê-lo.", "fonte": "Imunologia", "categoria": "saude"},
]

SEED_CONSELHOS_EXTRA = [
    {"problema": "luto", "conselho": "O luto não tem prazo nem sequência certa. Chorar quando vier, falar quando houver vontade — o tempo não cura sozinho, mas com cuidado alivia.", "categoria": "emocional"},
    {"problema": "timidez", "conselho": "A timidez encolhe com exposição pequena: uma pergunta a um desconhecido por dia. Ninguém nasceu confiante; a coragem é músculo.", "categoria": "social"},
    {"problema": "raiva do parceiro", "conselho": "Na discussão, fala do que sentes ('fiquei magoado quando...') em vez do que o outro é ('tu és sempre...'). Ataca o problema, não a pessoa.", "categoria": "relacoes"},
    {"problema": "burnout", "conselho": "Burnout pede duas coisas: descanso imediato e mudança estrutural. Férias sem alterar a carga regressam com o mesmo peso.", "categoria": "trabalho"},
    {"problema": "indecisao", "conselho": "Diante de duas opções, lança uma moeda — e repara em que resultado te deixa aliviado. O corpo decide antes da cabeça.", "categoria": "produtividade"},
    {"problema": "solteirice", "conselho": "Antes de procurar companhia, constrói a vida que gostarias de partilhar. Pessoas atraem-se pelos projetos, não pela carência.", "categoria": "relacoes"},
    {"problema": "ansiedade social", "conselho": "Numa reunião social, foca-te em fazer perguntas aos outros. As pessoas adoram quem as escuta — e tu esqueces-te de vigiar a ti mesmo.", "categoria": "social"},
    {"problema": "gastos por impulso", "conselho": "Regra das 24 horas: tudo o que não é essencial espera um dia. Metade dos desejos morre de velhice antes do pagamento.", "categoria": "dinheiro"},
    {"problema": "conflito no trabalho", "conselho": "Resolve conflitos em privado, elogia em público. A humilhação fecha portas que anos de confiança não reabrem.", "categoria": "trabalho"},
    {"problema": "acordar desmotivado", "conselho": "Não esperes motivação para começar; começa para a motivação aparecer. Um prato lavado abre a manhã melhor que dez planos.", "categoria": "bem-estar"},
]

SEED_HISTORIAS_EXTRA = [
    {
        "titulo": "a menina e o mar de luanda",
        "conteudo": (
            "Em Luanda, uma menina colecionava conchas na Ilha, dizendo que cada uma guardava "
            "uma conversa ouvida do mar. Um pescador velho perguntou-lhe para que queria tantas conchas. "
            "'Para quando o mar precisar de devolver o que ouviu', respondeu ela. O pescador riu — "
            "e nessa noite contou à esposa, pela primeira vez em anos, o que lhe ia na alma. "
            "O mar, afinal, emprestava as suas conversas a quem sabia escutar."
        ),
        "autor": "Conto urbano angolano",
        "categoria": "filosofica",
        "origem": "seed",
    },
    {
        "titulo": "o relógio que parou",
        "conteudo": (
            "Havia um relógio na praça que parava sempre às seis e um minuto. Ninguém consertava, "
            "porque a essa hora a cidade inteira olhava para cima e respirava junta. Quando finalmente "
            "o arranjam, notaram algo estranho: ninguém mais parava às seis. O relógio, perceberam tarde, "
            "não marcava horas — marcava pausas. Voltaram a deixá-lo parado. Às vezes um defeito é serviço público."
        ),
        "autor": "Microconto",
        "categoria": "reflexiva",
        "origem": "seed",
    },
    {
        "titulo": "dois amigos e a árvore",
        "conteudo": (
            "Dois amigos discutiram tanto que passaram um ano sem se falar. No quintal entre as duas casas, "
            "plantaram à vez, sem combinar, uma mangueira — cada um cuidava da metade do seu lado. "
            "Quando a árvore deu o primeiro fruto, caíram dois: um para cada casa. Os dois apareceram "
            "à mesma hora na vedação, com a fruta na mão. Não pediram desculpa. Partilharam o manga."
        ),
        "autor": "Parábola moderna",
        "categoria": "relacoes",
        "origem": "seed",
    },
    {
        "titulo": "o professor sem quadro",
        "conteudo": (
            "Numa aldeia sem material escolar, o professor escrevia lições no ar com o dedo. "
            "'Como queres que aprendamos o que não se vê?', perguntaram. Ele respondeu: 'Vede-me a mão; "
            "onde ela passa, fica o pensamento.' Anos depois, os alunos seguiam professores e diziam: "
            "'Aprendi a ver o invisível — foi a primeira coisa escrita naquela escola.'"
        ),
        "autor": "Anônimo",
        "categoria": "inspiradora",
        "origem": "seed",
    },
]

__all__ = [
    "SEED_FACTOS_EXTRA",
    "SEED_CONHECIMENTOS_EXTRA",
    "SEED_CONSELHOS_EXTRA",
    "SEED_HISTORIAS_EXTRA",
]
