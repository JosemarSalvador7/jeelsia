import sys
import random
import time
import threading
from datetime import datetime, timedelta
import platform
import re
import humanize
from rapidfuzz import fuzz
from logica import KnowledgeBase
from logica import (
    mensagens_busca,
    prefixos_factuais,
    padroes_conversa,
    sem_resposta,
)
# Novos módulos: utilitários de texto, emoções e contexto da conversa
from logica.utils import normalizar_texto, analisar_similaridade
from logica.emocoes import (
    detectar_emocao,
    deve_priorizar_empatia,
    responder_com_empatia,
)
from logica.contexto import (
    criar_estado,
    extrair_topico,
    manter_contexto,
    obter_resposta_unica,
    aplicar_reflections,
)
# Fio condutor: desenvolve a conversa sem perder o contexto entre turnos
from logica.contexto.fio import (
    PERGUNTAS_PROGRESSIVAS as PERGUNTAS_EMOÇÕES_FIO,
    atualizar_fio,
    encerrar_fio_se_despedida,
    proxima_pergunta_progressiva,
    responder_elipse,
    retomar_fio,
)
# Módulo de comunicação: fluidez e naturalidade das respostas
from logica.comunicacao import (
    gerar_transicao,
    gerar_pergunta_seguimento,
    gerar_resposta_curta,
    gerar_reconhecimento,
    gerar_despedida,
    finalizar_conversa,
    detectar_intencoes,
)
from logica.comunicacao.fluidez import compor_resposta
# Perfil do utilizador (tabela SQLite) + conversa multi-assunto
from logica.perfil import (
    PerfilUtilizador,
    contexto_pessoal,
    extrair_informacoes,
    personalizar_resposta,
)
from logica.perfil.perfil import saudação_com_perfil, sugestao_por_gostos
from logica.perfil.topicos import (
    gerir_topicos,
    persistir_fio_no_topico,
    sincronizar_fio_com_topico,
    transicao_natural,
)
import uuid as _uuid
# Configurações iniciais
sys.dont_write_bytecode = True

# Configuração de encoding para Windows
if sys.platform.startswith("win"):
    try:
        import io

        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    except Exception as e:
        print(f"Erro ao configurar encoding: {e}")

# Ativar localização para português
try:
    humanize.activate("pt_PT")
except Exception as e:
    print(f"Erro ao ativar localização: {e}")


class Jeelsia:
    def __init__(self) -> None:
        """Inicializa a assistente virtual Jeelsia"""
        try:
            self.kb = KnowledgeBase("./cerebro.db")
        except Exception as e:
            print(f"Erro crítico ao inicializar base de conhecimento: {e}")
            sys.exit(1)

        self.personalidade = {
            "nome": "Jeelsia",
            "origem": "Angola",
            "estado": "animada",
            "criador": "uma equipa de desenvolvedores angolanos!",
        }

        self.ultima_interacao = time.time()
        self.ativo = True
        self.evento_terminar = threading.Event()

        # Estado de contexto/memória (gerido pelo módulo logica.contexto)
        self.estado = criar_estado()
        # Atalhos compatíveis com o resto do código
        self.ultimas_respostas = self.estado["ultimas_respostas"]
        self.max_historico_respostas = self.estado["max_historico_respostas"]
        self.historico_conversa = self.estado["historico_conversa"]
        self.max_historico = self.estado["max_historico"]
        self.ultimo_topico = self.estado["ultimo_topico"]

        try:
            self.prefixos_factuais = prefixos_factuais()
            self.padroes_conversa = padroes_conversa()
            self.mensagens_busca = mensagens_busca()
            self.sem_resposta = sem_resposta()
        except Exception as e:
            print(f"Erro ao carregar configurações: {e}")
            sys.exit(1)

        self.sistema_operacional = platform.system()

        try:
            self.fact_knowledge_list = self.kb.listar_topicos_conhecimentos()
        except Exception as e:
            print(f"Erro ao listar tópicos: {e}")
            self.fact_knowledge_list = []

        # Perfil do utilizador — tabela `perfil_utilizador` no cerebro.db.
        # Guarda nome, preferências, humor e histórico de assuntos para
        # gerar respostas mais personalizadas entre sessões.
        try:
            self.perfil = PerfilUtilizador(self.kb.conn)
            self.ctx_perfil = contexto_pessoal(self.perfil)
        except Exception as e:
            print(f"Erro ao inicializar perfil do utilizador: {e}")
            self.perfil = None
            self.ctx_perfil = {}
        self.sessao_id = _uuid.uuid4().hex[:8]

        try:
            threading.Thread(target=self._monitorar_inatividade, daemon=True).start()
        except Exception as e:
            print(f"Erro ao iniciar monitoramento: {e}")

    # ------------------------------------------------------------------
    # Estas funções foram movidas para módulos próprios (logica.emocoes e
    # logica.contexto). Mantemos aqui delegadores finos por compatibilidade.
    # ------------------------------------------------------------------

    def _detectar_emocao(self, texto: str) -> dict:
        """Detecta emoções no texto do usuário (ver logica.emocoes)."""
        return detectar_emocao(texto)

    def _responder_com_empatia(self, emocao: dict, mensagem: str) -> str | None:
        """Gera resposta empática conforme a emoção (ver logica.emocoes)."""
        return responder_com_empatia(emocao, mensagem)

    def _aplicar_reflections(self, texto: str) -> str:
        """Aplica reflexões para inverter pronomes (ver logica.contexto)."""
        return aplicar_reflections(texto)

    def _obter_resposta_unica(self, resposta: str) -> str:
        """Evita respostas repetidas recentemente (ver logica.contexto)."""
        return obter_resposta_unica(self.estado, resposta)

    def _extrair_topico(self, mensagem: str) -> str | None:
        """Extrai o tópico principal da mensagem (ver logica.contexto)."""
        return extrair_topico(mensagem)

    def _manter_contexto(self, mensagem: str) -> bool:
        """Mantém o contexto da conversa (ver logica.contexto)."""
        return manter_contexto(self.estado, mensagem)


    def _responder_palavras_curtas(self, mensagem: str) -> str | None:
        """Responde a palavras curtas como 'sim', 'não', etc.

        A lógica agora vive em ``logica.comunicacao.gerar_resposta_curta``:
        as reformulações dependem do tópico anterior, dando continuidade
        natural à conversa em vez de despejar frases fixas.
        """
        return gerar_resposta_curta(mensagem, self.estado)

    # ------------------------------------------------------------------
    # Auxiliares de perfil (tabela perfil_utilizador / historico_conversas)
    # ------------------------------------------------------------------

    def _registra_turno(self, mensagem: str, intencao: str | None,
                        emocao: dict | None, info_topicos: dict) -> None:
        """Persiste o turno na tabela ``historico_conversas`` e atualiza
        o último assunto do perfil — memória entre sessões."""
        if not self.perfil:
            return
        try:
            dom = (emocao or {}).get("dominante")
            topico = info_topicos.get("topico") if isinstance(info_topicos, dict) else None
            self.perfil.registrar_turno(
                mensagem=mensagem,
                intencao=intencao,
                emocao=None if dom == "neutro" else dom,
                topico=topico,
                sessao=self.sessao_id,
            )
            if topico:
                self.perfil.registar_assunto(topico)
                self.ctx_perfil["ultimo_assunto"] = topico
        except Exception as e:
            print(f"Erro ao registar turno no histórico: {e}")

    @staticmethod
    def _inserir_nome(resposta: str, nome: str) -> str:
        """Insere o nome do utilizador na primeira frase da resposta."""
        frases = re.split(r"(?<=[.!?])\s+", resposta.strip())
        if not frases:
            return resposta
        f0 = frases[0]
        if nome.lower() in f0.lower():
            return resposta
        if f0.endswith("?"):
            frases[0] = f0[:-1].rstrip(", ") + f", {nome}?"
        elif f0.endswith("!"):
            frases[0] = f0[:-1].rstrip(", ") + f", {nome}!"
        elif f0.endswith("."):
            frases[0] = f0[:-1].rstrip(", ") + f". Fico aqui contigo, {nome}."
        else:
            frases[0] = f"{f0}, {nome}."
        return " ".join(frases)

    def _sugerir_comando_similar(self, comando: str) -> str | None:
        """Sugere comandos similares quando não entende o que o usuário disse"""
        try:
            comando_lower = comando.lower()
            
            # Lista de comandos conhecidos com suas variações
            comandos_conhecidos = {
                "falar sobre": ["fale sobre", "conte sobre", "me fale sobre", "explique sobre", "fala sobre"],
                "calcular": ["calcula", "quanto é", "conta", "soma", "subtrai", "multiplica", "divide", "faz a conta"],
                "tocar música": ["tocar", "toca", "música", "tocar música", "toca música", "youtube", "ouvir"],
                "hora": ["que horas são", "horas", "que horas", "relógio"],
                "data": ["que dia é", "data", "dia", "calendário"],
                "conselho": ["conselho", "ajuda", "preciso de ajuda", "me aconselha", "orientação"],
                "piada": ["conta uma piada", "piada", "algo engraçado", "me faz rir"],
                "história": ["conta uma história", "história", "conte uma história"],
                "tempo": ["clima", "tempo", "previsão do tempo", "vai chover"],
                "sair": ["sair", "fechar", "terminar", "exit", "quit"],
                "identidade": ["quem é você", "quem és tu", "o que és", "apresenta-te"],
                "criador": ["quem te criou", "teu criador", "desenvolvedor", "quem te fez"],
                "origem": ["de onde és", "de onde você é", "nacionalidade", "és de onde"],
                "idade": ["quantos anos tens", "idade", "anos"],
                "conhecimento": ["o que sabes", "o que podes fazer", "comandos", "funcionalidades"],
                "estado": ["como estás", "como vai", "tudo bem", "estás bem"],
                "elogio": ["gostei", "muito bom", "excelente", "incrível", "adorei", "amei"],
                "agradecimento": ["obrigado", "obrigada", "valeu", "agradeço"],
                "fome": ["com fome", "fome", "comer", "lanchar"],
                "cansado": ["cansado", "sono", "preciso dormir", "exausto"],
                "teamo": ["te amo", "amo você", "gosto de você", "adoro você"],
                "duvida": ["dúvida", "não sei", "indeciso", "talvez"],
                "surpresa": ["uau", "nossa", "caramba", "incrível", "sensacional"]
            }
            
            # Calcula similaridade com cada comando
            melhores_resultados = []
            for comando_key, variacoes in comandos_conhecidos.items():
                for variacao in variacoes:
                    try:
                        similaridade = fuzz.QRatio(comando_lower, variacao)
                        if similaridade >= 70:  # Limite de similaridade
                            melhores_resultados.append((comando_key, similaridade, variacao))
                    except:
                        continue
            
            # Ordena por similaridade
            melhores_resultados.sort(key=lambda x: x[1], reverse=True)
            
            if melhores_resultados:
                melhor_comando, score, variacao = melhores_resultados[0]
                
                # Mapeamento de sugestões amigáveis
                sugestoes = {
                    "falar sobre": f"Querias dizer 'falar sobre' algo? Podes perguntar 'fale sobre [tema]'!",
                    "calcular": f"Querias fazer uma conta? Diz 'calcular 2+2' ou 'quanto é 3*4'!",
                    "tocar música": f"Querias ouvir música? Diz 'tocar [nome da música]' ou 'toca música'!",
                    "hora": "Querias saber as horas? Diz 'que horas são'!",
                    "data": "Querias saber a data? Diz 'que dia é hoje'!",
                    "conselho": "Querias um conselho? Diz 'me dá um conselho'!",
                    "piada": "Querias ouvir uma piada? Diz 'conta uma piada'!",
                    "história": "Querias ouvir uma história? Diz 'conta uma história'!",
                    "tempo": "Querias saber o tempo? Diz 'previsão do tempo'!",
                    "sair": "Querias sair? Diz 'sair' ou 'fechar'!",
                    "identidade": "Querias saber quem sou? Diz 'quem és tu'!",
                    "criador": "Querias saber quem me criou? Diz 'quem te criou'!",
                    "origem": "Querias saber de onde sou? Diz 'de onde és'!",
                    "idade": "Querias saber a minha idade? Diz 'quantos anos tens'!",
                    "conhecimento": "Querias saber o que sei fazer? Diz 'o que sabes' ou 'comandos'!",
                    "estado": "Querias saber como estou? Diz 'como estás'!",
                    "elogio": "Ah, parece que gostaste! Fico feliz! 😊",
                    "agradecimento": "De nada! Fico feliz em ajudar!",
                    "fome": "Tens fome? Diz 'estou com fome' e dou sugestões!",
                    "cansado": "Estás cansado? Diz 'estou cansado' e dou dicas!",
                    "teamo": "Ah, que amor! Também gosto muito de ti! 💕",
                    "duvida": "Tens dúvidas? Podes perguntar 'o que é [assunto]'!",
                    "surpresa": "Fico feliz que tenhas gostado! 🎉"
                }
                
                sugestao = sugestoes.get(melhor_comando)
                if sugestao:
                    return f"Hmm, não entendi bem '{comando}'... Será que não querias dizer: {sugestao}"
            
            return None
            
        except Exception as e:
            print(f"Erro ao sugerir comando similar: {e}")
            return None

    def _fallback_resposta(self, comando: str) -> str:
        """Resposta de fallback quando nada mais funciona"""
        try:
            # Primeiro tenta sugerir um comando similar
            sugestao = self._sugerir_comando_similar(comando)
            if sugestao:
                return sugestao
            
            # Se não houver sugestão, usa respostas genéricas
            return random.choice([
                "Desculpa, não entendi o que quiseste dizer. Podes reformular de outra forma?",
                "Hmm, não consegui interpretar isso. Tenta usar palavras mais simples ou específicas.",
                "Não tenho certeza do que quiseste perguntar. Podes tentar novamente?",
                "Ops, não reconheci esse comando. Podes explicar de outra maneira?",
                "Não entendi bem... Talvez possas perguntar de forma diferente?",
                "Fiquei confusa com o que disseste. Podes reformular, por favor?",
                "Não sei como responder a isso. Que tal tentarmos outro assunto?",
                "Não consegui processar isso. Podes ser mais claro na tua pergunta?",
                "Hmm, essa pergunta é complicada para mim. Podes tentar de outro jeito?",
                "Desculpa, não aprendi a lidar com isso ainda. Podes perguntar outra coisa?"
            ])
        except Exception as e:
            print(f"Erro no fallback: {e}")
            return "Desculpa, ocorreu um erro. Podes tentar novamente?"

    def _responder_elogio_com_contexto(self, elogio: str, respostas_base: list) -> str:
        """Responde a um elogio com base no contexto da conversa anterior"""
        try:
            # Pega a última interação do usuário (excluindo o elogio atual)
            ultima_msg = ""
            if len(self.historico_conversa) >= 2:
                # Pega a penúltima mensagem (a anterior ao elogio)
                ultima_msg = self.historico_conversa[-2]
            elif self.historico_conversa:
                ultima_msg = self.historico_conversa[-1]
            
            # Extrai o assunto da última mensagem
            assunto = extrair_topico(ultima_msg) if ultima_msg else "conversa"
            
            # Respostas personalizadas com contexto
            respostas_contexto = [
                f"Ah, que bom que gostaste! Fico feliz em saber que a minha resposta sobre '{assunto}' te agradou! 😊",
                f"Que legal! Saber que apreciaste o que falei sobre '{assunto}' me deixa muito contente!",
                f"Fico toda feliz com o teu elogio! Especialmente porque foi sobre o que falei acerca de '{assunto}'!",
                f"Obrigada! Foi um prazer falar sobre '{assunto}' contigo. Que bom que gostaste!",
                f"Ah, que fofo! Fico feliz que tenhas gostado da nossa conversa sobre '{assunto}'!",
                f"Saber que apreciaste o que compartilhei sobre '{assunto}' faz o meu dia melhor!",
                f"Que bom! Adoro quando a nossa conversa sobre '{assunto}' é tão bem recebida!",
                f"Fico radiante! Falar sobre '{assunto}' contigo é sempre especial, e saber que gostaste é ainda melhor!"
            ]
            
            # Se não houver contexto, usa respostas genéricas
            if not ultima_msg or assunto == "conversa":
                return random.choice([
                    "Ah, obrigada! Fico toda feliz com o teu elogio! 😊",
                    "Que fofo! Saber que gostaste me deixa muito contente!",
                    "Obrigada! Foi um prazer conversar contigo!",
                    "Fico feliz em saber que gostaste! O que mais gostarias de explorar?"
                ] + respostas_base)
            
            # Escolhe uma resposta com contexto ou uma genérica
            if random.random() < 0.7:  # 70% de chance de usar contexto
                return random.choice(respostas_contexto)
            else:
                return random.choice(respostas_base)
                
        except Exception as e:
            print(f"Erro ao responder elogio com contexto: {e}")
            return random.choice(respostas_base)

    def responder(self, mensagem: str) -> str:
        """Método principal para processar e responder mensagens.

        Fluxo com comunicação fluida (logica.comunicacao) e fio condutor
        (logica.contexto.fio) para desenvolver a conversa sem perder contexto:
        1. Mensagens vazias → convite amigável;
        2. Emoção forte → empatia + pergunta progressiva (desenvolve o tema);
        3. Mensagem vaga ("pois", "hmm") com fio ativo → retoma o desabafo;
        4. Elipse ("sim"/"não" respondendo à última pergunta da IA) → o fio
           reconhece a referência implícita e continua o assunto;
        5. Resposta normal → composta com transição/pergunta de seguimento;
        6. No fim de cada turno, ``atualizar_fio`` regista emoção ativa,
           última pergunta aberta e memória curta — é isto que permite à
           conversa "lembrar-se" de onde ficou.
        """
        try:
            if not mensagem or not mensagem.strip():
                return random.choice([
                    "Estou aqui, ouvindo atentamente! O que gostaria de compartilhar?",
                    "Às vezes o silêncio também fala. Estou pronta quando você estiver!",
                    "Pensando em algo especial para conversarmos hoje?",
                    "Sim? Estou à espera do teu comando.",
                    "O que gostaria de fazer hoje? Estou aqui para ajudar!",
                    "Parece que o comando ficou em branco. O que gostaria de fazer ou perguntar?"
                ])

            # Detecta emoção (lógica movida para logica.emocoes)
            emocao = detectar_emocao(mensagem)

            # ---- Perfil do utilizador: aprendizagem implícita ----------
            # "o meu nome é X", "gosto de Y", "trabalho como Z" ficam
            # registados na tabela perfil_utilizador e são usados para
            # personalizar as respostas deste e de próximos turnos.
            if self.perfil:
                try:
                    novos = extrair_informacoes(mensagem, self.perfil)
                    if novos:
                        self.ctx_perfil = contexto_pessoal(self.perfil)
                    if emocao.get("dominante") not in (None, "neutro"):
                        self.perfil.registar_humor(emocao["dominante"])
                        self.ctx_perfil["humor"] = emocao["dominante"]
                except Exception as e:
                    print(f"Erro ao atualizar perfil: {e}")

            # ---- Multi-assunto: pilha de tópicos abertos ----------------
            # Humanos conversam sobre vários assuntos e retomam-nos depois.
            # gerir_topicos mantém até 3 fios temáticos; o fio clássico
            # passa a operar sobre o tópico ATIVO (sincronizar_fio...).
            info_topicos = {"acao": "continua", "topico": None, "anterior": None}
            try:
                info_topicos = gerir_topicos(self.estado, mensagem)
                sincronizar_fio_com_topico(self.estado, emocao)
            except Exception as e:
                print(f"Erro ao gerir tópicos: {e}")

            # Mantém contexto ANTES de compor respostas dependentes dele
            manter_contexto(self.estado, mensagem)
            self.estado["turnos"] = self.estado.get("turnos", 0) + 1

            # Encerrar o fio emocional quando o utilizador fecha o tema
            encerrar_fio_se_despedida(self.estado, mensagem)

            # ---- Fio condutor: elipses e retomadas -------------------
            # "sim"/"pois" respondendo a uma pergunta anterior da IA não
            # são comandos isolados — são continuidade. O fio resolve a
            # referência implícita e desenvolve o tema em vez de cair no
            # menu fixo de palavras curtas.
            ponte_topico = transicao_natural(info_topicos, self.estado)

            elipse = responder_elipse(self.estado, mensagem)
            if elipse:
                atualizar_fio(self.estado, mensagem, elipse, emocao=None)
                persistir_fio_no_topico(self.estado)
                self._registra_turno(mensagem, "elipse", emocao, info_topicos)
                return obter_resposta_unica(self.estado, elipse)

            # Mensagem vaga ("hmm", "ah", "entendi") com desabafo pendente
            # → retomar o fio ativo, citando a última frase relevante.
            retomada = retomar_fio(self.estado, mensagem)
            if retomada:
                atualizar_fio(self.estado, mensagem, retomada, emocao=None)
                persistir_fio_no_topico(self.estado)
                self._registra_turno(mensagem, "retomada", emocao, info_topicos)
                return obter_resposta_unica(self.estado, retomada)

            # Resposta empática: tem PRIORIDADE quando o utilizador fala
            # de si com emoção forte ("estou mal", "não correu bem"),
            # mesmo que um padrão genérico também coincida. Quando a
            # empatia não é prioritária, o fluxo segue para intenções —
            # mas recorda a emoção para contextualizar a resposta.
            prioridade_empatia = deve_priorizar_empatia(emocao, mensagem)
            resposta_empatica = None
            if prioridade_empatia:
                resposta_empatica = responder_com_empatia(
                    emocao, mensagem, self.estado
                )
            else:
                # Regista apenas a memória emocional (sem monopolizar a resposta)
                if emocao.get("dominante") != "neutro":
                    self.estado["ultima_emocao"] = emocao["dominante"]

            if resposta_empatica:
                # Desenvolvimento do tema: em vez de rematar sempre com a
                # mesma pergunta genérica, usa a próxima pergunta
                # progressiva do fio (causa → tempo → gatilho → apoio).
                follow = proxima_pergunta_progressiva(self.estado)
                if not resposta_empatica.rstrip().endswith("?"):
                    if not follow:
                        follow = gerar_pergunta_seguimento(self.estado, "emocao")
                    if follow:
                        resposta_empatica = f"{resposta_empatica} {follow}"
                # Personalização pelo perfil: nome/assunto conhecido tornam
                # a empatia mais humana ("Força, Carlos. ..." em vez de
                # frases fixas impessoais).
                nome = self.ctx_perfil.get("nome")
                if nome and random.random() < 0.5:
                    resposta_empatica = self._inserir_nome(resposta_empatica, nome)
                if ponte_topico:
                    resposta_empatica = f"{ponte_topico} {resposta_empatica[0].lower() + resposta_empatica[1:]}"
                resposta_final = obter_resposta_unica(self.estado, resposta_empatica)
                atualizar_fio(self.estado, mensagem, resposta_final, emocao)
                persistir_fio_no_topico(self.estado)
                self._registra_turno(mensagem, "empatia", emocao, info_topicos)
                return resposta_final

            # Verifica comandos especiais de saída
            if mensagem.lower() in ["sair", "fechar", "terminar", "exit", "quit"]:
                self.ativo = False
                self.evento_terminar.set()
                return finalizar_conversa(self.estado)

            # Reconhecimento imediato para mensagens longas/elaboradas
            reconhecimento = gerar_reconhecimento(mensagem)

            # Processa o comando
            resposta = self._processar_comando(mensagem)

            # Fio condutor: se o turno não casou em nenhuma intenção mas
            # há um desabafo ativo, a mensagem livre é tratada como
            # CONTINUIDADE do tema — nunca como "comando não entendido".
            tipo_antes = getattr(self, "_ultimo_tipo_resposta", None)
            if tipo_antes == "fallback":
                follow = proxima_pergunta_progressiva(self.estado)
                if follow:
                    ack = random.choice([
                        "Entendo, e continuamos por aí.",
                        "Recebo isso — vamos devagar.",
                        "Obrigado por partilhares. Segue o fio:",
                    ])
                    resposta = f"{ack} {follow[0].lower() + follow[1:]}"
                    self._ultimo_tipo_resposta = tipo = "emocao"
                    atualizar_fio(
                        self.estado, mensagem, follow, emocao=None
                    )
                    _f = self.estado.get("fio") or {}
                    _f["ultima_pergunta"] = follow
                    persistir_fio_no_topico(self.estado)
                    self._registra_turno(mensagem, "continuidade", emocao, info_topicos)
                    return obter_resposta_unica(self.estado, resposta)

            # Fluidez contextual: se a intenção casada era genérica mas o
            # utilizador demonstrou emoção neste turno (ex.: "estou bem,
            # obrigado" após um dia mau), emendar com continuidade em vez
            # de responder como se nada tivesse acontecido.
            tipo = getattr(self, "_ultimo_tipo_resposta", None)

            # Fio condutor: quando há um desabafo emocional pendente e o
            # turno atual é apenas social (obrigado/saudação/estado), a
            # resposta deve RETOMAR o fio — nunca encerrar o assunto como
            # se a conversa começasse do zero.
            fio = self.estado.get("fio") or {}
            if (
                resposta
                and tipo in ("agradecimento", "saudacao", "estado", "palavra_curta", None)
                and fio.get("emocao") in PERGUNTAS_EMOÇÕES_FIO
            ):
                ponte = random.choice([
                    "Antes de mais, retomando o que estavas a contar:",
                    "Sobre o que mencionaste há pouco,",
                    "Não quero deixar o teu desabafo em suspenso —",
                ])
                follow = proxima_pergunta_progressiva(self.estado)
                if follow:
                    resposta = f"{resposta} {ponte} {follow[0].lower() + follow[1:]}"
                    self._ultimo_tipo_resposta = tipo = "emocao"

            if (
                resposta
                and emocao.get("dominante") in ("tristeza", "raiva", "medo")
                and emocao.get(emocao["dominante"], 0) >= 40
                and tipo in ("agradecimento", "estado", "saudacao", None)
            ):
                ponte = random.choice([
                    "Ainda assim, sinto muito pelo teu dia difícil.",
                    "Mesmo assim, espero que as coisas melhorem depressa.",
                    "Fico contente, mas continua a contar comigo sobre o que te pesa.",
                ])
                resposta = f"{resposta} {ponte}"
                self._ultimo_tipo_resposta = "emocao"
                tipo = "emocao"

            # Aplica reflexões apenas quando o corpo da resposta é uma
            # pergunta DIRETA ao utilizador — evita espelhar pronomes no
            # meio de frases fixas e corromper texto ("com tu ajuda"?).
            if resposta and resposta.rstrip().endswith("?"):
                resposta = aplicar_reflections(resposta)
            eh_conversacional = tipo in ("palavra_curta", "fallback", "saudacao")
            if resposta and not eh_conversacional:
                resposta = compor_resposta(resposta, self.estado, tipo_resposta=tipo)

            if resposta and reconhecimento:
                resposta = f"{reconhecimento} {resposta[0].lower() + resposta[1:]}"

            # ---- Ponte de multi-assunto + perfil ----------------------
            if resposta and ponte_topico:
                resposta = f"{ponte_topico} {resposta[0].lower() + resposta[1:]}"
            if resposta:
                resposta = personalizar_resposta(resposta, self.ctx_perfil, tipo)

            # Evita repetição
            if resposta:
                resposta = obter_resposta_unica(self.estado, resposta)

            # Atualiza o fio condutor no fim do turno — é isto que permite
            # à conversa "lembrar-se" do tema/emoção pendente no próximo.
            atualizar_fio(self.estado, mensagem, resposta, emocao)
            persistir_fio_no_topico(self.estado)
            self._registra_turno(mensagem, tipo, emocao, info_topicos)

            return resposta if resposta else "Desculpa, não entendi. Podes reformular?"

        except KeyboardInterrupt:
            self.ativo = False
            self.evento_terminar.set()
            return "A sair..."
        except Exception as e:
            print(f"Erro em responder: {e}")
            return "Ocorreu um erro ao processar tua mensagem. Tenta novamente."

    def _processar_comando(self, comando: str) -> str | None:
        """Processa o comando e retorna uma resposta"""
        try:
            # Primeiro tenta responder palavras curtas
            resposta_curta = self._responder_palavras_curtas(comando)
            if resposta_curta:
                self._ultimo_tipo_resposta = "palavra_curta"
                return resposta_curta

            # Primeiro tenta conversa
            resposta_conversa = self._manter_conversa(comando)
            if resposta_conversa:
                return resposta_conversa

            # Remove 'jeelsia' do comando e tenta novamente
            try:
                comando_limpo = re.sub(
                    r"\bjeelsia\b", "", comando, flags=re.IGNORECASE
                ).strip()
                if comando_limpo != comando:
                    resposta_conversa = self._manter_conversa(comando_limpo)
                    if resposta_conversa:
                        return resposta_conversa
            except re.error:
                pass

            # Se não for conversa, tenta responder pergunta
            resposta_pergunta = self._responder_pergunta(comando)
            if resposta_pergunta and resposta_pergunta not in self.sem_resposta:
                self._ultimo_tipo_resposta = "conhecimento"
                return resposta_pergunta

            # ULTIMO FALLBACK: Sugere comandos similares
            self._ultimo_tipo_resposta = "fallback"
            return self._fallback_resposta(comando)

        except Exception as e:
            print(f"Erro inesperado em _processar_comando: {e}")
            self._ultimo_tipo_resposta = "fallback"
            return self._fallback_resposta(comando)

    def _manter_conversa(self, comando: str) -> str | None:
        """Gerencia conversas e comandos específicos"""
        try:
            comando_lower = comando.lower()
            listas = self.padroes_conversa

            # Saudações
            if analisar_similaridade(comando_lower, listas["saudacao"]):
                try:
                    agora = datetime.now()
                    if agora.hour < 12:
                        periodo = "manhã"
                    elif agora.hour < 18:
                        periodo = "tarde"
                    else:
                        periodo = "noite"

                    self._ultimo_tipo_resposta = "saudacao"

                    # Saudação personalizada com o perfil do utilizador:
                    # se soubermos o nome (tabela perfil_utilizador),
                    # cumprimentamos pelo nome e retomamos o último
                    # assunto da sessão anterior — como um humano faria.
                    if self.ctx_perfil.get("nome"):
                        saud = saudação_com_perfil(self.ctx_perfil, periodo)
                        if saud:
                            return saud

                    # Se já conversámos antes, saudação com continuidade
                    if self.estado.get("turnos", 0) > 1:
                        return random.choice([
                            f"Olá de novo! Boa {periodo.capitalize()}! Sobre o que querias continuar?",
                            f"Oi! Retomando a nossa conversa — boa {periodo}! Em que posso ajudar agora?",
                            f"Bom de novo falar contigo nesta {periodo}! O que tens em mente?",
                        ])

                    return random.choice([
                        f"Boa {periodo.capitalize()}! Como posso ajudar?",
                        f"Olá! Tudo bem? Boa {periodo.capitalize()}!",
                        "Saudações! Como vai essa força?",
                        f"Boa {periodo.capitalize()}! Que tenhas uma {periodo.capitalize()} maravilhosa!",
                        f"Olá! Boa {periodo.capitalize()}! Como está a correr o teu dia?",
                        f"{periodo.capitalize()}! Que alegria falar contigo! Tudo bem?",
                        "Oi! Tudo ótimo por aqui. E contigo, como está a correr o dia?",
                        "Olá! Estou muito bem, cheia de energia! E tu, como vais?",
                        "Hey! Tudo tranquilo por aqui! E aí, como estão as coisas contigo?",
                    ])
                except Exception as e:
                    print(f"Erro ao processar saudação: {e}")
                    return "Olá! Como posso ajudar?"

            # Horas
            if analisar_similaridade(comando_lower, listas["horas"]):
                try:
                    hora_atual = datetime.now()
                    hora = hora_atual.strftime("%H:%M")
                    return f"Olha só, são exatamente {hora}."
                except Exception as e:
                    print(f"Erro ao obter hora: {e}")
                    return "Não consegui obter a hora atual."

            # Fome
            if analisar_similaridade(comando_lower, listas["fome"]):
                try:
                    agora = datetime.now()
                    hora = agora.hour

                    if 6 <= hora < 12:
                        refeicao = "café da manhã"
                        sugestoes = [
                            "pão quentinho",
                            "ovos mexidos",
                            "frutas frescas",
                            "aveia com banana",
                        ]
                    elif 12 <= hora < 15:
                        refeicao = "almoço"
                        sugestoes = [
                            "muamba de galinha",
                            "calulu",
                            "peixe grelhado com funje",
                            "feijão com arroz",
                        ]
                    elif 15 <= hora < 18:
                        refeicao = "lanche"
                        sugestoes = [
                            "bolo caseiro",
                            "sanduíche natural",
                            "iogurte com granola",
                            "frutas",
                        ]
                    else:
                        refeicao = "jantar"
                        sugestoes = [
                            "sopa leve",
                            "salada nutritiva",
                            "omelete",
                            "peixe cozido",
                        ]

                    sugestao = random.choice(sugestoes)
                    return random.choice([
                        f"Ah, {refeicao} é uma refeição importante! Que tal {sugestao}? Parece delicioso!",
                        f"Fome chegando? Para o {refeicao}, recomendo {sugestao}! Uma opção saudável e saborosa!",
                        f"Hora do {refeicao}! Já pensou em {sugestao}? Me parece uma ótima ideia!",
                        f"{refeicao.capitalize()} é fundamental! {sugestao.capitalize()} seria perfeito agora, não acha?"
                    ])
                except Exception as e:
                    print(f"Erro ao processar fome: {e}")
                    return "Que tal comer algo? Eu recomendaria uma refeição saudável!"

            # Piadas
            if analisar_similaridade(comando_lower, listas["humor"]):
                try:
                    self._ultimo_tipo_resposta = "piada"
                    return random.choice(listas["piada"])
                except (KeyError, IndexError) as e:
                    print(f"Erro ao buscar piada: {e}")
                    return "Não tenho piadas disponíveis agora."

            # Identidade
            if analisar_similaridade(comando_lower, listas["identidade"]):
                return random.choice([
                    f"Eu sou {self.personalidade['nome']}, a tua assistente virtual!",
                    "Sou otimista, curiosa e sempre pronta para ajudar!",
                    "Minha personalidade: mistura de eficiência e simpatia!",
                    "Traços principais: paciência digital e vontade de aprender!",
                    "Qualidade: resiliência. Defeito: às vezes muito literal!",
                    "Pontos fortes: conhecimento. Fraqueza: não entendo muito bem o sarcasmo!",
                    "Carácter: leal aos dados e empática com os usuários!",
                    "Sou como um livro aberto - sempre disponível!",
                    "Personalidade: parte técnica, parte criativa, toda útil!",
                    f"Ah, sou a {self.personalidade['nome']}! Sua assistente virtual angolana!",
                    f"Eu sou a {self.personalidade['nome']}! Uma ajudante digital com sotaque angolano!",
                    f"{self.personalidade['nome']} aqui! Sou como aquela amiga que sabe de tudo um pouco!",
                    f"Sou a {self.personalidade['nome']}! Pense em mim como sua companheira virtual!"
                ])

            # Mapeamento de comandos para respostas
            comandos_mapeados = {
                "criador": listas["criador"],
                "modelos": listas["modelos"],
                "comparacao_chatgpt": listas["comparacao_chatgpt"],
                "outras_linguas": listas["outras_linguas"],
                "paciencia": listas["paciencia"],
                "base_dados": listas["base_dados"],
                "linguas_suportadas": listas["linguas_suportadas"],
                "termos_ti": listas["termos_ti"],
                "comandos_conversa": listas["comandos_conversa"],
                "conhecimento": listas["conhecimento"],
                "comandos_disponiveis": listas["comandos_disponiveis"],
                "estado": listas["estado"],
                "ordens": listas["ordens"],
                "agradecimento": listas["agradecimento"],
                "idade": listas["idade"],
                "sad_state_user": listas["sad_state_user"],
                "elogio": listas["elogio"],
                "origem": listas["origem"],
                "surpresa": listas["surpresa"],
                "duvida": listas["duvida"],
                "cansado": listas["cansado"],
                "teamo": listas["teamo"],
                "good_state_user": listas["good_state_user"],
                "fim_do_dia": listas["fim_do_dia"],
                "existencia": listas["existencia"],
            }

            for chave, valor in comandos_mapeados.items():
                try:
                    if analisar_similaridade(comando_lower, valor[0]):
                        self._ultimo_tipo_resposta = chave
                        # Se for um elogio, usa resposta com contexto
                        if chave == "elogio" and self.historico_conversa:
                            return self._responder_elogio_com_contexto(comando, valor[1])
                        return random.choice(valor[1])
                except (KeyError, IndexError) as e:
                    print(f"Erro ao acessar comando mapeado {chave}: {e}")
                    continue

            # Data/Hora
            if analisar_similaridade(comando_lower, listas["data"]):
                return self._mostrar_data_hora()

            # Conselho
            if analisar_similaridade(comando_lower, listas["conselho"]):
                try:
                    self._ultimo_tipo_resposta = "conselho"
                    self._mostrar_mensagem_busca()
                    conselhos = self.kb.pesquisar_conselhos_qradio("", limite=3)
                    if conselhos and len(conselhos) > 0 and conselhos[0]["similaridade"] >= 80:
                        return conselhos[0]["conselho"]
                    return "Lembra-te: um dia de cada vez!"
                except Exception as e:
                    print(f"Erro ao buscar conselho: {e}")
                    return "Lembra-te: um dia de cada vez!"

            # História
            if "conte uma historia" in comando_lower or "conta uma história" in comando_lower:
                try:
                    self._ultimo_tipo_resposta = "história"
                    self._mostrar_mensagem_busca()
                    return self._contar_historia()
                except Exception as e:
                    print(f"Erro ao contar história: {e}")
                    return "Não tenho histórias para contar agora."

            return None

        except KeyError as e:
            print(f"Erro de chave em _manter_conversa: {e}")
            return None
        except Exception as e:
            print(f"Erro inesperado em _manter_conversa: {e}")
            return None

    def _responder_pergunta(self, pergunta: str) -> str:
        """Processa perguntas com foco em precisão"""
        try:
            if not pergunta or not pergunta.strip():
                return random.choice(self.sem_resposta)

            pergunta_lower = pergunta.lower()

            # Busca em conhecimentos
            try:
                conhecimentos = self.kb.pesquisar_conhecimento_qradio(pergunta_lower)
                if conhecimentos and len(conhecimentos) > 0:
                    similaridade = conhecimentos[0].get("similaridade", 0)
                    if similaridade >= 80:
                        return conhecimentos[0].get(
                            "resposta", random.choice(self.sem_resposta)
                        )
            except Exception as e:
                print(f"Erro na busca de conhecimentos: {e}")

            # Busca em factos
            try:
                factos = self.kb.pesquisar_factos_qradio(pergunta_lower, 1, 80)
                if factos and len(factos) > 0:
                    similaridade = factos[0].get("similaridade", 0)
                    if similaridade >= 80:
                        return factos[0].get("facto", random.choice(self.sem_resposta))
            except Exception as e:
                print(f"Erro na busca de factos: {e}")

            # Busca com prefixos
            try:
                prefixos_factuais_all = self.prefixos_factuais
                if isinstance(pergunta_lower, str) and prefixos_factuais_all:
                    pergunta_limpa = pergunta_lower
                    for prefix in prefixos_factuais_all:
                        try:
                            if prefix and prefix.lower() in pergunta_limpa:
                                pergunta_limpa = re.sub(
                                    rf"\b{re.escape(prefix)}\b",
                                    "",
                                    pergunta_limpa,
                                    flags=re.IGNORECASE,
                                ).strip()
                        except re.error:
                            continue

                    pergunta_limpa = re.sub(
                        r"\bjeelsia\b", "", pergunta_limpa, flags=re.IGNORECASE
                    ).strip()

                    if pergunta_limpa:
                        resultados = self.kb.pesquisar_factos_qradio(
                            pergunta_limpa, 1, 80
                        )
                        if resultados and len(resultados) > 0:
                            if resultados[0].get("similaridade", 0) >= 80:
                                return resultados[0].get(
                                    "facto", random.choice(self.sem_resposta)
                                )
            except Exception as e:
                print(f"Erro na busca com prefixos: {e}")

            return random.choice(self.sem_resposta)

        except Exception as e:
            print(f"Erro crítico em _responder_pergunta: {e}")
            return random.choice(self.sem_resposta)

    def _mostrar_mensagem_busca(self) -> None:
        """Mostra uma mensagem divertida enquanto busca informações.

        Melhoria de fluxo: a mensagem temporária é APAGADA da linha antes
        da resposta final ser impressa pelo loop principal, evitando o
        artefacto "Jeelsia : Já já te respondo...Jeelsia : <resposta>".
        """
        try:
            if self.mensagens_busca:
                mensagem = random.choice(self.mensagens_busca)
                texto = f"\rJeelsia : {mensagem}"
                print(texto, end="", flush=True)
                time.sleep(0.5)
                # Limpa a linha para que só a resposta final apareça
                print("\r" + " " * (len(texto) + 4) + "\r", end="", flush=True)
        except Exception:
            pass

    def _mostrar_data_hora(self) -> str:
        """Mostra data e hora detalhadas"""
        try:
            agora = datetime.now()
            hora_formatada = agora.strftime("%H:%M:%S")
            dia_semana = agora.strftime("%A")

            dias_pt = {
                "Monday": "Segunda-feira",
                "Tuesday": "Terça-feira",
                "Wednesday": "Quarta-feira",
                "Thursday": "Quinta-feira",
                "Friday": "Sexta-feira",
                "Saturday": "Sábado",
                "Sunday": "Domingo",
            }

            meses_pt = {
                "January": "janeiro",
                "February": "fevereiro",
                "March": "março",
                "April": "abril",
                "May": "maio",
                "June": "junho",
                "July": "julho",
                "August": "agosto",
                "September": "setembro",
                "October": "outubro",
                "November": "novembro",
                "December": "dezembro",
            }

            dia_semana_pt = dias_pt.get(dia_semana, dia_semana)
            mes_pt = meses_pt.get(agora.strftime("%B"), agora.strftime("%B"))
            data_formatada_pt = agora.strftime(f"%d de {mes_pt} de %Y")

            return f"📅 **Data e Hora:**\n• {dia_semana_pt}\n• {data_formatada_pt}\n• {hora_formatada}"

        except Exception as e:
            return f"Erro ao obter data/hora: {e}"

    def _contar_historia(self) -> str:
        """Conta uma história da base de conhecimento"""
        try:
            historias = self.kb.pesquisar_historias("", 1)
            if historias and len(historias) > 0 and historias[0]["similaridade"] >= 85:
                historia = historias[0]
                return f"{historia['titulo']}:\n\n{historia['conteudo']}\n\n- {historia.get('autor', 'Autor desconhecido')}"
            return "Parece que ainda não aprendi histórias."
        except Exception as e:
            print(f"Erro ao contar história: {e}")
            return "Não tenho histórias para contar agora."

    def iniciar(self) -> None:
        """Inicia o loop principal da aplicação"""
        try:
            # Boas-vindas personalizadas com o perfil guardado no SQLite
            nome = self.ctx_perfil.get("nome")
            assunto = self.ctx_perfil.get("ultimo_assunto")
            if nome and assunto:
                print(
                    f"Jeelsia : Olá, {nome}! Bem-vindo de volta. Da última vez "
                    f"falávamos sobre {assunto} — queres continuar ou abrir um novo assunto?"
                )
            elif nome:
                print(f"Jeelsia : Olá, {nome}! Eu sou {self.personalidade['nome']}. Sobre o que queres conversar hoje?")
            else:
                print(f"Jeelsia : Olá! Eu sou {self.personalidade['nome']}, a tua assistente virtual. Como posso ajudar?")
            print("\nDigita o teu comando (ou 'sair' para terminar):")
            self.ultima_interacao = time.time()

            while self.ativo:
                try:
                    comando = input("Tu: ")
                    if not comando:
                        continue

                    resposta = self.responder(comando)
                    if resposta:
                        print(f"Jeelsia : {resposta}")
                    self.ultima_interacao = time.time()

                except EOFError:
                    print("\nFim da entrada detectado.")
                    break
                except KeyboardInterrupt:
                    print("\nInterrupção detectada.")
                    break
                except UnicodeDecodeError:
                    print("Erro de codificação. Tenta novamente.")
                    continue
                except Exception as e:
                    print(f"Jeelsia : Ocorreu um erro ({str(e)[:50]}). Podemos continuar?")

        except Exception as e:
            print(f"Erro fatal ao iniciar: {e}")
        finally:
            self.terminar()

    def _monitorar_inatividade(self) -> None:
        """Monitora inatividade e envia mensagens"""
        while not self.evento_terminar.is_set():
            try:
                agora = time.time()
                tempo_inativo = agora - self.ultima_interacao

                if tempo_inativo > 120:
                    try:
                        tempo_legivel = humanize.naturaldelta(
                            timedelta(seconds=tempo_inativo)
                        )
                        mensagem = random.choice([
                            f"Estou aqui se precisares de algo! (Faz {tempo_legivel} que não falamos)",
                            f"Quando quiseres conversar, é só chamar! (Já passaram {tempo_legivel})",
                        ])
                        print(f"Jeelsia : {mensagem}")
                        self.ultima_interacao = agora
                    except Exception:
                        pass

                self.evento_terminar.wait(10)
            except Exception:
                continue

    def terminar(self) -> None:
        """Finaliza a aplicação"""
        try:
            self.ativo = False
            self.evento_terminar.set()
            print("Jeelsia : Foi um prazer ajudar! Até logo!")
        except Exception:
            pass
        finally:
            sys.exit(0)


if __name__ == "__main__":
    try:
        Jeelsia_IA = Jeelsia()
        Jeelsia_IA.iniciar()
    except KeyboardInterrupt:
        print("\nPrograma terminado pelo usuário.")
        sys.exit(0)
    except Exception as e:
        print(f"Erro crítico: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)