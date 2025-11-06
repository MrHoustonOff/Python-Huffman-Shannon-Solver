# data_structures.py

from dataclasses import dataclass, field
from typing import Optional


@dataclass(order=True)
class Node:
    """
    Класс-узел для построения дерева Хаффмана.

    @dataclass(order=True) автоматически реализует методы сравнения
    (__lt__, __le__, __gt__, __ge__) на основе полей в том порядке,
    в котором они объявлены.
    
    Мы помещаем 'probability' первым, чтобы очередь с приоритетом (heapq)
    сортировала узлы именно по вероятности.
    """
    
    # Сортировка будет идти по этому полю
    probability: float
    
    # 'symbol' и 'priority_tiebreaker' не участвуют в основном сравнении, 
    # но 'field(compare=False)' для 'symbol' нужно, 
    # т.к. строки и float сравнивать нельзя.
    symbol: Optional[str] = field(compare=False, default=None)
    
    # 'left' и 'right' не должны участвовать в сравнении
    left_child: Optional['Node'] = field(compare=False, default=None)
    right_child: Optional['Node'] = field(compare=False, default=None)

    # NEW: "Разрушитель ничьих" (Tie-breaker)
    # Если два узла имеют ОДИНАКОВУЮ вероятность (например, 0.1 и 0.1),
    # heapq может попытаться сравнить следующие поля. 
    # Добавим простой счетчик, чтобы у него всегда было что сравнить.
    # Мы присвоим его при создании узла.
    priority_tiebreaker: int = field(default=0)


# Статический счетчик для "разрушителя ничьих"
# Будем увеличивать его каждый раз, когда создаем узел.
_node_counter = 0


def create_node(probability: float, symbol: Optional[str] = None, 
                left: Optional['Node'] = None, right: Optional['Node'] = None) -> Node:
    """
    Фабричная функция для создания узлов.
    Гарантирует, что у каждого узла будет уникальный 'priority_tiebreaker'.
    """
    global _node_counter
    _node_counter += 1
    
    return Node(
        probability=probability,
        symbol=symbol,
        left_child=left,
        right_child=right,
        priority_tiebreaker=_node_counter
    )