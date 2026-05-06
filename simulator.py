import heapq
import yaml
import sys

class FimSimulacao(Exception):
    """Exceção levantada quando o limite de aleatórios é atingido."""
    pass

# =====================================================================
# INSTRUÇÃO PARA O PYYAML IGNORAR A TAG !PARAMETERS DO JAVA
# =====================================================================
def ignora_tag_java(loader, node):
    return loader.construct_mapping(node)

yaml.SafeLoader.add_constructor('!PARAMETERS', ignora_tag_java)
# =====================================================================

class LCG:
    def __init__(self, semente=1, limite=100000):
        self.semente = semente
        self.a = 1664525
        self.c = 1013904223
        self.m = 4294967296
        self.consumidos = 0
        self.limite = limite

    def next(self):
        if self.consumidos >= self.limite:
            raise FimSimulacao()
        self.consumidos += 1
        self.semente = ((self.a * self.semente) + self.c) % self.m
        return float(self.semente) / float(self.m)

class Fila:
    def __init__(self, nome, config):
        self.nome = nome
        self.servers = config['servers']
        # Se a capacidade não for informada, é infinita
        self.capacity = config.get('capacity', 999999) 
        
        self.min_arrival = config.get('minArrival', None)
        self.max_arrival = config.get('maxArrival', None)
        
        self.min_service = config.get('minService')
        self.max_service = config.get('maxService')
        
        self.routing = config.get('routing', {})
        
        self.quant_fila = 0
        self.clientes_perdidos = 0
        limite_array = min(self.capacity + 1, 1000) 
        self.tempos_acumulados = [0.0] * limite_array
        
    def atualiza_tempo(self, delta):
        if self.quant_fila >= len(self.tempos_acumulados):
            self.tempos_acumulados.extend([0.0] * (self.quant_fila - len(self.tempos_acumulados) + 10))
        self.tempos_acumulados[self.quant_fila] += delta

class Simulador:
    def __init__(self, config_file):
        self.tempo_global = 0.0
        self.escalonador = []
        self.filas = {}
        self._carregar_config(config_file)

    def _carregar_config(self, config_file):
        with open(config_file, 'r', encoding='utf-8') as file:
            config = yaml.safe_load(file)
            
        # Configura o gerador de números aleatórios de acordo com o arquivo
        semente_inicial = config.get('seeds', [1])[0]
        limite_rnds = config.get('rndnumbersPerSeed', 100000)
        self.rng = LCG(semente=semente_inicial, limite=limite_rnds)
        
        # Mapeia a rede (converte a lista 'network' para os dicionários internos)
        mapa_rotas = {}
        if 'network' in config:
            for rota in config['network']:
                origem = rota['source']
                destino = rota['target']
                prob = rota['probability']
                if origem not in mapa_rotas:
                    mapa_rotas[origem] = {}
                mapa_rotas[origem][destino] = prob

        # Instancia as filas
        for nome, param in config['queues'].items():
            if nome in mapa_rotas:
                param['routing'] = mapa_rotas[nome]
            self.filas[nome] = Fila(nome, param)
            
        # Agenda as chegadas externas iniciais (no novo arquivo isso é só um float)
        if 'arrivals' in config:
            for nome_fila, tempo_inicial in config['arrivals'].items():
                heapq.heappush(self.escalonador, (tempo_inicial, "CHEG_EXTERNA", nome_fila))

    def rotear_cliente(self, fila_origem_nome):
        fila = self.filas[fila_origem_nome]
        if not fila.routing:
            return "OUT"
            
        rnd = self.rng.next()
        soma_prob = 0.0
        
        for destino, prob in fila.routing.items():
            soma_prob += prob
            if rnd < soma_prob:
                return destino
        return "OUT" # Se a soma das probabilidades for < 1, o restante vai pra fora

    def executar(self):
        try:
            while self.escalonador:
                tempo_evento, tipo_evento, nome_fila = heapq.heappop(self.escalonador)
                
                delta_t = tempo_evento - self.tempo_global
                for fila in self.filas.values():
                    fila.atualiza_tempo(delta_t)
                
                self.tempo_global = tempo_evento
                
                if nome_fila == "OUT":
                    continue
                    
                fila_atual = self.filas[nome_fila]
                
                if tipo_evento == "CHEG_EXTERNA":
                    self._processa_chegada_externa(fila_atual)
                elif tipo_evento == "CHEGADA":
                    self._processa_chegada(fila_atual)
                elif tipo_evento == "SAIDA":
                    self._processa_saida(fila_atual)
                    
        except FimSimulacao:
            self._imprimir_resultados()

    def _processa_chegada_externa(self, fila):
        # Agenda a PRÓXIMA chegada (agora pega min_arrival e max_arrival da própria fila)
        if fila.min_arrival is not None and fila.max_arrival is not None:
            t_min = fila.min_arrival
            t_max = fila.max_arrival
            tempo_prox = t_min + (t_max - t_min) * self.rng.next()
            heapq.heappush(self.escalonador, (self.tempo_global + tempo_prox, "CHEG_EXTERNA", fila.nome))

        self._processa_chegada(fila)

    def _processa_chegada(self, fila):
        if fila.quant_fila < fila.capacity:
            fila.quant_fila += 1
            if fila.quant_fila <= fila.servers:
                self._agenda_saida(fila)
        else:
            fila.clientes_perdidos += 1

    def _processa_saida(self, fila):
        fila.quant_fila -= 1
        
        if fila.quant_fila >= fila.servers:
            self._agenda_saida(fila)
            
        destino = self.rotear_cliente(fila.nome)
        
        if destino != "OUT":
            heapq.heappush(self.escalonador, (self.tempo_global, "CHEGADA", destino))

    def _agenda_saida(self, fila):
        tempo_atend = fila.min_service + (fila.max_service - fila.min_service) * self.rng.next()
        heapq.heappush(self.escalonador, (self.tempo_global + tempo_atend, "SAIDA", fila.nome))

    def _imprimir_resultados(self):
        print(f"\n{'='*65}")
        print(f" SIMULAÇÃO ENCERRADA ({self.rng.consumidos} Aleatórios Consumidos)")
        print(f" Tempo Global: {self.tempo_global:.4f} min")
        print(f"{'='*65}")

        for nome, fila in self.filas.items():
            print(f"\n--- {nome} ---")
            print(f"Perdas: {fila.clientes_perdidos}")
            print(f"{'Estado':<10} | {'Tempo Acumulado':<20} | {'Probabilidade':<15}")
            print("-" * 50)
            
            max_estado = fila.capacity if fila.capacity != 999999 else max((i for i, t in enumerate(fila.tempos_acumulados) if t > 0), default=0)
            
            for i in range(max_estado + 1):
                tempo_estado = fila.tempos_acumulados[i]
                prob = (tempo_estado / self.tempo_global) * 100 if self.tempo_global > 0 else 0.0
                print(f"{i:<10} | {tempo_estado:<20.4f} | {prob:<14.2f}%")
        print("\n")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        arquivo_yml = sys.argv[1]
    else:
        arquivo_yml = 'model.yml'
        
    try:
        sim = Simulador(arquivo_yml)
        sim.executar()
    except FileNotFoundError:
        print(f"Erro: Arquivo '{arquivo_yml}' não encontrado.")