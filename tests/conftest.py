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