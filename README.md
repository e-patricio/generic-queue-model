## Instruções de Uso
Este simulador foi generalizado utilizando Orientação a Objetos e estruturas de Filas de Prioridade (Heaps) para máxima performance. As topologias são definidas através de arquivos YAML.

### Instalação das dependências
O projeto requer o módulo `pyyaml` para realizar o parser do arquivo de configuração.
`pip install pyyaml`

### Execução
1. Certifique-se de que o arquivo `model.yml` contendo a modelagem solicitada (Fila 1, 2 e 3 com suas respectivas rotas e capacidades) está na mesma pasta.
2. Execute o comando:
`python simulator.py model.yml`