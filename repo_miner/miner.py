"""
Módulo de mineração de repositórios usando PyDriller.
"""

from pydriller import Repository
from typing import List, Dict, Optional
from datetime import datetime
import os
import tempfile
import shutil
from git import Repo


class RepoMiner:
    """Classe responsável por minerar informações de repositórios GitHub."""
    
    def __init__(self, repo_url: str, clone_dir: Optional[str] = None):
        """
        Inicializa o minerador de repositório.
        
        Args:
            repo_url: URL do repositório GitHub (formato: owner/repo ou URL completa)
            clone_dir: Diretório temporário para clonar o repositório (opcional)
        """
        self.repo_url = self._normalize_repo_url(repo_url)
        self.clone_dir = clone_dir or tempfile.mkdtemp(prefix="repo_miner_")
        self.repo_path = None
        self._clone_repository()
    
    def _normalize_repo_url(self, url: str) -> str:
        """Normaliza a URL do repositório para formato completo."""
        if url.startswith('http://') or url.startswith('https://'):
            return url
        elif url.startswith('git@'):
            return url
        elif '/' in url and ' ' not in url:
            # Formato owner/repo
            return f"https://github.com/{url}.git"
        else:
            raise ValueError(f"URL do repositório inválida: {url}")
    
    def _clone_repository(self):
        """Clona o repositório para um diretório temporário."""
        try:
            repo_name = self.repo_url.split('/')[-1].replace('.git', '')
            self.repo_path = os.path.join(self.clone_dir, repo_name)
            
            if os.path.exists(self.repo_path):
                shutil.rmtree(self.repo_path)
            
            print(f"Clonando repositório {self.repo_url}...")
            Repo.clone_from(self.repo_url, self.repo_path)
            print(f"Repositório clonado com sucesso em {self.repo_path}")
        except Exception as e:
            raise Exception(f"Erro ao clonar repositório: {str(e)}")
    
    def get_commits(self, 
                   since: Optional[datetime] = None,
                   to: Optional[datetime] = None,
                   filepath: Optional[str] = None,
                   only_modifications: bool = False) -> List[Dict]:
        """
        Obtém lista de commits do repositório.
        
        Args:
            since: Data inicial para filtrar commits
            to: Data final para filtrar commits
            filepath: Caminho do arquivo para filtrar commits
            only_modifications: Se True, retorna apenas commits com modificações
            
        Returns:
            Lista de dicionários com informações dos commits
        """
        commits_data = []
        
        try:
            repo_kwargs = {
                'path_to_repo': self.repo_path
            }
            if since:
                repo_kwargs['since'] = since
            if to:
                repo_kwargs['to'] = to
            if filepath:
                repo_kwargs['filepath'] = filepath
            
            repo = Repository(**repo_kwargs)
            
            for commit in repo.traverse_commits():
                commit_info = {
                    'hash': commit.hash,
                    'author': commit.author.name,
                    'author_email': commit.author.email,
                    'date': commit.author_date,
                    'message': commit.msg,
                    'files': [],
                    'insertions': 0,
                    'deletions': 0,
                    'lines': 0,
                    'dmm_unit_size': commit.dmm_unit_size if hasattr(commit, 'dmm_unit_size') else None,
                    'dmm_unit_complexity': commit.dmm_unit_complexity if hasattr(commit, 'dmm_unit_complexity') else None,
                }
                
                for modified_file in commit.modified_files:
                    file_info = {
                        'filename': modified_file.filename,
                        'new_path': modified_file.new_path,
                        'old_path': modified_file.old_path,
                        'change_type': modified_file.change_type.name if modified_file.change_type else None,
                        'added_lines': modified_file.added_lines,
                        'deleted_lines': modified_file.deleted_lines,
                        'nloc': modified_file.nloc,
                        'complexity': modified_file.complexity,
                        'token_count': modified_file.token_count,
                        'diff': modified_file.diff,
                        'source_code': modified_file.source_code,
                        'source_code_before': modified_file.source_code_before,
                    }
                    
                    commit_info['files'].append(file_info)
                    commit_info['insertions'] += modified_file.added_lines
                    commit_info['deletions'] += modified_file.deleted_lines
                    commit_info['lines'] += modified_file.nloc or 0
                
                commits_data.append(commit_info)
            
        except Exception as e:
            raise Exception(f"Erro ao minerar commits: {str(e)}")
        
        return commits_data
    
    def get_file_history(self, filepath: str) -> List[Dict]:
        """
        Obtém histórico de modificações de um arquivo específico.
        
        Args:
            filepath: Caminho do arquivo no repositório
            
        Returns:
            Lista de commits que modificaram o arquivo
        """
        return self.get_commits(filepath=filepath)
    
    def get_all_files(self) -> List[str]:
        """
        Retorna lista de todos os arquivos do repositório.
        
        Returns:
            Lista de caminhos de arquivos
        """
        files = []
        for root, dirs, filenames in os.walk(self.repo_path):
            # Ignorar diretórios .git
            dirs[:] = [d for d in dirs if d != '.git']
            for filename in filenames:
                filepath = os.path.join(root, filename)
                rel_path = os.path.relpath(filepath, self.repo_path)
                files.append(rel_path.replace('\\', '/'))
        return files
    
    def cleanup(self):
        """Remove o diretório temporário do repositório clonado."""
        if self.repo_path and os.path.exists(self.repo_path):
            try:
                shutil.rmtree(self.clone_dir)
                print(f"Diretório temporário removido: {self.clone_dir}")
            except Exception as e:
                print(f"Erro ao remover diretório temporário: {str(e)}")