"""
Módulo de exportação de resultados para diferentes formatos.
"""

import json
import csv
from typing import Dict, List
from datetime import datetime
from pathlib import Path


class ResultExporter:
    """Classe responsável por exportar resultados da análise."""
    
    @staticmethod
    def export_json(results: Dict, output_path: str):
        """
        Exporta resultados em formato JSON.
        
        Args:
            results: Dicionário com resultados da análise
            output_path: Caminho do arquivo de saída
        """
        # Serializa datetimes para strings
        serializable_results = ResultExporter._make_serializable(results)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(serializable_results, f, indent=2, ensure_ascii=False)
        
        print(f"Resultados exportados para JSON: {output_path}")
    
    @staticmethod
    def export_csv(results: Dict, output_path: str):
        """
        Exporta resultados principais em formato CSV.
        
        Args:
            results: Dicionário com resultados da análise
            output_path: Caminho do arquivo de saída
        """
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Escreve estatísticas
            writer.writerow(['Métrica', 'Valor'])
            stats = results.get('statistics', {})
            writer.writerow(['Total de Commits', stats.get('total_commits', 0)])
            writer.writerow(['Total de Arquivos Modificados', stats.get('total_files_modified', 0)])
            writer.writerow(['Total de Inserções', stats.get('total_insertions', 0)])
            writer.writerow(['Total de Deleções', stats.get('total_deletions', 0)])
            writer.writerow(['Total de Linhas', stats.get('total_lines', 0)])
            writer.writerow(['Mudança Líquida', stats.get('net_change', 0)])
            writer.writerow([])
            
            # Escreve duplicações
            if results.get('duplicates'):
                dup = results['duplicates']
                writer.writerow(['Duplicações'])
                writer.writerow(['Total de Funções Duplicadas', dup['summary']['total_duplicate_functions']])
                writer.writerow(['Total de Blocos Similares', dup['summary']['total_similar_blocks']])
                writer.writerow(['Total de Arquivos Duplicados', dup['summary']['total_duplicate_files']])
                writer.writerow([])
                
                # Escreve funções duplicadas
                writer.writerow(['Funções Duplicadas'])
                writer.writerow(['Arquivo', 'Função', 'Linhas', 'Complexidade', 'Hash'])
                for group in dup.get('duplicate_functions', []):
                    for func in group['functions']:
                        writer.writerow([
                            func['filepath'],
                            func['function_name'],
                            func['nloc'],
                            func['complexity'],
                            func['code_hash'][:8]
                        ])
        
        print(f"Resultados exportados para CSV: {output_path}")
    
    @staticmethod
    def export_markdown(results: Dict, output_path: str):
        """
        Exporta resultados em formato Markdown.
        
        Args:
            results: Dicionário com resultados da análise
            output_path: Caminho do arquivo de saída
        """
        md_content = []
        
        md_content.append("# Relatório de Análise de Repositório\n")
        md_content.append(f"**Repositório:** {results.get('repo_url', 'N/A')}\n")
        md_content.append(f"**Data da Análise:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # Estatísticas
        md_content.append("\n## Estatísticas Gerais\n")
        stats = results.get('statistics', {})
        md_content.append(f"- **Total de Commits:** {stats.get('total_commits', 0)}")
        md_content.append(f"- **Total de Arquivos Modificados:** {stats.get('total_files_modified', 0)}")
        md_content.append(f"- **Total de Inserções:** {stats.get('total_insertions', 0)}")
        md_content.append(f"- **Total de Deleções:** {stats.get('total_deletions', 0)}")
        md_content.append(f"- **Mudança Líquida:** {stats.get('net_change', 0)}")
        md_content.append(f"- **Média de Arquivos por Commit:** {stats.get('average_files_per_commit', 0):.2f}")
        
        # Autores
        if stats.get('authors'):
            md_content.append("\n### Autores\n")
            md_content.append("| Autor | Commits | Inserções | Deleções |")
            md_content.append("|-------|---------|-----------|----------|")
            for author, data in sorted(stats['authors'].items(), key=lambda x: x[1]['commits'], reverse=True):
                md_content.append(f"| {author} | {data['commits']} | {data['insertions']} | {data['deletions']} |")
        
        # Tipos de arquivo
        if stats.get('file_types'):
            md_content.append("\n### Tipos de Arquivo Modificados\n")
            md_content.append("| Extensão | Quantidade |")
            md_content.append("|----------|------------|")
            for ext, count in list(stats['file_types'].items())[:10]:
                md_content.append(f"| {ext} | {count} |")
        
        # Duplicações
        if results.get('duplicates'):
            dup = results['duplicates']
            md_content.append("\n## Análise de Código Duplicado\n")
            
            summary = dup['summary']
            md_content.append(f"- **Total de Arquivos Analisados:** {dup['total_files_analyzed']}")
            md_content.append(f"- **Funções Duplicadas Encontradas:** {summary['total_duplicate_functions']}")
            md_content.append(f"- **Blocos Similares Encontrados:** {summary['total_similar_blocks']}")
            md_content.append(f"- **Arquivos Duplicados Encontrados:** {summary['total_duplicate_files']}")
            
            # Funções duplicadas
            if dup.get('duplicate_functions'):
                md_content.append("\n### Funções Duplicadas\n")
                md_content.append("| Arquivo | Função | Linhas | Complexidade |")
                md_content.append("|---------|--------|--------|--------------|")
                for group in dup['duplicate_functions'][:20]:  # Top 20
                    for func in group['functions']:
                        md_content.append(f"| {func['filepath']} | {func['function_name']} | {func['nloc']} | {func['complexity']} |")
            
            # Blocos similares
            if dup.get('similar_blocks'):
                md_content.append("\n### Blocos de Código Similares (Top 10)\n")
                md_content.append("| Similaridade | Arquivo 1 | Função 1 | Arquivo 2 | Função 2 |")
                md_content.append("|--------------|-----------|----------|-----------|----------|")
                for block in dup['similar_blocks'][:10]:
                    md_content.append(f"| {block['similarity']:.2f}% | {block['function1']['filepath']} | {block['function1']['name']} | {block['function2']['filepath']} | {block['function2']['name']} |")
        
        # Commits recentes
        if results.get('commits'):
            md_content.append("\n## Commits Recentes (Últimos 10)\n")
            md_content.append("| Hash | Autor | Data | Mensagem |")
            md_content.append("|------|-------|------|----------|")
            for commit in results['commits'][:10]:
                hash_short = commit['hash'][:7]
                date_str = commit['date'].strftime('%Y-%m-%d') if isinstance(commit['date'], datetime) else str(commit['date'])
                msg = commit['message'].split('\n')[0][:50]
                md_content.append(f"| {hash_short} | {commit['author']} | {date_str} | {msg} |")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(md_content))
        
        print(f"Resultados exportados para Markdown: {output_path}")
    
    @staticmethod
    def _make_serializable(obj):
        """Converte objetos não-serializáveis (como datetime) para strings."""
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, dict):
            return {key: ResultExporter._make_serializable(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [ResultExporter._make_serializable(item) for item in obj]
        else:
            return obj

