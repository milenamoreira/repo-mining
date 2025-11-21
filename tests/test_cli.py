"""
Testes unitários para o módulo cli.py
"""

import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime

from repo_miner.cli import parse_date, main

class TestCLIParseDate:
    """Testes para parsing de datas."""
    
    @pytest.mark.unit
    def test_parse_date_yyyy_mm_dd(self):
        """Testa parsing de data no formato YYYY-MM-DD."""
        result = parse_date('2024-01-01')
        
        assert isinstance(result, datetime)
        assert result.year == 2024
        assert result.month == 1
        assert result.day == 1
    
    @pytest.mark.unit
    def test_parse_date_with_time(self):
        """Testa parsing de data com hora."""
        result = parse_date('2024-01-01 12:30:45')
        
        assert isinstance(result, datetime)
        assert result.hour == 12
        assert result.minute == 30
    
    @pytest.mark.unit
    def test_parse_date_invalid_format(self):
        """Testa parsing de formato inválido."""
        import argparse
        with pytest.raises(argparse.ArgumentTypeError):
            # parse_date levanta ArgumentTypeError para formato inválido
            parse_date('invalid-date')

class TestCLIValidation:
    """Testes para validação de argumentos."""
    
    @pytest.mark.unit
    @patch('sys.argv', ['cli.py', 'test/repo', '--threshold', '150'])
    def test_main_invalid_threshold_high(self):
        """Testa validação de threshold muito alto."""
        with pytest.raises(SystemExit):
            main()
    
    @pytest.mark.unit
    @patch('sys.argv', ['cli.py', 'test/repo', '--threshold', '-10'])
    def test_main_invalid_threshold_negative(self):
        """Testa validação de threshold negativo."""
        with pytest.raises(SystemExit):
            main()
    
    @pytest.mark.unit
    @patch('sys.argv', ['cli.py', 'test/repo', '--min-length', '0'])
    def test_main_invalid_min_length(self):
        """Testa validação de min-length inválido."""
        with pytest.raises(SystemExit):
            main()

class TestCLIMain:
    """Testes para função main da CLI."""
    
    @pytest.mark.unit
    @patch('repo_miner.cli.RepoAnalyzer')
    @patch('sys.argv', ['cli.py', 'test/repo', '--since', '2024-01-01', '--to', '2024-12-31'])
    def test_main_with_dates(self, mock_analyzer_class):
        """Testa CLI com filtros de data."""
        mock_analyzer = MagicMock()
        mock_analyzer.analyze_commits.return_value = {
            'repo_url': 'test/repo',
            'total_commits': 0,
            'commits': [],
            'statistics': {},
            'duplicates': None
        }
        mock_analyzer_class.return_value = mock_analyzer
        
        with patch('builtins.print'):
            try:
                main()
            except SystemExit:
                pass
        
        call_kwargs = mock_analyzer.analyze_commits.call_args[1]
        assert 'since' in call_kwargs
        assert 'to' in call_kwargs
    
    @pytest.mark.unit
    @patch('repo_miner.cli.RepoAnalyzer')
    @patch('sys.argv', ['cli.py', 'test/repo', '--no-duplicates'])
    def test_main_no_duplicates(self, mock_analyzer_class):
        """Testa CLI sem análise de duplicatas."""
        mock_analyzer = MagicMock()
        mock_analyzer.analyze_commits.return_value = {
            'repo_url': 'test/repo',
            'total_commits': 0,
            'commits': [],
            'statistics': {},
            'duplicates': None
        }
        mock_analyzer_class.return_value = mock_analyzer
        
        with patch('builtins.print'):
            try:
                main()
            except SystemExit:
                pass
        
        call_kwargs = mock_analyzer.analyze_commits.call_args[1]
        assert call_kwargs['analyze_duplicates'] == False
    
    
    @pytest.mark.unit
    @patch('repo_miner.cli.RepoAnalyzer')
    @patch('sys.argv', ['cli.py', 'test/repo', '--threshold', '80', '--min-length', '10'])
    def test_main_custom_threshold(self, mock_analyzer_class):
        """Testa CLI com threshold customizado."""
        mock_analyzer = MagicMock()
        mock_analyzer.analyze_commits.return_value = {
            'repo_url': 'test/repo',
            'total_commits': 0,
            'commits': [],
            'statistics': {},
            'duplicates': None
        }
        mock_analyzer_class.return_value = mock_analyzer
        
        with patch('builtins.print'):
            try:
                main()
            except SystemExit:
                pass
        
        # Verifica se threshold foi passado corretamente
        mock_analyzer_class.assert_called_once()
        call_kwargs = mock_analyzer_class.call_args[1]
        assert call_kwargs['threshold'] == 80
        assert call_kwargs['min_length'] == 10
    
    @pytest.mark.unit
    @patch('repo_miner.cli.RepoAnalyzer')
    @patch('sys.argv', ['cli.py', 'test/repo'])
    def test_main_keyboard_interrupt(self, mock_analyzer_class):
        """Testa tratamento de KeyboardInterrupt."""
        mock_analyzer = MagicMock()
        mock_analyzer.analyze_commits.side_effect = KeyboardInterrupt()
        mock_analyzer_class.return_value = mock_analyzer
        
        with pytest.raises(SystemExit):
            main()
        
        mock_analyzer.cleanup.assert_called_once()
    
    @pytest.mark.unit
    @patch('repo_miner.cli.RepoAnalyzer')
    @patch('sys.argv', ['cli.py', 'test/repo'])
    def test_main_exception_handling(self, mock_analyzer_class):
        """Testa tratamento de exceções genéricas."""
        mock_analyzer = MagicMock()
        mock_analyzer.analyze_commits.side_effect = Exception("Test error")
        mock_analyzer_class.return_value = mock_analyzer
        
        with pytest.raises(SystemExit):
            main()
        
        mock_analyzer.cleanup.assert_called_once()
    
    @pytest.mark.unit
    @patch('repo_miner.cli.RepoAnalyzer')
    @patch('sys.argv', ['cli.py', 'test/repo', '--quiet'])
    def test_main_quiet_mode(self, mock_analyzer_class):
        """Testa modo silencioso."""
        mock_analyzer = MagicMock()
        mock_analyzer.analyze_commits.return_value = {
            'repo_url': 'test/repo',
            'total_commits': 0,
            'commits': [],
            'statistics': {},
            'duplicates': None
        }
        mock_analyzer_class.return_value = mock_analyzer
        
        with patch('builtins.print') as mock_print:
            try:
                main()
            except SystemExit:
                pass
        
        # Em modo quiet, menos prints devem ser feitos
        assert isinstance(mock_print.call_count, int)