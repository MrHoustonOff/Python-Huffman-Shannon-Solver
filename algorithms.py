import heapq
from data_structures import Node, create_node
from typing import Dict, List, Optional, Tuple
from rich import print as rprint

def build_huffman_tree(probabilities: Dict[str, float]) -> Optional[Node]:
    """
    Строит дерево Хаффмана по "донному" (bottom-up) алгоритму.

    Реализует правило кодирования из методички:
    Узел с БОЛЬШЕЙ вероятностью всегда помещается в левую ветку ('0').

    Args:
        probabilities (dict): Словарь {'z1': p1, 'z2': p2, ...}.

    Returns:
        Node | None: Корневой узел (Node) построенного дерева или None,
                     если входные данные пусты.
    """
    
    # priority_queue (min-heap) будет хранить узлы,
    # автоматически сортируя их по наименьшей вероятности.
    priority_queue: List[Node] = []
    
    if not probabilities:
        return None
        
    for symbol, prob in probabilities.items():
        # Создаем "лист", имя узла = имя символа
        leaf_node = create_node(probability=prob, symbol=symbol, combined_name=symbol)
        heapq.heappush(priority_queue, leaf_node)
        
    # Шаг "Редукция": повторяем, пока в очереди не останется 1 узел (корень)
    while len(priority_queue) > 1:
        
        # Достаем ДВА узла с наименьшими вероятностями
        node_1 = heapq.heappop(priority_queue)
        node_2 = heapq.heappop(priority_queue)
        
        # Применяем правило "Больше P -> 0"
        if node_1.probability >= node_2.probability:
            higher_prob_node = node_1
            lower_prob_node = node_2
        else:
            higher_prob_node = node_2
            lower_prob_node = node_1
            
        # Имя левой ветки (0) + Имя правой ветки (1)
        left_name = higher_prob_node.combined_name
        right_name = lower_prob_node.combined_name
            
        combined_prob = higher_prob_node.probability + lower_prob_node.probability
        
        parent_node = create_node(
            probability=combined_prob,
            left=higher_prob_node,  # Ветка '0'
            right=lower_prob_node, # Ветка '1'
            combined_name=f"{left_name}{right_name}"
        )
        
        heapq.heappush(priority_queue, parent_node)
        
    # Последний узел в очереди - это корень
    return heapq.heappop(priority_queue) if priority_queue else None


def _find_shannon_fano_split_index(sorted_probs: List[Tuple[str, float]]) -> int:
    """
    Вспомогательная функция для Шеннона-Фано.
    Находит "идеальную" точку разделения отсортированного списка
    вероятностей так, чтобы суммы левой и правой части
    минимально различались.

    Args:
        sorted_probs (list): Список кортежей [('z1', p1), ...],
                             УЖЕ отсортированный по P (убывание).

    Returns:
        int: Индекс, по которому нужно "разрезать" список.
    """
    total_prob = sum(item[1] for item in sorted_probs)
    min_diff = float('inf')
    best_split_index = 0
    current_left_sum = 0.0
    
    # Идем по списку, ищем минимальную разницу между двумя
    # формирующимися группами
    for i in range(len(sorted_probs) - 1):
        current_left_sum += sorted_probs[i][1]
        diff = abs(current_left_sum - (total_prob - current_left_sum))
        
        if diff < min_diff:
            min_diff = diff
            best_split_index = i + 1
        else:
            # Как только разница снова начала расти, мы нашли лучшую точку
            break
            
    # Гарантируем, что сплит всегда происходит (даже для 2-х элементов)
    if best_split_index == 0:
        return 1
        
    return best_split_index


def build_shannon_fano_tree(probabilities: Dict[str, float]) -> Optional[Node]:
    """
    Строит дерево Шеннона-Фано по "верхнему" (top-down)
    рекурсивному алгоритму.

    Args:
        probabilities (dict): Словарь {'z1': p1, 'z2': p2, ...}.

    Returns:
        Node | None: Корневой узел (Node) построенного дерева или None,
                     если входные данные пусты.
    """
    
    # 1. Сортируем символы по УБЫВАНИЮ вероятности
    sorted_probs: List[Tuple[str, float]] = sorted(
        probabilities.items(),
        key=lambda item: item[1],
        reverse=True
    )
    
    def _build_recursive(current_probs_list: List[Tuple[str, float]]) -> Optional[Node]:
        """Вложенная рекурсивная функция построения."""
        
        # Базовый случай рекурсии: в группе 1 символ -> это ЛИСТ
        if len(current_probs_list) == 1:
            symbol, prob = current_probs_list[0]
            return create_node(probability=prob, symbol=symbol, combined_name=symbol)
            
        if not current_probs_list:
            return None

        # Находим точку разделения
        split_index = _find_shannon_fano_split_index(current_probs_list)
        
        # Делим на две группы (Группа 0 - левая, Группа 1 - правая)
        group_zero = current_probs_list[:split_index]
        group_one = current_probs_list[split_index:]
        
        # Рекурсивный вызов для "детей"
        left_child = _build_recursive(group_zero)
        right_child = _build_recursive(group_one)
        
        # Создаем ВНУТРЕННИЙ узел
        combined_prob = (left_child.probability if left_child else 0) + (right_child.probability if right_child else 0)
        
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


def generate_codes_from_tree(tree_root: Optional[Node]) -> Dict[str, str]:
    """
    Рекурсивно обходит ЛЮБОЕ дерево (Node) и генерирует коды
    для каждого символа.

    Args:
        tree_root (Node, optional): Корневой узел дерева.

    Returns:
        dict: Словарь кодов {'z1': '01', 'z2': '110', ...}.
    """
    codes_dictionary: Dict[str, str] = {}
    
    def traverse_tree(current_node: Optional[Node], current_code: str):
        """Вложенная рекурсивная функция обхода."""
        if current_node is None:
            return
            
        # Базовый случай: дошли до "листа"
        if current_node.symbol is not None:
            # Если в дереве всего 1 узел, его код будет "0"
            codes_dictionary[current_node.symbol] = current_code if current_code else "0"
            return

        # Рекурсивный шаг: идем налево (0) и направо (1)
        traverse_tree(current_node.left_child, current_code + "0")
        traverse_tree(current_node.right_child, current_code + "1")

    # Начинаем обход с корня и пустого кода
    traverse_tree(tree_root, "")
    
    return codes_dictionary