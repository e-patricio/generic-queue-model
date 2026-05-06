# Simulador Genérico de Rede de Filas
Este projeto é a consolidação e generalização de um simulador de eventos discretos. O objetivo desta versão final é suportar **qualquer topologia de rede de filas** através da leitura dinâmica de arquivos de configuração, eliminando a necessidade de alterar o código-fonte para testar novos cenários.

## Sobre o Projeto
O simulador foi implementado utilizando a abordagem de **Avanço do Tempo Orientado a Eventos**. Para garantir o máximo de performance mesmo em redes complexas e com alta carga, o escalonador global foi construído utilizando estruturas de **Filas de Prioridade (Heaps)**, o que reduz drasticamente a complexidade computacional da ordenação de eventos.

* **Motor Estocástico:** O controle de aleatoriedade é feito por um Gerador Congruente Linear (LCG) encapsulado, encerrando a simulação de forma cirúrgica no exato momento em que o 100.000º número pseudoaleatório é consumido.
* **Arquitetura Dinâmica:** O modelo foi desenvolvido com Orientação a Objetos (POO). As filas e rotas não são "chumbadas" no código; elas são instanciadas dinamicamente a partir de um arquivo `YAML`.
* **Compatibilidade:** O *parser* de configuração foi desenhado para ser 100% compatível com o formato de arquivos utilizado no simulador em Java disponibilizado no módulo 3 da disciplina, permitindo validações e comparações diretas ("A/B testing").

## Topologia Validada nesta Etapa
Para fins de validação do motor genérico, o arquivo `model.yml` anexo representa a seguinte rede de filas:

* **Fila 1 (G/G/1):** Fila de entrada principal com capacidade ilimitada. Recebe clientes do exterior (intervalo de chegada: 2 a 4 min). Possui 1 servidor com tempo de atendimento muito rápido (1 a 2 min).
  * *Roteamento:* Envia 80% dos clientes para a Fila 2 e 20% para a Fila 3.
* **Fila 2 (G/G/2/5):** Fila intermediária com capacidade máxima para 5 clientes. Possui 2 servidores mais lentos (atendimento entre 4 e 6 min), gerando perdas severas.
  * *Roteamento:* Possui *feedback loop* retornando 30% dos clientes para a Fila 1; envia 50% para a Fila 3 e 20% deixam o sistema.
* **Fila 3 (G/G/2/10):** Fila de saída com capacidade para 10 clientes. Possui 2 servidores com tempo de atendimento altamente variável (5 a 15 min).
  * *Roteamento:* Envia 70% dos clientes de volta para a Fila 2 (outro *feedback loop*) e 30% deixam o sistema.

## Como Executar
O simulador foi desenvolvido em Python 3.x e necessita apenas de uma biblioteca externa para a leitura dos arquivos de modelagem.

### Pré-requisitos
* Python 3.x instalado na máquina.
* Instalação do módulo de *parser* YAML. Para instalar, execute no terminal:
  ```bash
  pip install pyyaml

### Execução
1. Certifique-se de que o arquivo `model.yml` contendo a modelagem solicitada (Fila 1, 2 e 3 com suas respectivas rotas e capacidades) está na mesma pasta.
2. Execute o comando:
`python simulator.py model.yml`