# data_structures.py

from dataclasses import dataclass, field
from typing import Optional

@dataclass(order=True)
class Node:
    """
    Класс-узел для построения дерева Хаффмана.
    """
    
    # Сортировка будет идти по этому полю
    probability: float
    
    # --- НОВОЕ ПОЛЕ ---
    # Будет хранить имена 'z1z2z3...'
    combined_name: str = field(compare=False, default="")
    
    symbol: Optional[str] = field(compare=False, default=None)
    left_child: Optional['Node'] = field(compare=False, default=None)
    right_child: Optional['Node'] = field(compare=False, default=None)
    
    priority_tiebreaker: int = field(default=0)


_node_counter = 0

def create_node(probability: float, symbol: Optional[str] = None, 
                left: Optional['Node'] = None, right: Optional['Node'] = None,
                combined_name: str = "") -> Node: # <-- Добавили combined_name
    """
    Фабричная функция для создания узлов.
    """
    global _node_counter
    _node_counter += 1
    
    return Node(
        probability=probability,
        # Если имя не задано, используем имя символа
        combined_name=combined_name if combined_name else (symbol if symbol else ""),
        symbol=symbol,
        left_child=left,
        right_child=right,
        priority_tiebreaker=_node_counter
    )