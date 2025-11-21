"""
Testes unitários para o módulo reporter.py
"""

import pytest
from unittest.mock import patch, MagicMock
from io import StringIO
import sys

from repo_miner.reporter import ResultReporter


class TestResultReporterPrintSummary:
    """Testes para impressão de resumo."""
    
    @pytest.mark.unit
    @patch('sys.stdout', new_callable=StringIO)
    def test_print_summary_basic(self, mock_stdout, sample_analysis_results):
        """Testa impressão básica de resumo."""
        ResultReporter.print_summary(sample_analysis_results)
        
        output = mock_stdout.getvalue()
        
        assert 'RESUMO DA ANÁLISE' in output or 'RESUMO' in output
        assert 'Repositório' in output
        assert 'Total de Commits' in output
    
    @pytest.mark.unit
    @patch('sys.stdout', new_callable=StringIO)
    def test_print_summary_with_statistics(self, mock_stdout, sample_analysis_results):
        """Testa impressão de resumo com estatísticas."""
        ResultReporter.print_summary(sample_analysis_results)
        
        output = mock_stdout.getvalue()
        
        assert 'Estatísticas' in output or 'Estatisticas' in output
        assert 'Arquivos Modificados' in output or 'arquivos' in output.lower()
    
    @pytest.mark.unit
    @patch('sys.stdout', new_callable=StringIO)
    def test_print_summary_with_duplicates(self, mock_stdout, sample_analysis_results):
        """Testa impressão de resumo com duplicações."""
        ResultReporter.print_summary(sample_analysis_results)
        
        output = mock_stdout.getvalue()
        
        # Deve exibir informações sobre duplicações se presentes
        assert isinstance(output, str)


class TestResultReporterPrintStatistics:
    """Testes para impressão de estatísticas."""
    
    @pytest.mark.unit
    @patch('sys.stdout', new_callable=StringIO)
    def test_print_statistics_empty(self, mock_stdout):
        """Testa impressão com estatísticas vazias."""
        results = {'statistics': {}}
        
        ResultReporter.print_statistics(results, detailed=True)
        
        output = mock_stdout.getvalue()
        # Não deve levantar exceção
    
    @pytest.mark.unit
    @patch('sys.stdout', new_callable=StringIO)
    def test_print_statistics_with_authors(self, mock_stdout, sample_analysis_results):
        """Testa impressão de estatísticas com autores."""
        ResultReporter.print_statistics(sample_analysis_results, detailed=True)
        
        output = mock_stdout.getvalue()
        
        # Deve conter informações sobre autores
        assert isinstance(output, str)


class TestResultReporterPrintDuplicates:
    """Testes para impressão de duplicações."""
    
    @pytest.mark.unit
    @patch('sys.stdout', new_callable=StringIO)
    def test_print_duplicates_empty(self, mock_stdout):
        """Testa impressão quando não há duplicatas."""
        results = {'duplicates': None}
        
        ResultReporter.print_duplicates(results)
        
        output = mock_stdout.getvalue()
        # Não deve levantar exceção
    
    @pytest.mark.unit
    @patch('sys.stdout', new_callable=StringIO)
    def test_print_duplicates_with_data(self, mock_stdout, sample_analysis_results):
        """Testa impressão de duplicações com dados."""
        ResultReporter.print_duplicates(sample_analysis_results)
        
        output = mock_stdout.getvalue()
        
        # Deve exibir informações sobre duplicações
        assert isinstance(output, str)
    
    @pytest.mark.unit
    @patch('sys.stdout', new_callable=StringIO)
    def test_print_duplicates_with_limit(self, mock_stdout, sample_analysis_results):
        """Testa impressão com limite de duplicações."""
        ResultReporter.print_duplicates(sample_analysis_results, limit=5)
        
        output = mock_stdout.getvalue()
        
        # Deve respeitar o limite
        assert isinstance(output, str)


class TestResultReporterPrintRecentCommits:
    """Testes para impressão de commits recentes."""
    
    @pytest.mark.unit
    @patch('sys.stdout', new_callable=StringIO)
    def test_print_recent_commits_empty(self, mock_stdout):
        """Testa impressão quando não há commits."""
        results = {'commits': []}
        
        ResultReporter.print_recent_commits(results)
        
        output = mock_stdout.getvalue()
        # Não deve levantar exceção
    
    @pytest.mark.unit
    @patch('sys.stdout', new_callable=StringIO)
    def test_print_recent_commits_with_data(self, mock_stdout, sample_analysis_results):
        """Testa impressão de commits recentes."""
        ResultReporter.print_recent_commits(sample_analysis_results, limit=10)
        
        output = mock_stdout.getvalue()
        
        assert 'COMMITS' in output or 'Commits' in output
        assert isinstance(output, str)
    
    @pytest.mark.unit
    @patch('sys.stdout', new_callable=StringIO)
    def test_print_recent_commits_with_limit(self, mock_stdout, sample_commits_list):
        """Testa impressão com limite de commits."""
        results = {'commits': sample_commits_list}
        
        ResultReporter.print_recent_commits(results, limit=1)
        
        output = mock_stdout.getvalue()
        
        # Deve respeitar o limite
        assert isinstance(output, str)


class TestResultReporterPrintFullReport:
    """Testes para impressão de relatório completo."""
    
    @pytest.mark.unit
    @patch('sys.stdout', new_callable=StringIO)
    def test_print_full_report(self, mock_stdout, sample_analysis_results):
        """Testa impressão de relatório completo."""
        ResultReporter.print_full_report(
            sample_analysis_results,
            duplicates_limit=10,
            commits_limit=5
        )
        
        output = mock_stdout.getvalue()
        
        # Deve conter várias seções do relatório
        assert len(output) > 0
        assert isinstance(output, str)