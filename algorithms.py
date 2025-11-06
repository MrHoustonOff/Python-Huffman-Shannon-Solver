# algorithms.py

import heapq
from data_structures import Node, create_node
from typing import Dict, List, Optional, Tuple
from rich import print as rprint

# --- АЛГОРИТМ ХАФФМАНА ---
def build_huffman_tree(probabilities: Dict[str, float]) -> Optional[Node]:
    """
    Строит дерево Хаффмана.
    Правило: узел с БОЛЬШЕЙ вероятностью идет в левую ветку ('0').
    """
    
    priority_queue: List[Node] = []
    if not probabilities:
        return None
        
    for symbol, prob in probabilities.items():
        # Создаем "лист", имя узла = имя символа
        leaf_node = create_node(probability=prob, symbol=symbol, combined_name=symbol)
        heapq.heappush(priority_queue, leaf_node)
        
    # Шаг "Редукция"
    while len(priority_queue) > 1:
        
        # 1. Достаем ДВА узла с наименьшими вероятностями
        node_1 = heapq.heappop(priority_queue)
        node_2 = heapq.heappop(priority_queue)
        
        # 2. Применяем правило "Больше P -> 0"
        if node_1.probability >= node_2.probability:
            # Если P равны, то node_1 (созданный раньше) > node_2
            # Но для Хаффмана это не так важно, как для правила из методички.
            # Главное - консистентность.
            higher_prob_node = node_1
            lower_prob_node = node_2
        else:
            higher_prob_node = node_2
            lower_prob_node = node_1
            
        # 3. СОЗДАЕМ ИМЕНА (Порядок важен для Рис. 3)
        # Имя левой ветки (0) + Имя правой ветки (1)
        left_name = higher_prob_node.combined_name
        right_name = lower_prob_node.combined_name
            
        combined_prob = higher_prob_node.probability + lower_prob_node.probability
        
        parent_node = create_node(
            probability=combined_prob,
            left=higher_prob_node,  # <-- Ветка '0' (больше P)
            right=lower_prob_node, # <-- Ветка '1' (меньше P)
            combined_name=f"{left_name}{right_name}" # Собираем имя
        )
        
        heapq.heappush(priority_queue, parent_node)
        
    return heapq.heappop(priority_queue) if priority_queue else None

# --- АЛГОРИТМ ШЕННОНА-ФАНО ---
def _find_shannon_fano_split_index(sorted_probs: List[Tuple[str, float]]) -> int:
    """
    Вспомогательная функция. Находит "идеальную" точку разделения списка.
    """
    total_prob = sum(item[1] for item in sorted_probs)
    min_diff = float('inf')
    best_split_index = 0
    current_left_sum = 0.0
    for i in range(len(sorted_probs) - 1):
        current_left_sum += sorted_probs[i][1]
        diff = abs(current_left_sum - (total_prob - current_left_sum))
        if diff < min_diff:
            min_diff = diff
            best_split_index = i + 1
        else:
            break
    if best_split_index == 0:
        return 1
    return best_split_index

def build_shannon_fano_tree(probabilities: Dict[str, float]) -> Optional[Node]:
    """
    Строит дерево Шеннона-Фано рекурсивно.
    (Алгоритм "сверху-вниз")
    """
    
    # 1. Сортируем символы по УБЫВАНИЮ вероятности
    sorted_probs: List[Tuple[str, float]] = sorted(
        probabilities.items(),
        key=lambda item: item[1],
        reverse=True
    )
    
    # 2. Запускаем рекурсивный процесс построения
    def _build_recursive(current_probs_list: List[Tuple[str, float]]) -> Optional[Node]:
        
        # Базовый случай рекурсии: в группе 1 символ -> это ЛИСТ
        if len(current_probs_list) == 1:
            symbol, prob = current_probs_list[0]
            return create_node(probability=prob, symbol=symbol, combined_name=symbol)
            
        if not current_probs_list:
            return None

        # 3. Находим точку разделения
        split_index = _find_shannon_fano_split_index(current_probs_list)
        
        # 4. Делим на две группы (Группа 0 - больше P)
        group_zero = current_probs_list[:split_index]
        group_one = current_probs_list[split_index:]
        
        # 5. Рекурсивный вызов для "детей"
        left_child = _build_recursive(group_zero)
        right_child = _build_recursive(group_one)
        
        # 6. Создаем ВНУТРЕННИЙ узел
        combined_prob = (left_child.probability if left_child else 0) + (right_child.probability if right_child else 0)
        
        # Добавляем имена
        left_name = left_child.combined_name if left_child else ""
        right_name = right_child.combined_name if right_child else ""
        
        return create_node(
            probability=combined_prob, 
            left=left_child, 
            right=right_child, 
            combined_name=f"{left_name}{right_name}"
        )

    # Начинаем рекурсию со всем списком
    return _build_recursive(sorted_probs)

# --- ОБЩАЯ ФУНКЦИЯ ГЕНЕРАЦИИ КОДОВ ---
def generate_codes_from_tree(tree_root: Optional[Node]) -> Dict[str, str]:
    """
    Рекурсивно обходит ЛЮБОЕ дерево (Node) и генерирует коды
    для каждого символа.
    """
    codes_dictionary: Dict[str, str] = {}
    def traverse_tree(current_node: Optional[Node], current_code: str):
        if current_node is None:
            return
        if current_node.symbol is not None:
            codes_dictionary[current_node.symbol] = current_code if current_code else "0"
            return
        traverse_tree(current_node.left_child, current_code + "0")
        traverse_tree(current_node.right_child, current_code + "1")
    traverse_tree(tree_root, "")
    return codes_dictionary