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