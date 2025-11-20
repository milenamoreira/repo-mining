"""
Testes unitários para o módulo cli.py
"""

import pytest
from unittest.mock import patch
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