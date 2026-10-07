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
        
        # Memória de últimas respostas para evitar repetição
        self.ultimas_respostas = []
        self.max_historico_respostas = 5
        
        # Memória de contexto da conversa
        self.historico_conversa = []
        self.max_historico = 10
        
        # Último tópico discutido
        self.ultimo_topico = None
        
        # Reflexões para inverter pronomes (espelhamento)
        self.reflections = {
            "eu": "você",
            "meu": "seu",
            "minha": "sua",
            "me": "te",
            "estou": "está",
            "sinto": "sente",
            "quero": "quer",
            "preciso": "precisa",
            "vou": "vai",
            "posso": "pode",
            "tenho": "tem",
            "estava": "estava",
            "fui": "foi",
            "faz": "faz",
            "sei": "sabe",
            "acho": "acha",
            "penso": "pensa",
            "gosto": "gosta",
            "adoro": "adora",
            "amo": "ama",
            "queria": "queria",
            "precisava": "precisava"
        }

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

        try:
            threading.Thread(target=self._monitorar_inatividade, daemon=True).start()
        except Exception as e:
            print(f"Erro ao iniciar monitoramento: {e}")

    def _detectar_emocao(self, texto: str) -> dict:
        """Detecta emoções no texto do usuário"""
        emocao = {
            "tristeza": 0,
            "alegria": 0,
            "raiva": 0,
            "medo": 0,
            "surpresa": 0,
            "neutro": 0
        }
        
        texto_lower = texto.lower()
        
        # Palavras-chave por emoção
        palavras_tristeza = ["triste", "chateado", "mal", "deprimido", "desanimado", "frustrado", "saudade", "chorar", "sofrendo", "pior", "difícil", "cansado", "esgotado", "desiludido", "melancólico", "abatido"]
        palavras_alegria = ["feliz", "alegre", "bem", "ótimo", "excelente", "maravilhoso", "incrível", "animado", "contente", "radiante", "top", "perfeito", "bom", "alegria", "sorriso", "felicidade", "realizado"]
        palavras_raiva = ["raiva", "bravo", "irritado", "nervoso", "pistola", "furioso", "estressado", "ódio", "puto", "injusto", "revoltado", "indignado", "aborrecido", "enfurecido"]
        palavras_medo = ["medo", "preocupado", "ansioso", "inseguro", "receio", "temeroso", "apreensivo", "nervoso", "angustiado", "aflito", "assustado", "com medo"]
        palavras_surpresa = ["uau", "nossa", "caramba", "que legal", "incrível", "sensacional", "fantástico", "surpresa", "nunca", "impossível", "inacreditável", "espantado", "pasmo"]
        
        for palavra in palavras_tristeza:
            if palavra in texto_lower:
                emocao["tristeza"] += 1
        for palavra in palavras_alegria:
            if palavra in texto_lower:
                emocao["alegria"] += 1
        for palavra in palavras_raiva:
            if palavra in texto_lower:
                emocao["raiva"] += 1
        for palavra in palavras_medo:
            if palavra in texto_lower:
                emocao["medo"] += 1
        for palavra in palavras_surpresa:
            if palavra in texto_lower:
                emocao["surpresa"] += 1
        
        # Se nenhuma emoção detectada
        if sum(emocao.values()) == 0:
            emocao["neutro"] = 1
        
        # Normalizar para percentuais
        total = sum(emocao.values())
        for key in emocao:
            emocao[key] = (emocao[key] / total) * 100 if total > 0 else 0
            
        # Encontrar emoção dominante
        emocao["dominante"] = max(emocao, key=emocao.get)
        
        return emocao

    def _responder_com_empatia(self, emocao: dict, mensagem: str) -> str | None:
        """Gera resposta com base na emoção detectada"""
        dominante = emocao["dominante"]
        
        # Só responde com empatia se a emoção for forte (>40%)
        if emocao[dominante] < 40:
            return None
        
        respostas_empaticas = {
            "tristeza": [
                "Percebo que estás a sentir-te triste. Queres conversar sobre isso? Estou aqui para ouvir.",
                "Sinto muito que estejas triste. Às vezes partilhar ajuda. O que está a acontecer?",
                "Entendo que estejas a passar por um momento difícil. Podes contar comigo para desabafar.",
                "A tristeza faz parte da vida, mas não precisas de a carregar sozinho. Queres falar sobre o que te preocupa?",
                "Percebo a tua tristeza. Lembra-te que também há dias bons a caminho. Queres conversar?",
                "Ah, sinto muito. Estou aqui para te ouvir, sempre que precisares desabafar."
            ],
            "alegria": [
                "Que bom ver-te tão feliz! Conta-me o que te deixou assim tão radiante.",
                "A tua alegria é contagiante! O que está a acontecer de tão bom?",
                "Fico muito feliz por ti! Partilha essa energia positiva comigo.",
                "Uau, que energia boa! É tão bom ver alguém tão feliz. Conta-me mais!",
                "Que maravilha! Ver-te assim alegre faz o meu dia melhor também!",
                "Essa alegria é linda! O que te deixou tão radiante hoje?"
            ],
            "raiva": [
                "Entendo que estejas irritado. Respira fundo e, quando quiseres, podes contar-me o que aconteceu.",
                "Às vezes a raiva é justa, mas precisamos de processá-la. Queres desabafar?",
                "Percebo a tua frustração. Vamos respirar juntos e, se quiseres, conversar sobre isso.",
                "É normal sentir raiva às vezes. Estou aqui para ouvir e ajudar se puder.",
                "Entendo que estejas chateado. Quando te sentires pronto, podes contar-me tudo.",
                "A raiva é uma emoção válida. Queres falar sobre o que te deixou assim?"
            ],
            "medo": [
                "Entendo que possas estar com medo ou preocupado. Queres partilhar o que te deixa assim?",
                "O medo é uma emoção natural. Estou aqui para te ouvir e, juntos, podemos pensar sobre isso.",
                "Percebo a tua ansiedade. Respira comigo e, quando estiveres pronto, podes falar sobre isso.",
                "Não precisas de enfrentar os teus medos sozinho. Estou aqui para te apoiar.",
                "Sei que o medo pode ser paralisante. Queres conversar sobre o que te preocupa?",
                "É normal sentir medo. Estou aqui para te ajudar a enfrentá-lo, se quiseres."
            ],
            "surpresa": [
                "Uau, parece que algo te surpreendeu! Conta-me o que aconteceu!",
                "Percebo a tua surpresa! São esses momentos que tornam a vida interessante.",
                "Que reação incrível! Partilha essa surpresa comigo.",
                "Também fico surpresa quando algo me tira do eixo. Conta-me tudo!",
                "Adoro ver essa surpresa! O que foi que te deixou assim tão espantado?",
                "Essa surpresa é contagiante! Partilha comigo o que aconteceu!"
            ],
            "neutro": None
        }
        
        if dominante in respostas_empaticas and respostas_empaticas[dominante]:
            return random.choice(respostas_empaticas[dominante])
        return None

    def _aplicar_reflections(self, texto: str) -> str:
        """Aplica reflexões para inverter pronomes"""
        palavras = texto.split()
        for i, palavra in enumerate(palavras):
            palavra_limpa = palavra.lower().strip('.,!?')
            if palavra_limpa in self.reflections:
                # Preservar capitalização
                if palavra[0].isupper():
                    palavras[i] = self.reflections[palavra_limpa].capitalize()
                else:
                    palavras[i] = self.reflections[palavra_limpa]
        return ' '.join(palavras)

    def _obter_resposta_unica(self, resposta: str) -> str:
        """Garante que a resposta não seja repetida recentemente"""
        if resposta in self.ultimas_respostas:
            # Tenta variação ou resposta alternativa
            variacoes = [
                f"{resposta} (já disse isso antes, mas reforço novamente!)",
                f"Como já tinha mencionado antes: {resposta}",
                f"Relembrando o que já falamos: {resposta}",
                f"Como te disse anteriormente: {resposta}"
            ]
            return random.choice(variacoes)
        else:
            self.ultimas_respostas.append(resposta)
            if len(self.ultimas_respostas) > self.max_historico_respostas:
                self.ultimas_respostas.pop(0)
            return resposta

    def _extrair_topico(self, mensagem: str) -> str | None:
        """Extrai tópico principal da mensagem"""
        # Remove palavras comuns e mantém substantivos principais
        palavras = mensagem.lower().split()
        stopwords = ["o", "a", "os", "as", "um", "uma", "uns", "umas", "de", "da", "do", "das", "dos", "para", "com", "por", "em", "na", "no", "que", "se", "é", "são", "está", "estão"]
        topicos = [p for p in palavras if p not in stopwords and len(p) > 3]
        return topicos[0] if topicos else None

    def _manter_contexto(self, mensagem: str) -> bool:
        """Mantém contexto da conversa"""
        # Se não há histórico, adiciona
        if not self.historico_conversa:
            self.historico_conversa.append(mensagem)
            return False
        
        # Verifica se a mensagem se relaciona com o último tópico
        topico_atual = self._extrair_topico(mensagem)
        ultimo_topico = self._extrair_topico(self.historico_conversa[-1]) if self.historico_conversa else None
        
        if topico_atual and ultimo_topico and topico_atual == ultimo_topico:
            return True
        
        # Adiciona ao histórico
        self.historico_conversa.append(mensagem)
        if len(self.historico_conversa) > self.max_historico:
            self.historico_conversa.pop(0)
        return False

    def _responder_palavras_curtas(self, mensagem: str) -> str | None:
        """Responde a palavras curtas como 'sim', 'não', etc."""
        mensagem_limpa = mensagem.lower().strip()
        
        # Verifica respostas curtas baseadas no contexto
        if mensagem_limpa in ["sim", "s", "si", "yeah", "yep", "claro", "exato", "exatamente", "certeza", "ok", "okei", "blz", "beleza"]:
            if self.historico_conversa:
                return random.choice([
                    "Fico feliz que concordes! O que mais gostarias de abordar?",
                    "Excelente! Vamos continuar nessa linha então.",
                    "Perfeito! É sempre bom quando estamos na mesma página.",
                    "Ótimo! Queres aprofundar algum ponto específico?",
                    "Que bom que concordas! O que mais podemos explorar?",
                    "Boa! Estamos na mesma sintonia. Continua."
                ])
            return random.choice([
                "Sim! O que mais posso fazer por ti?",
                "Perfeito! Estou aqui para o que precisares.",
                "Ótimo! Diz-me como posso ajudar."
            ])
        
        elif mensagem_limpa in ["não", "n", "nao", "nah", "nem", "nops", "nunca", "negativo"]:
            if self.historico_conversa:
                return random.choice([
                    "Entendo. Se mudares de ideia, estou aqui.",
                    "Tudo bem, respeito a tua decisão. Queres falar sobre outra coisa?",
                    "Sem problemas! O importante é te sentires confortável.",
                    "Certo. Se quiseres explorar outros tópicos, é só dizer.",
                    "Compreendo. Estou disponível para o que precisares.",
                    "Respeito a tua posição. Queres conversar sobre algo diferente?"
                ])
            return random.choice([
                "Entendo. Se precisares de algo, estou disponível.",
                "Tudo bem. O que gostarias de fazer então?",
                "Certo. Estou aqui quando precisares."
            ])
        
        elif mensagem_limpa in ["talvez", "quem sabe", "pode ser", "vamos ver", "não sei", "dúvida"]:
            return random.choice([
                "Compreendo. Às vezes é bom refletir um pouco antes de decidir.",
                "Tudo bem, podemos deixar em aberto. O que mais te interessa?",
                "Entendo a indecisão. Queres pensar mais sobre isso?",
                "Às vezes a dúvida nos ajuda a tomar melhores decisões.",
                "Sem pressa! O importante é chegares a uma decisão que te agrade."
            ])
        
        return None

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
            assunto = self._extrair_topico(ultima_msg) if ultima_msg else "conversa"
            
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
        """Método principal para processar e responder mensagens"""
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

            # Detecta emoção
            emocao = self._detectar_emocao(mensagem)
            
            # Resposta empática se houver emoção forte
            resposta_empatica = self._responder_com_empatia(emocao, mensagem)
            if resposta_empatica:
                return self._obter_resposta_unica(resposta_empatica)

            # Mantém contexto
            self._manter_contexto(mensagem)

            # Verifica comandos especiais de saída
            if mensagem.lower() in ["sair", "fechar", "terminar", "exit", "quit"]:
                self.ativo = False
                self.evento_terminar.set()
                return "Foi um prazer ajudar! Até logo!"

            # Processa o comando
            resposta = self._processar_comando(mensagem)
            
            # Aplica reflexões se for uma pergunta sobre o usuário
            if resposta and ("você" in resposta or "tu" in resposta or "te" in resposta):
                resposta = self._aplicar_reflections(resposta)
            
            # Evita repetição
            if resposta:
                resposta = self._obter_resposta_unica(resposta)
            
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
                return resposta_pergunta

            # ULTIMO FALLBACK: Sugere comandos similares
            return self._fallback_resposta(comando)

        except Exception as e:
            print(f"Erro inesperado em _processar_comando: {e}")
            return self._fallback_resposta(comando)

    def _manter_conversa(self, comando: str) -> str | None:
        """Gerencia conversas e comandos específicos"""
        try:
            comando_lower = comando.lower()
            listas = self.padroes_conversa

            # Saudações
            if self._analise_similaidade(comando_lower, listas["saudacao"]):
                try:
                    agora = datetime.now()
                    if agora.hour < 12:
                        periodo = "manhã"
                    elif agora.hour < 18:
                        periodo = "tarde"
                    else:
                        periodo = "noite"

                    return random.choice([
                        f"Boa {periodo.capitalize()}! Como posso ajudar?",
                        f"Olá! Tudo bem? Boa {periodo.capitalize()}!",
                        "Saudações! Como vai essa força?",
                        f"Boa {periodo.capitalize()}! Que tenhas uma {periodo.capitalize()} maravilhosa!",
                        f"Boa {periodo.capitalize()} Continuação de um boa! {periodo.capitalize()}",
                        f"Olá! {periodo.capitalize()}!. Como vai você?",
                        f"{periodo.capitalize()}! Que alegria falar com você! Tudo bem?",
                        f"Oi! {periodo.capitalize()}!. Como está se sentindo hoje?",
                        f"{periodo.capitalize()}! Espero que esteja tudo bem por aí. Como está?",
                        f"Olá! {periodo.capitalize()}!. Tudo tranquilo com você?",
                        "Oi! Tudo ótimo por aqui",
                        "Obrigada por perguntar! E com você, como está a vida?",
                        "Olá! Estou muito bem, cheia de energia! E você, como vai?",
                        "Hey! Tudo tranquilo por aqui! E aí, como estão as coisas contigo?",
                        "Olá! Estou bem, obrigada! E você, tudo em ordem?"
                    ])
                except Exception as e:
                    print(f"Erro ao processar saudação: {e}")
                    return "Olá! Como posso ajudar?"

            # Horas
            if self._analise_similaidade(comando_lower, listas["horas"]):
                try:
                    hora_atual = datetime.now()
                    hora = hora_atual.strftime("%H:%M")
                    return f"Olha só, são exatamente {hora}."
                except Exception as e:
                    print(f"Erro ao obter hora: {e}")
                    return "Não consegui obter a hora atual."

            # Fome
            if self._analise_similaidade(comando_lower, listas["fome"]):
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
            if self._analise_similaidade(comando_lower, listas["humor"]):
                try:
                    return random.choice(listas["piada"])
                except (KeyError, IndexError) as e:
                    print(f"Erro ao buscar piada: {e}")
                    return "Não tenho piadas disponíveis agora."

            # Identidade
            if self._analise_similaidade(comando_lower, listas["identidade"]):
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
                    if self._analise_similaidade(comando_lower, valor[0]):
                        # Se for um elogio, usa resposta com contexto
                        if chave == "elogio" and self.historico_conversa:
                            return self._responder_elogio_com_contexto(comando, valor[1])
                        return random.choice(valor[1])
                except (KeyError, IndexError) as e:
                    print(f"Erro ao acessar comando mapeado {chave}: {e}")
                    continue

            # Data/Hora
            if self._analise_similaidade(comando_lower, listas["data"]):
                return self._mostrar_data_hora()

            # Conselho
            if self._analise_similaidade(comando_lower, listas["conselho"]):
                try:
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
        """Mostra uma mensagem divertida enquanto busca informações"""
        try:
            if self.mensagens_busca:
                mensagem = random.choice(self.mensagens_busca)
                print(f"\rJeelsia : {mensagem}", end="", flush=True)
                time.sleep(0.5)
        except Exception:
            pass

    def _analise_similaidade(
        self, frase: str, lista: list, threshold=90
    ) -> bool | None:
        """Analisa similaridade entre frase e itens da lista"""
        try:
            if not lista:
                return False

            frase = self._normalizar_texto(frase)
            for linha in lista:
                try:
                    if fuzz.QRatio(f"{frase}", f"{linha}") >= threshold:
                        return True
                    if fuzz.token_sort_ratio(f"{frase}", f"{linha}") >= 90:
                        return True
                except Exception:
                    continue
            return False
        except Exception:
            return False

    def _normalizar_texto(self, texto: str) -> str:
        """Normaliza texto removendo caracteres especiais"""
        try:
            texto = re.sub(r"[^\w\s]", "", texto)
            texto = re.sub(r"\s{2,}", " ", texto)
            return texto.lower().strip()
        except Exception:
            return texto.lower().strip() if texto else ""

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