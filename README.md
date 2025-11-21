# RepoMiner

Analisador de Repositórios GitHub com Detecção de Código Duplicado

## Membros do Grupo

- Lucas Santana do Carmo Sacramento
- Milena Corrêa Moreira
- Rafaela de Fátima Silva Alexandre
- Pedro Henrique Meireles de Almeida

## Descrição

O RepoMiner é uma ferramenta que analisa repositórios do GitHub, examinando o histórico de commits e identificando código duplicado. Os resultados podem ser exibidos na linha de comando ou exportados em diferentes formatos (JSON, CSV, Markdown).

## Funcionalidades

-  Análise de histórico de commits
-  Detecção de código duplicado
-  Estatísticas detalhadas (commits, arquivos, linhas, autores)
-  Exportação de resultados em múltiplos formatos (JSON, CSV, Markdown)
-  Filtros por data
-  Configuração de threshold de similaridade
-  Interface de linha de comando (CLI) intuitiva

## Tecnologias Utilizadas

- **GitHub** - Fonte dos repositórios
- **pydriller** - Mineração do histórico de commits
- **Lizard** - Identificação de duplicação de código
- **argparse** - Interface da linha de comando
- **Python 3.10+** - Linguagem de programação

## Instalação

### Pré-requisitos

- Python 3.10 ou superior
- Git instalado

### Instalação das Dependências

```bash
pip install -r requirements.txt
```

### Dependências

- pydriller==2.1
- lizard==1.19.0
- requests==2.31.0
- python-dateutil==2.8.2
- tabulate==0.9.0
- colorama==0.4.6
- pytest==7.4.3 (para testes)
- pytest-cov==4.1.0 (para testes)
- pytest-mock==3.12.0 (para testes)
- pytest-timeout==2.2.0 (para testes)

## Uso

### Análise Básica

```bash
python -m repo_miner.cli owner/repository
```

### Análise com Filtro de Datas

```bash
python -m repo_miner.cli owner/repository --since 2024-01-01 --to 2024-12-31
```

### Análise sem Detecção de Duplicação (Mais Rápida)

```bash
python -m repo_miner.cli owner/repository --no-duplicates
```

### Exportar Resultados

#### Exportar para JSON
```bash
python -m repo_miner.cli owner/repository --export json --output results
```

#### Exportar para CSV
```bash
python -m repo_miner.cli owner/repository --export csv --output results
```

#### Exportar para Markdown
```bash
python -m repo_miner.cli owner/repository --export md --output results
```

#### Exportar para Múltiplos Formatos
```bash
python -m repo_miner.cli owner/repository --export json,csv,md --output results
```

### Configurações Avançadas

#### Ajustar Threshold de Similaridade
```bash
python -m repo_miner.cli owner/repository --threshold 80 --min-length 10
```

#### Modo Silencioso
```bash
python -m repo_miner.cli owner/repository --quiet
```

#### Não Imprimir Resultados no Console
```bash
python -m repo_miner.cli owner/repository --no-print --export json
```

## Opções da CLI

| Opção | Descrição | Padrão |
|-------|-----------|--------|
| `repository` | URL do repositório GitHub (formato: owner/repo) | Obrigatório |
| `--since` | Data inicial para análise (YYYY-MM-DD) | Opcional |
| `--to` | Data final para análise (YYYY-MM-DD) | Opcional |
| `--no-duplicates` | Não detectar código duplicado | False |
| `--threshold` | Threshold de similaridade (0-100) | 70 |
| `--min-length` | Tamanho mínimo de bloco para análise | 5 |
| `--export` | Formatos de exportação (json, csv, md) | Opcional |
| `--output` | Nome do arquivo de saída (sem extensão) | results |
| `--quiet` | Modo silencioso (apenas erros) | False |
| `--no-print` | Não imprimir resultados no console | False |
| `--duplicates-limit` | Limite de duplicações a exibir | 20 |
| `--commits-limit` | Limite de commits a exibir | 10 |

## Formatos de Exportação

### JSON
Exporta todos os dados da análise em formato JSON estruturado, incluindo commits, estatísticas e duplicações.

### CSV
Exporta as principais métricas e informações de duplicação em formato CSV, ideal para análise em planilhas.

### Markdown
Gera um relatório formatado em Markdown com tabelas e seções organizadas, perfeito para documentação.

## Estrutura do Projeto

```
repo-mining/
├── repo_miner/
│   ├── analyzer.py          # Analisador principal
│   ├── cli.py               # Interface de linha de comando
│   ├── duplicate_detector.py # Detector de código duplicado
│   ├── exporter.py          # Exportador de resultados
│   ├── miner.py             # Minerador de commits
│   └── reporter.py          # Gerador de relatórios
├── tests/                   # Testes unitários e de integração
├── main.py                  # Ponto de entrada principal
└── requirements.txt         # Dependências do projeto
```

## Testes

Execute os testes com:

```bash
pytest
```

Para executar com cobertura:

```bash
pytest --cov=repo_miner
```

## Exemplos de Saída

### Console
O RepoMiner exibe estatísticas detalhadas incluindo:
- Total de commits analisados
- Arquivos modificados
- Linhas inseridas/deletadas
- Autores e suas contribuições
- Código duplicado encontrado
- Commits recentes

### Arquivos Exportados
Os arquivos exportados contêm todas as informações da análise em formatos estruturados, facilitando análise posterior e integração com outras ferramentas.

## Contribuindo

Este é um projeto acadêmico desenvolvido pelo grupo. Para contribuições, por favor abra uma issue ou pull request.

## Licença

Este projeto é desenvolvido para fins acadêmicos.
