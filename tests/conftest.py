"""
Configurações e fixtures compartilhadas para testes.
"""

import pytest
import tempfile
import os
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List


@pytest.fixture
def temp_dir():
    """Cria um diretório temporário para testes."""
    temp_path = tempfile.mkdtemp(prefix="test_repo_miner_")
    yield temp_path
    if os.path.exists(temp_path):
        shutil.rmtree(temp_path, ignore_errors=True)

@pytest.fixture
def sample_commit_data():
    """Dados de commit de exemplo."""
    return {
        'hash': 'abc123def456',
        'author': 'Test Author',
        'author_email': 'test@example.com',
        'date': datetime(2024, 1, 1, 12, 0, 0),
        'message': 'Test commit message',
        'files': [
            {
                'filename': 'test.py',
                'new_path': 'test.py',
                'old_path': None,
                'change_type': 'ADD',
                'added_lines': 10,
                'deleted_lines': 0,
                'nloc': 8,
                'complexity': 2,
                'token_count': 50,
                'diff': '+def test():\\n    pass',
                'source_code': 'def test():\n    pass\n',
                'source_code_before': None
            }
        ],
        'insertions': 10,
        'deletions': 0,
        'lines': 8
    }
@pytest.fixture
def sample_python_code():
    """Código Python de exemplo para testes."""
    return """
def calculate_sum(a, b):
    \"\"\"Calcula a soma de dois números.\"\"\"
    result = a + b
    return result

def calculate_product(x, y):
    \"\"\"Calcula o produto de dois números.\"\"\"
    return x * y

def calculate_sum(a, b):
    \"\"\"Duplicata da função calculate_sum.\"\"\"
    result = a + b
    return result
"""

@pytest.fixture
def sample_commits_list(sample_commit_data):
    """Lista de commits de exemplo."""
    commits = [sample_commit_data.copy()]
    
    # Adiciona mais um commit
    commit2 = sample_commit_data.copy()
    commit2['hash'] = 'xyz789ghi012'
    commit2['author'] = 'Another Author'
    commit2['date'] = datetime(2024, 1, 2, 12, 0, 0)
    commits.append(commit2)
    
    return commits