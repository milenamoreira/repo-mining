"""
Interface de linha de comando (CLI) para o RepoMiner.
"""

import argparse
import sys
from datetime import datetime

from repo_miner.analyzer import RepoAnalyzer
from repo_miner.reporter import ResultReporter

def parse_date(date_string: str) -> datetime:
    """Converte string de data para objeto datetime."""
    try:
        return datetime.strptime(date_string, '%Y-%m-%d')
    except ValueError:
        try:
            return datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            raise argparse.ArgumentTypeError(f"Data inválida: {date_string}. Use formato YYYY-MM-DD ou YYYY-MM-DD HH:MM:SS")
        
def argument_parser():
    parser = argparse.ArgumentParser(
        description='RepoMiner - Analisador de Repositórios GitHub com Detecção de Código Duplicado',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  
  # Análise básica de um repositório
  python -m repo_miner.cli owner/repository
  
  # Análise com filtro de datas
  python -m repo_miner.cli owner/repository --since 2024-01-01 --to 2024-12-31
  
  # Análise sem detecção de duplicação (mais rápido)
  python -m repo_miner.cli owner/repository --no-duplicates
  
  # Exportar resultados para JSON
  python -m repo_miner.cli owner/repository --export json --output results.json
  
  # Exportar para múltiplos formatos
  python -m repo_miner.cli owner/repository --export json,csv,md --output results
  
  # Ajustar threshold de similaridade
  python -m repo_miner.cli owner/repository --threshold 80 --min-length 10
        """
    )
    
    parser.add_argument(
        'repository',
        type=str,
        help='URL do repositório GitHub (formato: owner/repo ou URL completa)'
    )
    
    parser.add_argument(
        '--since',
        type=parse_date,
        help='Data inicial para análise (formato: YYYY-MM-DD ou YYYY-MM-DD HH:MM:SS)'
    )
    
    parser.add_argument(
        '--to',
        type=parse_date,
        help='Data final para análise (formato: YYYY-MM-DD ou YYYY-MM-DD HH:MM:SS)'
    )
    
    parser.add_argument(
        '--no-duplicates',
        action='store_true',
        help='Não detectar código duplicado (análise mais rápida)'
    )
    
    parser.add_argument(
        '--threshold',
        type=int,
        default=70,
        metavar='N',
        help='Threshold de similaridade para duplicação (0-100, padrão: 70)'
    )
    
    parser.add_argument(
        '--min-length',
        type=int,
        default=5,
        metavar='N',
        help='Tamanho mínimo de bloco para análise de duplicação (padrão: 5)'
    )
    
    parser.add_argument(
        '--export',
        type=str,
        choices=['json', 'csv', 'md', 'markdown'],
        nargs='+',
        help='Formatos de exportação: json, csv, md'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        default='results',
        help='Nome do arquivo ou prefixo para exportação (sem extensão, padrão: results)'
    )
    
    parser.add_argument(
        '--quiet',
        action='store_true',
        help='Modo silencioso (apenas erros)'
    )
    
    parser.add_argument(
        '--no-print',
        action='store_true',
        help='Não imprimir resultados no console'
    )
    
    parser.add_argument(
        '--duplicates-limit',
        type=int,
        default=20,
        metavar='N',
        help='Limite de duplicações a exibir (padrão: 20)'
    )
    
    parser.add_argument(
        '--commits-limit',
        type=int,
        default=10,
        metavar='N',
        help='Limite de commits a exibir (padrão: 10)'
    )


    return parser.parse_args()

def validate_args(args):
    if args.threshold < 0 or args.threshold > 100:
        print("Erro: threshold deve estar entre 0 e 100", file=sys.stderr)
        sys.exit(1)
    
    if args.min_length < 1:
        print("Erro: min-length deve ser maior que 0", file=sys.stderr)
        sys.exit(1)


def main():
    """Função principal da CLI."""

    args = argument_parser()

    validate_args(args)
    analyzer = None
    try:
        if not args.quiet:
            print(f"Iniciando análise do repositório: {args.repository}")
            print(f"Threshold de similaridade: {args.threshold}%")
            print(f"Tamanho mínimo de bloco: {args.min_length} linhas")
        
        analyzer = RepoAnalyzer(
            repo_url=args.repository,
            threshold=args.threshold,
            min_length=args.min_length
        )
        
        results = analyzer.analyze_commits(
            since=args.since,
            to=args.to,
            analyze_duplicates=not args.no_duplicates
        )

        # Exibe resultados
        if not args.no_print:
            ResultReporter.print_full_report(
                results,
                duplicates_limit=args.duplicates_limit,
                commits_limit=args.commits_limit
            )
        
    except KeyboardInterrupt:
        print("\n\nAnálise interrompida pelo usuário.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\nErro durante a análise: {str(e)}", file=sys.stderr)
        import traceback
        if not args.quiet:
            traceback.print_exc()
        sys.exit(1)
    finally:
        if analyzer:
            analyzer.cleanup()


if __name__ == '__main__':
    main()