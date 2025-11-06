# algorithms.py

import heapq  # Наша "очередь с приоритетом"
from data_structures import Node, create_node # Импортируем наш Узел
from typing import Dict, List, Optional

def build_huffman_tree(probabilities: Dict[str, float]) -> Optional[Node]:
    """
    Строит дерево Хаффмана на основе словаря вероятностей.
    [cite_start][cite: 493, 494, 495, 496, 497, 498]
    Возвращает корень (Node) построенного дерева.
    """
    
    # 1. Шаг "Упорядочение" (для нас это "Инициализация")
    # Создаем список "листьев" (наши z1, z2...).
    # heapq - это "мин-куча" (min-heap), она будет автоматически
    # держать узел с НАИМЕНЬШЕЙ вероятностью в начале.
    
    priority_queue: List[Node] = []
    
    if not probabilities:
        return None
        
    for symbol, prob in probabilities.items():
        # Создаем "лист"
        leaf_node = create_node(probability=prob, symbol=symbol)
        # Кладем его в "кучу" (очередь)
        heapq.heappush(priority_queue, leaf_node)
        
    
    # [cite_start]2. Шаг "Редукция" (пока в очереди не останется 1 узел) [cite: 496]
    while len(priority_queue) > 1:
        
        # [cite_start]3. Достаем ДВА узла с наименьшими вероятностями [cite: 495]
        left_node = heapq.heappop(priority_queue)
        right_node = heapq.heappop(priority_queue)
        
        # 4. Создаем "составной знак" (родителя)
        combined_prob = left_node.probability + right_node.probability
        
        parent_node = create_node(
            probability=combined_prob,
            left=left_node,   # 0
            right=right_node  # 1
        )
        
        # 5. Кладем родителя ОБРАТНО в очередь
        heapq.heappush(priority_queue, parent_node)
        
    # 6. В конце в "куче" остается один элемент - корень дерева
    return heapq.heappop(priority_queue) if priority_queue else None

def generate_codes_from_tree(tree_root: Optional[Node]) -> Dict[str, str]:
    """
    Рекурсивно обходит дерево и генерирует коды для каждого символа.
    [cite_start][cite: 497, 498]
    Возвращает словарь вида {'z1': '01', 'z2': '110', ...}
    """
    
    codes_dictionary: Dict[str, str] = {}

    def traverse_tree(current_node: Optional[Node], current_code: str):
        """ Вложенная рекурсивная функция """
        
        if current_node is None:
            return

        # 1. Проверяем, это "лист" (конечный символ)?
        if current_node.symbol is not None:
            # Да! Записываем его код.
            # (Если код пустой - значит, в дереве всего 1 узел, даем ему '0')
            codes_dictionary[current_node.symbol] = current_code if current_code else "0"
            return

        # [cite_start]2. Это "составной узел". Идем налево, добавляя '0' [cite: 497]
        traverse_tree(current_node.left_child, current_code + "0")
        
        # [cite_start]3. Идем направо, добавляя '1' [cite: 497]
        traverse_tree(current_node.right_child, current_code + "1")

    # Начинаем обход с корня и пустого кода
    traverse_tree(tree_root, "")
    
    return codes_dictionary