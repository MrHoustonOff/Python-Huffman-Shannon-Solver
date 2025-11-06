from dataclasses import dataclass, field
from typing import Optional

@dataclass(order=True)
class Node:
    """
    Класс-узел для построения дерева кодирования (Хаффман/Шеннон).
    
    Использует `@dataclass(order=True)` для автоматической сортировки
    объектов Node в 'heapq' (очереди с приоритетом).
    
    Атрибуты:
        probability (float): Вероятность этого узла. 
                             Это *первое* поле, по нему идет сортировка.
        combined_name (str): Имя, собранное из "детей" (напр. 'z1z5z4').
        symbol (str, optional): Имя символа ('z1', 'z2'...),
                                если это "лист" дерева.
        left_child (Node, optional): Потомок для ветки '0'.
        right_child (Node, optional): Потомок для ветки '1'.
        priority_tiebreaker (int): "Разрушитель ничьих". Гарантирует,
                                   что узлы с одинаковой P можно сравнить.
    """
    
    # Поле для сортировки в heapq
    probability: float
    
    # Поля, не участвующие в сортировке
    combined_name: str = field(compare=False, default="")
    symbol: Optional[str] = field(compare=False, default=None)
    left_child: Optional['Node'] = field(compare=False, default=None)
    right_child: Optional['Node'] = field(compare=False, default=None)
    
    # Поле для "разрушения ничьих" при одинаковых probability
    priority_tiebreaker: int = field(default=0)


# Глобальный счетчик для 'priority_tiebreaker'
_node_counter = 0

def create_node(probability: float, symbol: Optional[str] = None, 
                left: Optional['Node'] = None, right: Optional['Node'] = None,
                combined_name: str = "") -> Node:
    """
    Фабричная функция для безопасного создания объектов Node.
    
    Автоматически присваивает уникальный 'priority_tiebreaker'
    для стабильной работы 'heapq'.
    
    Args:
        probability (float): Вероятность узла.
        symbol (str, optional): Имя символа (если это лист).
        left (Node, optional): Левый дочерний узел (ветка '0').
        right (Node, optional): Правый дочерний узел (ветка '1').
        combined_name (str, optional): Имя для внутреннего узла.
            Если не задано, используется 'symbol'.

    Returns:
        Node: Новый экземпляр класса Node.
    """
    global _node_counter
    _node_counter += 1
    
    # Если 'combined_name' не предоставлено,
    # по умолчанию используется 'symbol' (если он есть).
    final_name = combined_name if combined_name else (symbol if symbol else "")
    
    return Node(
        probability=probability,
        combined_name=final_name,
        symbol=symbol,
        left_child=left,
        right_child=right,
        priority_tiebreaker=_node_counter
    )