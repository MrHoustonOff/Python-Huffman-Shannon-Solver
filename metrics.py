import math
from typing import Dict, Tuple

# Глобальный параметр, регулирующий округление в ВЫВОДИМЫХ строках
ROUND_DIGITS = 3

def calculate_entropy(probabilities: Dict[str, float]) -> Tuple[float, str, str, str]:
    """
    Вычисляет энтропию H(Z) = -Σ p(i) * log2(p(i)).
    
    Возвращает кортеж с "сырым" float-результатом и строками
    для "раскошного" вывода:
    (result, formula_general, formula_expanded, formula_substituted).
    """
    
    formula_general = "H(Z) = -Sum [ p(zi) * log2(p(zi)) ]"
    formula_expanded_parts = []
    formula_substituted_parts = []
    
    entropy = 0.0
    sorted_symbols = sorted(probabilities.keys(), key=lambda z: int(z[1:]))
    
    for symbol in sorted_symbols:
        prob = probabilities[symbol]
        if prob > 0: # Защита от log(0)
            entropy += prob * math.log2(prob)
            formula_expanded_parts.append(f"p({symbol})*log2(p({symbol}))")
            formula_substituted_parts.append(f"{prob:.{ROUND_DIGITS}f}*log2({prob:.{ROUND_DIGITS}f})")
        
    formula_expanded = "H(Z) = -[ " + " + ".join(formula_expanded_parts) + " ]"
    formula_substituted = "H(Z) = -[ " + " + ".join(formula_substituted_parts) + " ]"
    
    result = -entropy
    
    return result, formula_general, formula_expanded, formula_substituted

def calculate_average_length(probabilities: Dict[str, float], codes: Dict[str, str]) -> Tuple[float, str, str, str]:
    """
    Вычисляет среднюю длину L_avg = Σ p(i) * L(i).
    
    Возвращает кортеж с "сырым" float-результатом и строками
    для "раскошного" вывода:
    (result, formula_general, formula_expanded, formula_substituted).
    """
    
    formula_general = "L_avg = Sum [ p(zi) * L(zi) ]"
    formula_expanded_parts = []
    formula_substituted_parts = []
    
    avg_length = 0.0
    sorted_symbols = sorted(probabilities.keys(), key=lambda z: int(z[1:]))

    for symbol in sorted_symbols:
        prob = probabilities[symbol]
        code = codes.get(symbol)
        if code is None:
            raise ValueError(f"Ошибка: Нет сгенерированного кода для символа {symbol}")
            
        code_length = len(code)
        avg_length += prob * code_length
        
        formula_expanded_parts.append(f"p({symbol})*L({symbol})")
        formula_substituted_parts.append(f"{prob:.{ROUND_DIGITS}f}*{code_length}")

    formula_expanded = "L_avg = " + " + ".join(formula_expanded_parts)
    formula_substituted = "L_avg = " + " + ".join(formula_substituted_parts)

    return avg_length, formula_general, formula_expanded, formula_substituted

def calculate_kraft_inequality(codes: Dict[str, str]) -> Tuple[float, str, str, str]:
    """
    Вычисляет сумму ряда Крафта K = Σ 2^(-L(i)).
    
    Возвращает кортеж с "сырым" float-результатом и строками
    для "раскошного" вывода:
    (result, formula_general, formula_expanded, formula_substituted).
    """
    
    formula_general = "K = Sum [ 2^(-L(zi)) ]"
    formula_expanded_parts = []
    formula_substituted_parts = []
    
    kraft_sum = 0.0
    sorted_symbols = sorted(codes.keys(), key=lambda z: int(z[1:]))

    for symbol in sorted_symbols:
        code = codes[symbol]
        code_length = len(code)
        
        kraft_sum += 2 ** (-code_length)
        
        formula_expanded_parts.append(f"2^(-L({symbol}))")
        formula_substituted_parts.append(f"2^(-{code_length})")
        
    formula_expanded = "K = " + " + ".join(formula_expanded_parts)
    formula_substituted = "K = " + " + ".join(formula_substituted_parts)
    
    return kraft_sum, formula_general, formula_expanded, formula_substituted

def calculate_redundancy(avg_length: float, entropy: float) -> Tuple[float, str, str]:
    """
    Вычисляет избыточность r = L_avg - H.
    
    Возвращает кортеж с "сырым" float-результатом и строками
    для "раскошного" вывода:
    (result, formula_general, formula_substituted).
    """
    
    formula_general = "r = L_avg - H"
    result = avg_length - entropy
    formula_substituted = f"r = {avg_length:.{ROUND_DIGITS}f} - {entropy:.{ROUND_DIGITS}f}"
    
    return result, formula_general, formula_substituted