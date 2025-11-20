"""
Módulo de detecção de código duplicado usando Lizard.
"""

import lizard
from typing import List, Dict, Set, Tuple
from collections import defaultdict
import hashlib
import difflib


class DuplicateDetector:
    """Classe responsável por detectar código duplicado usando Lizard."""
    
    def __init__(self, threshold: int = 50, min_length: int = 3):
        """
        Inicializa o detector de duplicação.
        
        Args:
            threshold: Porcentagem mínima de similaridade para considerar duplicação (0-100)
            min_length: Número mínimo de linhas para considerar um bloco
        """
        self.threshold = threshold
        self.min_length = min_length
    
    def analyze_file(self, filepath: str, source_code: str) -> Dict:
        """
        Analisa um arquivo e retorna métricas de complexidade.
        
        Args:
            filepath: Caminho do arquivo
            source_code: Código-fonte do arquivo
            
        Returns:
            Dicionário com métricas do arquivo
        """
        if not source_code:
            return {
                'filepath': filepath,
                'functions': [],
                'nloc': 0,
                'complexity': 0,
                'token_count': 0
            }
        
        try:
            analysis = lizard.analyze_file.analyze_source_code(filepath, source_code)
            
            functions = []
            for func in analysis.function_list:
                functions.append({
                    'name': func.name,
                    'start_line': func.start_line,
                    'end_line': func.end_line,
                    'nloc': func.nloc,
                    'complexity': func.cyclomatic_complexity,
                    'parameters': func.parameters,
                    'token_count': func.token_count,
                    'code': '\n'.join(source_code.split('\n')[func.start_line-1:func.end_line])
                })
            
            return {
                'filepath': filepath,
                'functions': functions,
                'nloc': analysis.nloc,
                'complexity': sum(f['complexity'] for f in functions),
                'token_count': analysis.token_count,
                'average_nloc': analysis.average_nloc if analysis.function_list else 0,
                # 'average_ccn': analysis.average_ccn if analysis.function_list else 0
            }
        except Exception as e:
            print(f"Erro ao analisar arquivo {filepath}: {str(e)}")
            return {
                'filepath': filepath,
                'functions': [],
                'nloc': 0,
                'complexity': 0,
                'token_count': 0,
                'error': str(e)
            }
    
    def find_duplicate_functions(self, files_data: List[Dict]) -> List[Dict]:
        """
        Encontra funções duplicadas entre arquivos.
        
        Args:
            files_data: Lista de dicionários com dados dos arquivos
            
        Returns:
            Lista de grupos de funções duplicadas
        """
        function_groups = defaultdict(list)
        
        # Agrupa funções por hash do código normalizado
        for file_data in files_data:
            for func in file_data.get('functions', []):
                normalized_code = self._normalize_code(func['code'])
                code_hash = hashlib.md5(normalized_code.encode()).hexdigest()
                
                function_groups[code_hash].append({
                    'filepath': file_data['filepath'],
                    'function_name': func['name'],
                    'start_line': func['start_line'],
                    'end_line': func['end_line'],
                    'nloc': func['nloc'],
                    'complexity': func['complexity'],
                    'code': func['code'],
                    'code_hash': code_hash
                })
        
        # Filtra apenas grupos com duplicatas (2 ou mais)
        duplicates = []
        for code_hash, functions in function_groups.items():
            if len(functions) >= 2:
                duplicates.append({
                    'code_hash': code_hash,
                    'count': len(functions),
                    'functions': functions,
                    'similarity': 100.0  # Mesmo hash = 100% similar
                })
        
        return duplicates
    
    def find_similar_code_blocks(self, files_data: List[Dict]) -> List[Dict]:
        """
        Encontra blocos de código similares usando algoritmo de similaridade.
        
        Args:
            files_data: Lista de dicionários com dados dos arquivos
            
        Returns:
            Lista de pares de blocos similares
        """
        similar_blocks = []
        all_functions = []
        
        # Coleta todas as funções
        for file_data in files_data:
            for func in file_data.get('functions', []):
                if func['nloc'] >= self.min_length:
                    all_functions.append({
                        'filepath': file_data['filepath'],
                        'function_name': func['name'],
                        'start_line': func['start_line'],
                        'end_line': func['end_line'],
                        'nloc': func['nloc'],
                        'complexity': func['complexity'],
                        'code': func['code'],
                        'normalized_code': self._normalize_code(func['code'])
                    })
        
        # Compara cada par de funções
        for i, func1 in enumerate(all_functions):
            for func2 in all_functions[i+1:]:
                similarity = self._calculate_similarity(
                    func1['normalized_code'],
                    func2['normalized_code']
                )
                
                if similarity >= self.threshold:
                    similar_blocks.append({
                        'similarity': similarity,
                        'function1': {
                            'filepath': func1['filepath'],
                            'name': func1['function_name'],
                            'start_line': func1['start_line'],
                            'end_line': func1['end_line'],
                            'nloc': func1['nloc'],
                            'code': func1['code']
                        },
                        'function2': {
                            'filepath': func2['filepath'],
                            'name': func2['function_name'],
                            'start_line': func2['start_line'],
                            'end_line': func2['end_line'],
                            'nloc': func2['nloc'],
                            'code': func2['code']
                        }
                    })
        
        # Ordena por similaridade decrescente
        similar_blocks.sort(key=lambda x: x['similarity'], reverse=True)
        
        return similar_blocks
    
    def _normalize_code(self, code: str) -> str:
        """
        Normaliza o código removendo espaços extras e normalizando indentação.
        
        Args:
            code: Código-fonte original
            
        Returns:
            Código normalizado
        """
        lines = code.split('\n')
        normalized_lines = []
        
        for line in lines:
            # Remove espaços em branco no início e fim
            stripped = line.strip()
            # Remove comentários
            if stripped and not stripped.startswith('#'):
                # Remove comentários inline
                if '#' in stripped:
                    stripped = stripped[:stripped.index('#')].strip()
                if stripped:
                    normalized_lines.append(stripped)
        
        return '\n'.join(normalized_lines)
    
    def _calculate_similarity(self, code1: str, code2: str) -> float:
        """
        Calcula similaridade entre dois blocos de código usando SequenceMatcher.
        
        Args:
            code1: Primeiro bloco de código
            code2: Segundo bloco de código
            
        Returns:
            Porcentagem de similaridade (0-100)
        """
        if not code1 or not code2:
            return 0.0
        
        # Usa SequenceMatcher para calcular similaridade
        matcher = difflib.SequenceMatcher(None, code1, code2)
        similarity = matcher.ratio() * 100
        
        return round(similarity, 2)
    
    def find_file_duplicates(self, files_data: List[Dict]) -> List[Dict]:
        """
        Encontra arquivos inteiros duplicados ou muito similares.
        
        Args:
            files_data: Lista de dicionários com dados dos arquivos
            
        Returns:
            Lista de pares de arquivos duplicados
        """
        file_duplicates = []
        
        for i, file1 in enumerate(files_data):
            for file2 in files_data[i+1:]:
                similarity = self._calculate_file_similarity(file1, file2)
                
                if similarity >= self.threshold:
                    file_duplicates.append({
                        'similarity': similarity,
                        'file1': {
                            'filepath': file1['filepath'],
                            'nloc': file1['nloc'],
                            'complexity': file1['complexity']
                        },
                        'file2': {
                            'filepath': file2['filepath'],
                            'nloc': file2['nloc'],
                            'complexity': file2['complexity']
                        }
                    })
        
        return file_duplicates
    
    def _calculate_file_similarity(self, file1: Dict, file2: Dict) -> float:
        """Calcula similaridade entre dois arquivos."""
        # Compara funções de ambos os arquivos
        funcs1 = {f['name']: f['code'] for f in file1.get('functions', [])}
        funcs2 = {f['name']: f['code'] for f in file2.get('functions', [])}
        
        if not funcs1 or not funcs2:
            return 0.0
        
        # Compara funções com mesmos nomes
        similarities = []
        for name in set(funcs1.keys()) & set(funcs2.keys()):
            norm1 = self._normalize_code(funcs1[name])
            norm2 = self._normalize_code(funcs2[name])
            similarities.append(self._calculate_similarity(norm1, norm2))
        
        if similarities:
            return sum(similarities) / len(similarities)
        
        return 0.0
