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