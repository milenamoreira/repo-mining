"""
Testes unitários para o módulo exporter.py
"""

import pytest
import json
import csv
import os
import tempfile
from pathlib import Path
from datetime import datetime

from repo_miner.exporter import ResultExporter


class TestResultExporterJSON:
    """Testes para exportação JSON."""
    
    @pytest.mark.unit
    def test_export_json_basic(self, sample_analysis_results, temp_dir):
        """Testa exportação básica para JSON."""
        output_path = os.path.join(temp_dir, 'test.json')
        
        ResultExporter.export_json(sample_analysis_results, output_path)
        
        assert os.path.exists(output_path)
        
        with open(output_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        assert data['repo_url'] == sample_analysis_results['repo_url']
        assert data['total_commits'] == sample_analysis_results['total_commits']
    
    @pytest.mark.unit
    def test_export_json_with_datetime(self, temp_dir):
        """Testa que datetimes são serializados corretamente."""
        results = {
            'date': datetime(2024, 1, 1, 12, 0, 0),
            'commits': [
                {'date': datetime(2024, 1, 1, 12, 0, 0)}
            ]
        }
        
        output_path = os.path.join(temp_dir, 'test.json')
        
        ResultExporter.export_json(results, output_path)
        
        with open(output_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        assert 'date' in data
        assert isinstance(data['date'], str) or isinstance(data['date'], str)


class TestResultExporterCSV:
    """Testes para exportação CSV."""
    
    @pytest.mark.unit
    def test_export_csv_basic(self, sample_analysis_results, temp_dir):
        """Testa exportação básica para CSV."""
        output_path = os.path.join(temp_dir, 'test.csv')
        
        ResultExporter.export_csv(sample_analysis_results, output_path)
        
        assert os.path.exists(output_path)
        
        with open(output_path, 'r', encoding='utf-8', newline='') as f:
            reader = csv.reader(f)
            rows = list(reader)
        
        assert len(rows) > 0
        assert 'Métrica' in rows[0] or 'Metrica' in rows[0][0]
    
    @pytest.mark.unit
    def test_export_csv_with_duplicates(self, sample_analysis_results, temp_dir):
        """Testa exportação CSV com dados de duplicação."""
        # Adiciona dados de duplicação
        sample_analysis_results['duplicates'] = {
            'summary': {
                'total_duplicate_functions': 5,
                'total_similar_blocks': 10,
                'total_duplicate_files': 2
            },
            'duplicate_functions': [
                {
                    'functions': [
                        {
                            'filepath': 'file1.py',
                            'function_name': 'func1',
                            'nloc': 10,
                            'complexity': 2,
                            'code_hash': 'abc123'
                        }
                    ]
                }
            ]
        }
        
        output_path = os.path.join(temp_dir, 'test.csv')
        
        ResultExporter.export_csv(sample_analysis_results, output_path)
        
        assert os.path.exists(output_path)
        
        with open(output_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert 'Duplicações' in content or 'Duplicacoes' in content


class TestResultExporterMarkdown:
    """Testes para exportação Markdown."""
    
    @pytest.mark.unit
    def test_export_markdown_basic(self, sample_analysis_results, temp_dir):
        """Testa exportação básica para Markdown."""
        output_path = os.path.join(temp_dir, 'test.md')
        
        ResultExporter.export_markdown(sample_analysis_results, output_path)
        
        assert os.path.exists(output_path)
        
        with open(output_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert '# Relatório de Análise de Repositório' in content
        assert '## Estatísticas Gerais' in content
    
    @pytest.mark.unit
    def test_export_markdown_with_authors(self, sample_analysis_results, temp_dir):
        """Testa exportação Markdown com informações de autores."""
        output_path = os.path.join(temp_dir, 'test.md')
        
        ResultExporter.export_markdown(sample_analysis_results, output_path)
        
        with open(output_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert '### Autores' in content
        assert 'Test Author' in content or 'Another Author' in content
    
    @pytest.mark.unit
    def test_export_markdown_with_duplicates(self, sample_analysis_results, temp_dir):
        """Testa exportação Markdown com dados de duplicação."""
        sample_analysis_results['duplicates'] = {
            'total_files_analyzed': 10,
            'duplicate_functions': [
                {
                    'functions': [
                        {
                            'filepath': 'file1.py',
                            'function_name': 'func1',
                            'nloc': 10,
                            'complexity': 2
                        }
                    ]
                }
            ],
            'similar_blocks': [],
            'duplicate_files': [],
            'summary': {
                'total_duplicate_functions': 1,
                'total_similar_blocks': 0,
                'total_duplicate_files': 0
            }
        }
        
        output_path = os.path.join(temp_dir, 'test.md')
        
        ResultExporter.export_markdown(sample_analysis_results, output_path)
        
        with open(output_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert '## Análise de Código Duplicado' in content
        assert '### Funções Duplicadas' in content


class TestResultExporterSerialization:
    """Testes para serialização de objetos."""
    
    @pytest.mark.unit
    def test_make_serializable_datetime(self):
        """Testa serialização de datetime."""
        dt = datetime(2024, 1, 1, 12, 0, 0)
        result = ResultExporter._make_serializable(dt)
        
        assert isinstance(result, str)
    
    @pytest.mark.unit
    def test_make_serializable_dict(self):
        """Testa serialização de dicionário."""
        data = {
            'date': datetime(2024, 1, 1),
            'number': 42,
            'string': 'test'
        }
        
        result = ResultExporter._make_serializable(data)
        
        assert isinstance(result['date'], str)
        assert result['number'] == 42
        assert result['string'] == 'test'
    
    @pytest.mark.unit
    def test_make_serializable_list(self):
        """Testa serialização de lista."""
        data = [
            datetime(2024, 1, 1),
            42,
            'test'
        ]
        
        result = ResultExporter._make_serializable(data)
        
        assert isinstance(result[0], str)
        assert result[1] == 42
        assert result[2] == 'test'
    
    @pytest.mark.unit
    def test_make_serializable_nested(self):
        """Testa serialização de estruturas aninhadas."""
        data = {
            'commits': [
                {
                    'date': datetime(2024, 1, 1),
                    'author': 'Test'
                }
            ]
        }
        
        result = ResultExporter._make_serializable(data)
        
        assert isinstance(result['commits'][0]['date'], str)
        assert result['commits'][0]['author'] == 'Test'

