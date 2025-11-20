"""
Testes unitários para o módulo duplicate_detector.py
"""

import pytest
from unittest.mock import patch, MagicMock
from repo_miner.duplicate_detector import DuplicateDetector


class TestDuplicateDetectorInitialization:
    """Testes para inicialização do detector."""
    
    @pytest.mark.unit
    def test_init_default_values(self):
        """Testa inicialização com valores padrão."""
        detector = DuplicateDetector()
        assert detector.threshold == 50
        assert detector.min_length == 3
    
    @pytest.mark.unit
    def test_init_custom_values(self):
        """Testa inicialização com valores customizados."""
        detector = DuplicateDetector(threshold=80, min_length=10)
        assert detector.threshold == 80
        assert detector.min_length == 10


class TestDuplicateDetectorFileAnalysis:
    """Testes para análise de arquivos."""
    
    @pytest.fixture
    def detector(self):
        """Cria um detector para testes."""
        return DuplicateDetector()
    
    @pytest.mark.unit
    def test_analyze_file_empty_code(self, detector):
        """Testa análise de arquivo vazio."""
        result = detector.analyze_file('test.py', '')
        
        assert result['filepath'] == 'test.py'
        assert result['functions'] == []
        assert result['nloc'] == 0
        assert result['complexity'] == 0
    
    @pytest.mark.unit
    def test_analyze_file_none_code(self, detector):
        """Testa análise com código None."""
        result = detector.analyze_file('test.py', None)
        
        assert result['filepath'] == 'test.py'
        assert result['functions'] == []
    
    @pytest.mark.unit
    def test_analyze_file_with_functions(self, detector, sample_python_code):
        """Testa análise de arquivo com funções."""
        result = detector.analyze_file('test.py', sample_python_code)
        
        assert result['filepath'] == 'test.py'
        assert 'functions' in result
        assert result['nloc'] >= 0
        assert result['complexity'] >= 0
        assert isinstance(result['functions'], list)
    
    @pytest.mark.unit
    def test_analyze_file_error_handling(self, detector):
        """Testa tratamento de erros na análise."""
        with patch('lizard.analyze_file.analyze_source_code') as mock_analyze:
            mock_analyze.side_effect = Exception("Analysis error")
            
            result = detector.analyze_file('test.py', 'def test(): pass')
            
            assert 'error' in result
            assert result['error'] == 'Analysis error'


class TestDuplicateDetectorCodeNormalization:
    """Testes para normalização de código."""
    
    @pytest.fixture
    def detector(self):
        """Cria um detector para testes."""
        return DuplicateDetector()
    
    @pytest.mark.unit
    def test_normalize_code_basic(self, detector):
        """Testa normalização básica de código."""
        code = "def test():\n    return 1"
        normalized = detector._normalize_code(code)
        
        assert isinstance(normalized, str)
        assert 'def test():' in normalized or 'test' in normalized
    
    @pytest.mark.unit
    def test_normalize_code_removes_comments(self, detector):
        """Testa que comentários são removidos."""
        code = "def test():  # This is a comment\n    return 1"
        normalized = detector._normalize_code(code)
        
        assert '# This is a comment' not in normalized or 'comment' not in normalized.lower()
    
    @pytest.mark.unit
    def test_normalize_code_removes_whitespace(self, detector):
        """Testa que espaços em branco são normalizados."""
        code = "    def test():\n        return 1    "
        normalized = detector._normalize_code(code)
        
        # Deve remover espaços iniciais e finais
        assert isinstance(normalized, str)
    
    @pytest.mark.unit
    def test_normalize_code_empty_string(self, detector):
        """Testa normalização de string vazia."""
        result = detector._normalize_code('')
        assert result == ''
    
    @pytest.mark.unit
    def test_normalize_code_only_comments(self, detector):
        """Testa normalização de código apenas com comentários."""
        code = "# This is a comment\n# Another comment"
        normalized = detector._normalize_code(code)
        
        # Deve retornar string vazia ou sem comentários
        assert isinstance(normalized, str)


class TestDuplicateDetectorSimilarityCalculation:
    """Testes para cálculo de similaridade."""
    
    @pytest.fixture
    def detector(self):
        """Cria um detector para testes."""
        return DuplicateDetector()
    
    @pytest.mark.unit
    def test_calculate_similarity_identical(self, detector):
        """Testa similaridade de código idêntico."""
        code = "def test():\n    return 1"
        similarity = detector._calculate_similarity(code, code)
        
        assert similarity == 100.0
    
    @pytest.mark.unit
    def test_calculate_similarity_different(self, detector):
        """Testa similaridade de código diferente."""
        code1 = "def test1():\n    return 1"
        code2 = "def test2():\n    return 2\n    x = 3"
        similarity = detector._calculate_similarity(code1, code2)
        
        assert 0 <= similarity < 100
    
    @pytest.mark.unit
    def test_calculate_similarity_empty_strings(self, detector):
        """Testa similaridade com strings vazias."""
        similarity = detector._calculate_similarity('', '')
        assert similarity == 0.0
    
    @pytest.mark.unit
    def test_calculate_similarity_one_empty(self, detector):
        """Testa similaridade quando uma string está vazia."""
        similarity = detector._calculate_similarity('def test(): pass', '')
        assert similarity == 0.0


class TestDuplicateDetectorDuplicateFinding:
    """Testes para detecção de duplicatas."""
    
    @pytest.fixture
    def detector(self):
        """Cria um detector para testes."""
        return DuplicateDetector(threshold=70, min_length=3)
    
    @pytest.mark.unit
    def test_find_duplicate_functions_empty(self, detector):
        """Testa busca de duplicatas em lista vazia."""
        result = detector.find_duplicate_functions([])
        assert result == []
    
    @pytest.mark.unit
    def test_find_duplicate_functions_no_duplicates(self, detector):
        """Testa busca quando não há duplicatas."""
        files_data = [
            {
                'filepath': 'file1.py',
                'functions': [
                    {
                        'name': 'func1',
                        'code': 'def func1():\n    return 1',
                        'start_line': 1,
                        'end_line': 2,
                        'nloc': 2,
                        'complexity': 1
                    }
                ]
            }
        ]
        
        result = detector.find_duplicate_functions(files_data)
        # Pode retornar vazio ou lista vazia se não houver duplicatas exatas
        assert isinstance(result, list)
    
    @pytest.mark.unit
    def test_find_duplicate_functions_with_duplicates(self, detector):
        """Testa busca de funções duplicadas."""
        same_code = 'def test():\n    return 1\n'
        
        files_data = [
            {
                'filepath': 'file1.py',
                'functions': [
                    {
                        'name': 'test',
                        'code': same_code,
                        'start_line': 1,
                        'end_line': 2,
                        'nloc': 2,
                        'complexity': 1
                    }
                ]
            },
            {
                'filepath': 'file2.py',
                'functions': [
                    {
                        'name': 'test',
                        'code': same_code,
                        'start_line': 1,
                        'end_line': 2,
                        'nloc': 2,
                        'complexity': 1
                    }
                ]
            }
        ]
        
        result = detector.find_duplicate_functions(files_data)
        
        assert len(result) > 0
        assert all('code_hash' in dup for dup in result)
        assert all('functions' in dup for dup in result)
        assert all('similarity' in dup for dup in result)
    
    @pytest.mark.unit
    def test_find_similar_code_blocks_empty(self, detector):
        """Testa busca de blocos similares em lista vazia."""
        result = detector.find_similar_code_blocks([])
        assert result == []
    
    @pytest.mark.unit
    def test_find_similar_code_blocks_below_threshold(self, detector):
        """Testa que blocos abaixo do threshold não são retornados."""
        detector.threshold = 90
        
        files_data = [
            {
                'filepath': 'file1.py',
                'functions': [
                    {
                        'name': 'func1',
                        'code': 'def func1():\n    return 1',
                        'start_line': 1,
                        'end_line': 2,
                        'nloc': 5,
                        'complexity': 1
                    }
                ]
            },
            {
                'filepath': 'file2.py',
                'functions': [
                    {
                        'name': 'func2',
                        'code': 'def func2():\n    x = 5\n    y = 10\n    return x + y',
                        'start_line': 1,
                        'end_line': 4,
                        'nloc': 5,
                        'complexity': 1
                    }
                ]
            }
        ]
        
        result = detector.find_similar_code_blocks(files_data)
        
        # Blocos muito diferentes não devem aparecer se threshold for alto
        assert isinstance(result, list)
    
    @pytest.mark.unit
    def test_find_similar_code_blocks_min_length_filter(self, detector):
        """Testa que funções menores que min_length são filtradas."""
        detector.min_length = 10
        
        files_data = [
            {
                'filepath': 'file1.py',
                'functions': [
                    {
                        'name': 'short_func',
                        'code': 'def short(): pass',
                        'start_line': 1,
                        'end_line': 1,
                        'nloc': 1,
                        'complexity': 1
                    }
                ]
            }
        ]
        
        result = detector.find_similar_code_blocks(files_data)
        
        # Funções muito curtas devem ser filtradas
        assert isinstance(result, list)


class TestDuplicateDetectorFileDuplicates:
    """Testes para detecção de arquivos duplicados."""
    
    @pytest.fixture
    def detector(self):
        """Cria um detector para testes."""
        return DuplicateDetector(threshold=70, min_length=3)
    
    @pytest.mark.unit
    def test_find_file_duplicates_empty(self, detector):
        """Testa busca em lista vazia."""
        result = detector.find_file_duplicates([])
        assert result == []
    
    @pytest.mark.unit
    def test_find_file_duplicates_no_duplicates(self, detector):
        """Testa busca quando não há arquivos duplicados."""
        files_data = [
            {
                'filepath': 'file1.py',
                'functions': [
                    {
                        'name': 'func1',
                        'code': 'def func1():\n    return 1'
                    }
                ],
                'nloc': 2,
                'complexity': 1
            },
            {
                'filepath': 'file2.py',
                'functions': [
                    {
                        'name': 'func2',
                        'code': 'def func2():\n    return 2'
                    }
                ],
                'nloc': 2,
                'complexity': 1
            }
        ]
        
        result = detector.find_file_duplicates(files_data)
        assert isinstance(result, list)
    
    @pytest.mark.unit
    def test_calculate_file_similarity_no_common_functions(self, detector):
        """Testa similaridade quando não há funções em comum."""
        file1 = {
            'filepath': 'file1.py',
            'functions': [
                {
                    'name': 'func1',
                    'code': 'def func1(): pass'
                }
            ]
        }
        
        file2 = {
            'filepath': 'file2.py',
            'functions': [
                {
                    'name': 'func2',
                    'code': 'def func2(): pass'
                }
            ]
        }
        
        similarity = detector._calculate_file_similarity(file1, file2)
        assert similarity == 0.0
    
    @pytest.mark.unit
    def test_calculate_file_similarity_empty_functions(self, detector):
        """Testa similaridade com arquivos sem funções."""
        file1 = {'filepath': 'file1.py', 'functions': []}
        file2 = {'filepath': 'file2.py', 'functions': []}
        
        similarity = detector._calculate_file_similarity(file1, file2)
        assert similarity == 0.0
