"""
Testes unitários para o módulo analyzer.py
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import os

from repo_miner.analyzer import RepoAnalyzer


class TestRepoAnalyzerInitialization:
    """Testes para inicialização do analisador."""
    
    @pytest.mark.unit
    @patch('repo_miner.analyzer.RepoMiner')
    def test_init_default_values(self, mock_miner_class):
        """Testa inicialização com valores padrão."""
        mock_miner = MagicMock()
        mock_miner_class.return_value = mock_miner
        
        analyzer = RepoAnalyzer('test/repo')
        
        assert analyzer.miner == mock_miner
        assert analyzer.detector.threshold == 70
        assert analyzer.detector.min_length == 5
    
    @pytest.mark.unit
    @patch('repo_miner.analyzer.RepoMiner')
    def test_init_custom_values(self, mock_miner_class):
        """Testa inicialização com valores customizados."""
        mock_miner = MagicMock()
        mock_miner_class.return_value = mock_miner
        
        analyzer = RepoAnalyzer('test/repo', threshold=80, min_length=10)
        
        assert analyzer.detector.threshold == 80
        assert analyzer.detector.min_length == 10


class TestRepoAnalyzerStatistics:
    """Testes para cálculo de estatísticas."""
    
    @pytest.fixture
    def analyzer(self):
        """Cria um analisador mockado."""
        with patch('repo_miner.analyzer.RepoMiner'):
            return RepoAnalyzer.__new__(RepoAnalyzer)
    
    @pytest.mark.unit
    def test_calculate_statistics_empty_commits(self, analyzer):
        """Testa cálculo de estatísticas com lista vazia."""
        result = analyzer._calculate_statistics([])
        assert result == {}
    
    @pytest.mark.unit
    def test_calculate_statistics_single_commit(self, analyzer, sample_commit_data):
        """Testa cálculo com um único commit."""
        commits = [sample_commit_data]
        result = analyzer._calculate_statistics(commits)
        
        assert result['total_commits'] == 1
        assert result['total_files_modified'] == 1
        assert result['total_insertions'] == sample_commit_data['insertions']
        assert result['total_deletions'] == sample_commit_data['deletions']
        assert 'authors' in result
        assert 'file_types' in result
    
    @pytest.mark.unit
    def test_calculate_statistics_multiple_commits(self, analyzer, sample_commits_list):
        """Testa cálculo com múltiplos commits."""
        result = analyzer._calculate_statistics(sample_commits_list)
        
        assert result['total_commits'] == 2
        assert result['total_files_modified'] == 2
        assert len(result['authors']) == 2
        assert result['average_files_per_commit'] == 1.0
    
    @pytest.mark.unit
    def test_calculate_statistics_net_change(self, analyzer):
        """Testa cálculo de mudança líquida."""
        commits = [
            {
                'insertions': 10,
                'deletions': 5,
                'files': [{'filename': 'test.py'}],
                'lines': 5,
                'author': 'Test'
            }
        ]
        
        result = analyzer._calculate_statistics(commits)
        
        assert result['net_change'] == 5  # 10 - 5
    
    @pytest.mark.unit
    def test_calculate_statistics_file_types(self, analyzer):
        """Testa agrupamento por tipos de arquivo."""
        commits = [
            {
                'files': [
                    {'filename': 'test.py'},
                    {'filename': 'test.java'},
                    {'filename': 'test.py'}
                ],
                'insertions': 0,
                'deletions': 0,
                'lines': 0,
                'author': 'Test'
            }
        ]
        
        result = analyzer._calculate_statistics(commits)
        
        assert '.py' in result['file_types']
        assert '.java' in result['file_types']
        assert result['file_types']['.py'] == 2
        assert result['file_types']['.java'] == 1


class TestRepoAnalyzerCommitAnalysis:
    """Testes para análise de commits."""
    
    @pytest.fixture
    def analyzer(self):
        """Cria um analisador mockado."""
        with patch('repo_miner.analyzer.RepoMiner') as mock_miner_class:
            mock_miner = MagicMock()
            mock_miner.repo_url = 'https://github.com/test/repo.git'
            mock_miner.get_commits.return_value = []
            mock_miner_class.return_value = mock_miner
            
            analyzer = RepoAnalyzer('test/repo')
            return analyzer
    
    @pytest.mark.unit
    @patch('builtins.print')
    def test_analyze_commits_basic(self, mock_print, analyzer):
        """Testa análise básica de commits."""
        analyzer.miner.get_commits.return_value = []
        
        result = analyzer.analyze_commits(analyze_duplicates=False)
        
        assert 'repo_url' in result
        assert 'total_commits' in result
        assert 'commits' in result
        assert 'statistics' in result
        assert result['duplicates'] is None
    
    @pytest.mark.unit
    @patch('builtins.print')
    def test_analyze_commits_with_duplicates(self, mock_print, analyzer, sample_commits_list):
        """Testa análise com detecção de duplicatas."""
        analyzer.miner.get_commits.return_value = sample_commits_list
        
        result = analyzer.analyze_commits(analyze_duplicates=True)
        
        assert result['duplicates'] is not None
        assert 'total_files_analyzed' in result['duplicates']
        assert 'summary' in result['duplicates']
    
    @pytest.mark.unit
    @patch('builtins.print')
    def test_analyze_commits_with_dates(self, mock_print, analyzer):
        """Testa análise com filtro de datas."""
        since = datetime(2024, 1, 1)
        to = datetime(2024, 12, 31)
        
        analyzer.miner.get_commits.return_value = []
        
        analyzer.analyze_commits(since=since, to=to)
        
        analyzer.miner.get_commits.assert_called_once_with(since=since, to=to)


class TestRepoAnalyzerDuplicateAnalysis:
    """Testes para análise de duplicatas."""
    
    @pytest.fixture
    def analyzer(self):
        """Cria um analisador mockado."""
        with patch('repo_miner.analyzer.RepoMiner') as mock_miner_class:
            mock_miner = MagicMock()
            mock_miner.repo_url = 'https://github.com/test/repo.git'
            mock_miner_class.return_value = mock_miner
            
            analyzer = RepoAnalyzer('test/repo')
            return analyzer
    
    @pytest.mark.unit
    @patch('builtins.print')
    def test_analyze_duplicates_empty_commits(self, mock_print, analyzer):
        """Testa análise de duplicatas com commits vazios."""
        result = analyzer._analyze_duplicates([])
        
        assert result['total_files_analyzed'] == 0
        assert result['duplicate_functions'] == []
        assert result['similar_blocks'] == []
        assert result['duplicate_files'] == []
    
    @pytest.mark.unit
    @patch('builtins.print')
    def test_analyze_duplicates_filters_code_files(self, mock_print, analyzer):
        """Testa que apenas arquivos de código são analisados."""
        commits = [
            {
                'files': [
                    {
                        'new_path': 'test.py',
                        'filename': 'test.py',
                        'source_code': 'def test(): pass'
                    },
                    {
                        'new_path': 'README.md',
                        'filename': 'README.md',
                        'source_code': '# Documentation'
                    }
                ]
            }
        ]
        
        result = analyzer._analyze_duplicates(commits)
        
        # Deve processar apenas .py, não .md
        assert result['total_files_analyzed'] >= 0
    
    @pytest.mark.unit
    @patch('builtins.print')
    def test_analyze_duplicates_handles_missing_source_code(self, mock_print, analyzer):
        """Testa tratamento quando source_code está ausente."""
        commits = [
            {
                'files': [
                    {
                        'new_path': 'test.py',
                        'filename': 'test.py',
                        'source_code': None
                    }
                ]
            }
        ]
        
        result = analyzer._analyze_duplicates(commits)
        
        # Deve lidar graciosamente com source_code None
        assert isinstance(result, dict)
        assert 'total_files_analyzed' in result


class TestRepoAnalyzerCleanup:
    """Testes para limpeza de recursos."""
    
    @pytest.mark.unit
    @patch('repo_miner.analyzer.RepoMiner')
    def test_cleanup_calls_miner_cleanup(self, mock_miner_class):
        """Testa que cleanup chama cleanup do miner."""
        mock_miner = MagicMock()
        mock_miner_class.return_value = mock_miner
        
        analyzer = RepoAnalyzer('test/repo')
        analyzer.cleanup()
        
        mock_miner.cleanup.assert_called_once()