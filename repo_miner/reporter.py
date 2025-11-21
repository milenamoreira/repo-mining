"""
Módulo de relatório e exibição de resultados no console.
"""

from typing import Dict, List
from tabulate import tabulate
from colorama import init, Fore, Style
from datetime import datetime

# Inicializa colorama para Windows
init(autoreset=True)


class ResultReporter:
    """Classe responsável por exibir resultados formatados no console."""
    
    @staticmethod
    def print_summary(results: Dict):
        """Imprime resumo dos resultados da análise."""
        print("\n" + "="*80)
        print(f"{Fore.CYAN}{Style.BRIGHT}{'RESUMO DA ANÁLISE':^80}{Style.RESET_ALL}")
        print("="*80)
        
        print(f"\n{Fore.YELLOW}Repositório:{Style.RESET_ALL} {results.get('repo_url', 'N/A')}")
        print(f"{Fore.YELLOW}Total de Commits:{Style.RESET_ALL} {results.get('total_commits', 0)}")
        
        stats = results.get('statistics', {})
        if stats:
            print(f"\n{Fore.GREEN}{Style.BRIGHT}Estatísticas:{Style.RESET_ALL}")
            print(f"  • Arquivos Modificados: {stats.get('total_files_modified', 0)}")
            print(f"  • Inserções: {Fore.GREEN}{stats.get('total_insertions', 0)}{Style.RESET_ALL}")
            print(f"  • Deleções: {Fore.RED}{stats.get('total_deletions', 0)}{Style.RESET_ALL}")
            print(f"  • Mudança Líquida: {stats.get('net_change', 0)}")
            print(f"  • Média de Arquivos por Commit: {stats.get('average_files_per_commit', 0):.2f}")
        
        # Duplicações
        if results.get('duplicates'):
            dup = results['duplicates']
            summary = dup['summary']
            print(f"\n{Fore.MAGENTA}{Style.BRIGHT}Duplicações Detectadas:{Style.RESET_ALL}")
            print(f"  • Arquivos Analisados: {dup['total_files_analyzed']}")
            print(f"  • Funções Duplicadas: {Fore.RED}{summary['total_duplicate_functions']}{Style.RESET_ALL}")
            print(f"  • Blocos Similares: {Fore.YELLOW}{summary['total_similar_blocks']}{Style.RESET_ALL}")
            print(f"  • Arquivos Duplicados: {Fore.RED}{summary['total_duplicate_files']}{Style.RESET_ALL}")
    
    @staticmethod
    def print_statistics(results: Dict, detailed: bool = False):
        """Imprime estatísticas detalhadas."""
        stats = results.get('statistics', {})
        
        if not stats:
            print(f"{Fore.RED}Nenhuma estatística disponível.{Style.RESET_ALL}")
            return
        
        print(f"\n{Fore.CYAN}{Style.BRIGHT}{'='*80}")
        print(f"{'ESTATÍSTICAS DETALHADAS':^80}")
        print(f"{'='*80}{Style.RESET_ALL}\n")
        
        # Tabela de autores
        if stats.get('authors'):
            authors_data = []
            for author, data in sorted(stats['authors'].items(), key=lambda x: x[1]['commits'], reverse=True):
                authors_data.append([
                    author,
                    data['commits'],
                    data['insertions'],
                    data['deletions']
                ])
            
            print(f"{Fore.YELLOW}Top Contribuidores:{Style.RESET_ALL}")
            print(tabulate(
                authors_data,
                headers=['Autor', 'Commits', 'Inserções', 'Deleções'],
                tablefmt='grid',
                numalign='right'
            ))
        
        # Tipos de arquivo
        if stats.get('file_types'):
            file_types_data = []
            for ext, count in sorted(stats['file_types'].items(), key=lambda x: x[1], reverse=True)[:15]:
                file_types_data.append([ext or 'sem extensão', count])
            
            print(f"\n{Fore.YELLOW}Tipos de Arquivo Modificados (Top 15):{Style.RESET_ALL}")
            print(tabulate(
                file_types_data,
                headers=['Extensão', 'Quantidade'],
                tablefmt='grid',
                numalign='right'
            ))
    
    @staticmethod
    def print_duplicates(results: Dict, limit: int = 20):
        """Imprime informações sobre duplicações."""
        if not results.get('duplicates'):
            print(f"\n{Fore.GREEN}Nenhuma duplicação detectada.{Style.RESET_ALL}")
            return
        
        dup = results['duplicates']
        
        print(f"\n{Fore.CYAN}{Style.BRIGHT}{'='*80}")
        print(f"{'ANÁLISE DE CÓDIGO DUPLICADO':^80}")
        print(f"{'='*80}{Style.RESET_ALL}\n")
        
        # Funções duplicadas
        if dup.get('duplicate_functions'):
            print(f"{Fore.RED}{Style.BRIGHT}Funções Duplicadas (Exatamente Iguais):{Style.RESET_ALL}")
            dup_func_data = []
            
            for group in dup['duplicate_functions'][:limit]:
                for func in group['functions']:
                    dup_func_data.append([
                        func['filepath'][:50],
                        func['function_name'],
                        func['nloc'],
                        func['complexity'],
                        group['count']
                    ])
            
            print(tabulate(
                dup_func_data,
                headers=['Arquivo', 'Função', 'Linhas', 'Complexidade', 'Cópias'],
                tablefmt='grid',
                maxcolwidths=[50, 30, 10, 12, 8]
            ))
        
        # Blocos similares
        if dup.get('similar_blocks'):
            print(f"\n{Fore.YELLOW}{Style.BRIGHT}Blocos de Código Similares (Top {limit}):{Style.RESET_ALL}")
            similar_data = []
            
            for block in dup['similar_blocks'][:limit]:
                similar_data.append([
                    f"{block['similarity']:.2f}%",
                    block['function1']['filepath'][:35],
                    block['function1']['name'],
                    block['function2']['filepath'][:35],
                    block['function2']['name'],
                    block['function1']['nloc']
                ])
            
            print(tabulate(
                similar_data,
                headers=['Similaridade', 'Arquivo 1', 'Função 1', 'Arquivo 2', 'Função 2', 'Linhas'],
                tablefmt='grid',
                maxcolwidths=[12, 35, 25, 35, 25, 8]
            ))
        
        # Arquivos duplicados
        if dup.get('duplicate_files'):
            print(f"\n{Fore.MAGENTA}{Style.BRIGHT}Arquivos Duplicados:{Style.RESET_ALL}")
            file_dup_data = []
            
            for pair in dup['duplicate_files'][:limit]:
                file_dup_data.append([
                    f"{pair['similarity']:.2f}%",
                    pair['file1']['filepath'][:40],
                    pair['file2']['filepath'][:40]
                ])
            
            print(tabulate(
                file_dup_data,
                headers=['Similaridade', 'Arquivo 1', 'Arquivo 2'],
                tablefmt='grid',
                maxcolwidths=[12, 40, 40]
            ))
    
    @staticmethod
    def print_recent_commits(results: Dict, limit: int = 10):
        """Imprime commits recentes."""
        commits = results.get('commits', [])
        
        if not commits:
            return
        
        print(f"\n{Fore.CYAN}{Style.BRIGHT}{'='*80}")
        print(f"{'COMMITS RECENTES':^80}")
        print(f"{'='*80}{Style.RESET_ALL}\n")
        
        commit_data = []
        for commit in commits[:limit]:
            hash_short = commit['hash'][:7]
            date_str = commit['date'].strftime('%Y-%m-%d') if isinstance(commit['date'], datetime) else str(commit['date'])[:10]
            author = commit['author']
            msg = commit['message'].split('\n')[0][:60]
            files = len(commit['files'])
            
            commit_data.append([
                hash_short,
                date_str,
                author[:20],
                f"+{commit['insertions']}/-{commit['deletions']}",
                files,
                msg
            ])
        
        print(tabulate(
            commit_data,
            headers=['Hash', 'Data', 'Autor', 'Mudanças', 'Arquivos', 'Mensagem'],
            tablefmt='grid',
            maxcolwidths=[8, 12, 20, 12, 8, 60]
        ))
    
    @staticmethod
    def print_full_report(results: Dict, duplicates_limit: int = 20, commits_limit: int = 10):
        """Imprime relatório completo."""
        ResultReporter.print_summary(results)
        ResultReporter.print_statistics(results, detailed=True)
        ResultReporter.print_duplicates(results, limit=duplicates_limit)
        ResultReporter.print_recent_commits(results, limit=commits_limit)
        print("\n" + "="*80 + "\n")
