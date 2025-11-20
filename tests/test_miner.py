"""
Testes unitários para o módulo miner.py
"""

import pytest
import os
import tempfile
import shutil
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from git import Repo

from repo_miner.miner import RepoMiner


class TestRepoMinerURLNormalization:
    """Testes para normalização de URLs de repositório."""
    
    @pytest.mark.unit
    def test_normalize_owner_repo_format(self):
        """Testa normalização de formato owner/repo."""
        with patch.object(RepoMiner, '_clone_repository'):
            miner = RepoMiner.__new__(RepoMiner)
            miner.repo_url = miner._normalize_repo_url('owner/repo')
            assert miner.repo_url == 'https://github.com/owner/repo.git'
    
    @pytest.mark.unit
    def test_normalize_https_url(self):
        """Testa normalização de URL HTTPS completa."""
        with patch.object(RepoMiner, '_clone_repository'):
            url = 'https://github.com/owner/repo.git'
            miner = RepoMiner.__new__(RepoMiner)
            miner.repo_url = miner._normalize_repo_url(url)
            assert miner.repo_url == url
    
    @pytest.mark.unit
    def test_normalize_git_url(self):
        """Testa normalização de URL git@."""
        with patch.object(RepoMiner, '_clone_repository'):
            url = 'git@github.com:owner/repo.git'
            miner = RepoMiner.__new__(RepoMiner)
            miner.repo_url = miner._normalize_repo_url(url)
            assert miner.repo_url == url
    
    @pytest.mark.unit
    def test_normalize_invalid_url(self):
        """Testa que URL inválida levanta exceção."""
        with patch.object(RepoMiner, '_clone_repository'):
            miner = RepoMiner.__new__(RepoMiner)
            with pytest.raises(ValueError, match="URL do repositório inválida"):
                miner._normalize_repo_url('invalid url')


class TestRepoMinerCloning:
    """Testes para clonagem de repositórios."""
    
    @pytest.mark.unit
    @pytest.mark.requires_git
    def test_clone_repository_success(self, temp_dir, monkeypatch):
        """Testa clonagem bem-sucedida de repositório."""
        mock_clone = Mock()
        monkeypatch.setattr(Repo, 'clone_from', mock_clone)
        
        with patch('builtins.print'):  # Suprime prints
            miner = RepoMiner.__new__(RepoMiner)
            miner.repo_url = 'https://github.com/test/repo.git'
            miner.clone_dir = temp_dir
            miner._clone_repository()
            
            assert mock_clone.called
            assert miner.repo_path is not None
    
    @pytest.mark.unit
    def test_clone_repository_error(self, monkeypatch):
        """Testa tratamento de erro na clonagem."""
        def mock_clone_raise(*args, **kwargs):
            raise Exception("Clone error")
        
        monkeypatch.setattr(Repo, 'clone_from', mock_clone_raise)
        
        with patch('builtins.print'):
            miner = RepoMiner.__new__(RepoMiner)
            miner.repo_url = 'https://github.com/test/repo.git'
            miner.clone_dir = tempfile.mkdtemp()
            
            with pytest.raises(Exception, match="Erro ao clonar repositório"):
                miner._clone_repository()
            
            shutil.rmtree(miner.clone_dir, ignore_errors=True)


class TestRepoMinerCommitMining:
    """Testes para mineração de commits."""
    
    @pytest.fixture
    def mock_miner(self, temp_dir, monkeypatch):
        """Cria um minerador mockado."""
        with patch.object(RepoMiner, '_clone_repository'):
            miner = RepoMiner('test/repo', clone_dir=temp_dir)
            miner.repo_path = temp_dir
            return miner
    
    @pytest.mark.unit
    def test_get_commits_empty_repo(self, mock_miner):
        """Testa mineração em repositório vazio."""
        with patch('repo_miner.miner.Repository') as mock_repo:
            mock_repo_instance = MagicMock()
            mock_repo.return_value = mock_repo_instance
            mock_repo_instance.traverse_commits.return_value = []
            
            commits = mock_miner.get_commits()
            assert commits == []
            assert isinstance(commits, list)
    
    @pytest.mark.unit
    def test_get_commits_with_data(self, mock_miner, sample_commit_data):
        """Testa mineração de commits com dados."""
        mock_commit = MagicMock()
        mock_commit.hash = sample_commit_data['hash']
        mock_commit.author.name = sample_commit_data['author']
        mock_commit.author.email = sample_commit_data['author_email']
        mock_commit.author_date = sample_commit_data['date']
        mock_commit.msg = sample_commit_data['message']
        
        mock_file = MagicMock()
        mock_file.filename = sample_commit_data['files'][0]['filename']
        mock_file.new_path = sample_commit_data['files'][0]['new_path']
        mock_file.old_path = sample_commit_data['files'][0]['old_path']
        mock_file.change_type.name = sample_commit_data['files'][0]['change_type']
        mock_file.added_lines = sample_commit_data['files'][0]['added_lines']
        mock_file.deleted_lines = sample_commit_data['files'][0]['deleted_lines']
        mock_file.nloc = sample_commit_data['files'][0]['nloc']
        mock_file.complexity = sample_commit_data['files'][0]['complexity']
        mock_file.token_count = sample_commit_data['files'][0]['token_count']
        mock_file.diff = sample_commit_data['files'][0]['diff']
        mock_file.source_code = sample_commit_data['files'][0]['source_code']
        mock_file.source_code_before = sample_commit_data['files'][0]['source_code_before']
        
        mock_commit.modified_files = [mock_file]
        
        with patch('repo_miner.miner.Repository') as mock_repo:
            mock_repo_instance = MagicMock()
            mock_repo.return_value = mock_repo_instance
            mock_repo_instance.traverse_commits.return_value = [mock_commit]
            
            commits = mock_miner.get_commits()
            
            assert len(commits) == 1
            assert commits[0]['hash'] == sample_commit_data['hash']
            assert commits[0]['author'] == sample_commit_data['author']
            assert len(commits[0]['files']) == 1
    
    @pytest.mark.unit
    def test_get_commits_with_filters(self, mock_miner):
        """Testa mineração com filtros de data."""
        since = datetime(2024, 1, 1)
        to = datetime(2024, 12, 31)
        
        with patch('repo_miner.miner.Repository') as mock_repo:
            mock_repo_instance = MagicMock()
            mock_repo.return_value = mock_repo_instance
            mock_repo_instance.traverse_commits.return_value = []
            
            mock_miner.get_commits(since=since, to=to)
            
            mock_repo.assert_called_once()
            call_kwargs = mock_repo.call_args[1]
            assert call_kwargs['since'] == since
            assert call_kwargs['to'] == to
    
    @pytest.mark.unit
    def test_get_commits_with_filepath(self, mock_miner):
        """Testa mineração com filtro de arquivo."""
        filepath = 'test.py'
        
        with patch('repo_miner.miner.Repository') as mock_repo:
            mock_repo_instance = MagicMock()
            mock_repo.return_value = mock_repo_instance
            mock_repo_instance.traverse_commits.return_value = []
            
            mock_miner.get_commits(filepath=filepath)
            
            call_kwargs = mock_repo.call_args[1]
            assert call_kwargs['filepath'] == filepath
    
    @pytest.mark.unit
    def test_get_file_history(self, mock_miner):
        """Testa obtenção de histórico de arquivo."""
        filepath = 'test.py'
        
        with patch.object(mock_miner, 'get_commits') as mock_get_commits:
            mock_get_commits.return_value = []
            
            result = mock_miner.get_file_history(filepath)
            
            mock_get_commits.assert_called_once_with(filepath=filepath)
            assert result == []
    
    @pytest.mark.unit
    def test_get_all_files(self, mock_miner, temp_dir):
        """Testa obtenção de todos os arquivos."""
        # Cria alguns arquivos de teste
        test_files = ['file1.py', 'file2.py', 'subdir/file3.py']
        for filepath in test_files:
            full_path = os.path.join(mock_miner.repo_path, filepath)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, 'w') as f:
                f.write('# Test file\n')
        
        files = mock_miner.get_all_files()
        
        assert len(files) >= len(test_files)
        assert all('file' in f or 'file' in f for f in files if 'file' in f)
        # Não deve incluir .git
        assert not any('.git' in f for f in files)


class TestRepoMinerCleanup:
    """Testes para limpeza de recursos."""
    
    @pytest.mark.unit
    def test_cleanup_success(self, temp_dir):
        """Testa limpeza bem-sucedida."""
        with patch.object(RepoMiner, '_clone_repository'):
            miner = RepoMiner.__new__(RepoMiner)
            miner.clone_dir = temp_dir
            miner.repo_path = temp_dir
            
            test_file = os.path.join(temp_dir, 'test.txt')
            with open(test_file, 'w') as f:
                f.write('test')
            
            with patch('builtins.print'):
                miner.cleanup()
            
    
    @pytest.mark.unit
    def test_cleanup_nonexistent_path(self, temp_dir):
        """Testa limpeza quando o caminho não existe."""
        with patch.object(RepoMiner, '_clone_repository'):
            miner = RepoMiner.__new__(RepoMiner)
            miner.clone_dir = temp_dir
            miner.repo_path = None
            
            with patch('builtins.print'):
                miner.cleanup()
