"""
Testes de integração para o RepoMiner.
"""

import pytest
import os
import tempfile
import shutil
from unittest.mock import patch, MagicMock

from repo_miner.analyzer import RepoAnalyzer
from repo_miner.duplicate_detector import DuplicateDetector


class TestIntegrationAnalyzerAndDetector:
    """Testes de integração entre Analyzer e Detector."""
    
    @pytest.mark.integration
    @patch('repo_miner.analyzer.RepoMiner')
    def test_analyzer_uses_detector(self, mock_miner_class):
        """Testa que o analyzer usa o detector corretamente."""
        mock_miner = MagicMock()
        mock_miner.repo_url = 'https://github.com/test/repo.git'
        mock_miner.get_commits.return_value = [
            {
                'files': [
                    {
                        'new_path': 'test.py',
                        'filename': 'test.py',
                        'source_code': 'def test():\n    return 1\n'
                    }
                ],
                'insertions': 2,
                'deletions': 0,
                'lines': 2,
                'author': 'Test'
            }
        ]
        mock_miner_class.return_value = mock_miner
        
        analyzer = RepoAnalyzer('test/repo', threshold=70, min_length=5)
        
        with patch('builtins.print'):
            results = analyzer.analyze_commits(analyze_duplicates=True)
        
        assert results['duplicates'] is not None
        assert 'total_files_analyzed' in results['duplicates']
        analyzer.cleanup()


class TestIntegrationDetectorWorkflow:
    """Testes de integração do workflow do detector."""
    
    @pytest.mark.integration
    def test_detector_full_workflow(self):
        """Testa workflow completo do detector."""
        detector = DuplicateDetector(threshold=70, min_length=3)
        
        code1 = """
def calculate_sum(a, b):
    result = a + b
    return result
"""
        
        code2 = """
def calculate_sum(a, b):
    total = a + b
    return total
"""
        
        # Analisa arquivos
        file1_data = detector.analyze_file('file1.py', code1)
        file2_data = detector.analyze_file('file2.py', code2)
        
        files_data = [file1_data, file2_data]
        
        # Encontra duplicatas
        duplicate_functions = detector.find_duplicate_functions(files_data)
        similar_blocks = detector.find_similar_code_blocks(files_data)
        
        # Verifica resultados
        assert isinstance(duplicate_functions, list)
        assert isinstance(similar_blocks, list)


class TestIntegrationExporterFormats:
    """Testes de integração para diferentes formatos de exportação."""
    
    @pytest.fixture
    def sample_results(self):
        """Resultados de exemplo para testes de exportação."""
        return {
            'repo_url': 'https://github.com/test/repo.git',
            'total_commits': 1,
            'commits': [
                {
                    'hash': 'abc123',
                    'author': 'Test Author',
                    'date': '2024-01-01',
                    'message': 'Test commit',
                    'files': []
                }
            ],
            'statistics': {
                'total_commits': 1,
                'total_files_modified': 0,
                'total_insertions': 0,
                'total_deletions': 0
            },
            'duplicates': {
                'total_files_analyzed': 0,
                'duplicate_functions': [],
                'similar_blocks': [],
                'duplicate_files': [],
                'summary': {
                    'total_duplicate_functions': 0,
                    'total_similar_blocks': 0,
                    'total_duplicate_files': 0
                }
            }
        }
    
    @pytest.mark.integration
    def test_export_all_formats(self, sample_results, temp_dir):
        """Testa exportação em todos os formatos suportados."""
        from repo_miner.exporter import ResultExporter
        
        json_path = os.path.join(temp_dir, 'test.json')
        csv_path = os.path.join(temp_dir, 'test.csv')
        md_path = os.path.join(temp_dir, 'test.md')
        
        ResultExporter.export_json(sample_results, json_path)
        ResultExporter.export_csv(sample_results, csv_path)
        ResultExporter.export_markdown(sample_results, md_path)
        
        assert os.path.exists(json_path)
        assert os.path.exists(csv_path)
        assert os.path.exists(md_path)


@pytest.mark.slow
@pytest.mark.requires_git
class TestIntegrationRealRepository:
    """Testes de integração com repositório real (marcado como lento)."""
    
    @pytest.mark.skip(reason="Requer clonagem real de repositório")
    def test_analyze_real_small_repo(self):
        """Testa análise de repositório real pequeno."""
        # Este teste pode ser habilitado para testar com repositórios reais
        # Usar repositórios muito pequenos para não demorar muito
        pass

