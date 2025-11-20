"""
Módulo principal que combina mineração e detecção de duplicação.
"""

from typing import List, Dict, Optional
from datetime import datetime
from .miner import RepoMiner
from .duplicate_detector import DuplicateDetector
import os


class RepoAnalyzer:
    """Classe principal que orquestra análise de repositórios."""
    
    def __init__(self, repo_url: str, threshold: int = 70, min_length: int = 5):
        """
        Inicializa o analisador de repositório.
        
        Args:
            repo_url: URL do repositório GitHub
            threshold: Threshold de similaridade para duplicação (0-100)
            min_length: Tamanho mínimo de bloco para análise
        """
        self.miner = RepoMiner(repo_url)
        self.detector = DuplicateDetector(threshold=threshold, min_length=min_length)
        self.analysis_results = {}
    
    def analyze_commits(self,
                       since: Optional[datetime] = None,
                       to: Optional[datetime] = None,
                       analyze_duplicates: bool = True) -> Dict:
        """
        Analisa commits do repositório e detecta duplicações.
        
        Args:
            since: Data inicial para análise
            to: Data final para análise
            analyze_duplicates: Se True, analisa duplicações de código
            
        Returns:
            Dicionário com resultados da análise
        """
        print("Minerando commits...")
        commits = self.miner.get_commits(since=since, to=to)
        print(f"Encontrados {len(commits)} commits")
        
        results = {
            'repo_url': self.miner.repo_url,
            'total_commits': len(commits),
            'commits': commits,
            'statistics': self._calculate_statistics(commits),
            'duplicates': None
        }
        
        if analyze_duplicates:
            print("Analisando código duplicado...")
            duplicates = self._analyze_duplicates(commits)
            results['duplicates'] = duplicates
        
        self.analysis_results = results
        return results
    
    def _calculate_statistics(self, commits: List[Dict]) -> Dict:
        """Calcula estatísticas dos commits."""
        if not commits:
            return {}
        
        total_files = sum(len(c['files']) for c in commits)
        total_insertions = sum(c['insertions'] for c in commits)
        total_deletions = sum(c['deletions'] for c in commits)
        total_lines = sum(c['lines'] for c in commits)
        
        authors = {}
        for commit in commits:
            author = commit['author']
            if author not in authors:
                authors[author] = {'commits': 0, 'insertions': 0, 'deletions': 0}
            authors[author]['commits'] += 1
            authors[author]['insertions'] += commit['insertions']
            authors[author]['deletions'] += commit['deletions']
        
        file_types = {}
        for commit in commits:
            for file_info in commit['files']:
                filename = file_info['filename']
                ext = os.path.splitext(filename)[1] or 'sem extensão'
                if ext not in file_types:
                    file_types[ext] = 0
                file_types[ext] += 1
        
        return {
            'total_commits': len(commits),
            'total_files_modified': total_files,
            'total_insertions': total_insertions,
            'total_deletions': total_deletions,
            'total_lines': total_lines,
            'net_change': total_insertions - total_deletions,
            'average_files_per_commit': total_files / len(commits) if commits else 0,
            'authors': authors,
            'file_types': dict(sorted(file_types.items(), key=lambda x: x[1], reverse=True))
        }
    
    def _analyze_duplicates(self, commits: List[Dict]) -> Dict:
        """Analisa duplicações de código nos commits."""
        print("Coletando arquivos modificados...")
        
        # Coleta todos os arquivos únicos modificados
        files_analyzed = {}
        file_contents = {}
        
        for commit in commits:
            for file_info in commit['files']:
                filepath = file_info.get('new_path') or file_info.get('filename')
                
                if not filepath:
                    continue
                
                # Analisa apenas arquivos de código (extensões comuns)
                code_extensions = {'.py', '.java', '.js', '.ts', '.cpp', '.c', '.cs', '.rb', '.go', '.php', '.swift', '.kt'}
                ext = os.path.splitext(filepath)[1].lower()
                
                if ext in code_extensions:
                    source_code = file_info.get('source_code') or ''
                    if source_code and filepath not in files_analyzed:
                        file_contents[filepath] = source_code
        
        print(f"Analisando {len(file_contents)} arquivos de código...")
        
        # Analisa cada arquivo
        files_data = []
        for filepath, source_code in file_contents.items():
            file_data = self.detector.analyze_file(filepath, source_code)
            files_data.append(file_data)
        
        # Detecta duplicações
        print("Detectando funções duplicadas...")
        duplicate_functions = self.detector.find_duplicate_functions(files_data)
        
        print("Detectando blocos similares...")
        similar_blocks = self.detector.find_similar_code_blocks(files_data)
        
        print("Detectando arquivos duplicados...")
        duplicate_files = self.detector.find_file_duplicates(files_data)
        
        return {
            'total_files_analyzed': len(files_data),
            'duplicate_functions': duplicate_functions,
            'similar_blocks': similar_blocks,
            'duplicate_files': duplicate_files,
            'summary': {
                'total_duplicate_functions': len(duplicate_functions),
                'total_similar_blocks': len(similar_blocks),
                'total_duplicate_files': len(duplicate_files)
            }
        }
    
    def cleanup(self):
        """Limpa recursos utilizados."""
        self.miner.cleanup()
