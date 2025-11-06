# visualizer.py

import graphviz
from data_structures import Node
from typing import Optional, List
from rich import print as rprint

def _find_leaves(node: Optional[Node]) -> List[Node]:
    """
    Вспомогательная функция: рекурсивно находит все ОБЪЕКТЫ Node,
    которые являются "листьями" (z1, z2...).
    """
    if node is None:
        return []
    if node.symbol is not None:
        return [node]
    return _find_leaves(node.left_child) + _find_leaves(node.right_child)

def _build_gv_tree(dot: graphviz.Digraph, node: Optional[Node]):
    """
    Рекурсивно "гуляет" по дереву и добавляет узлы/ветки
    в объект Digraph.
    """
    if node is None:
        return

    node_id = str(id(node))
    
    if node.symbol:
        # --- ЛИСТ (z1, z2...) ---
        dot.node(
            name=node_id,
            # Округляем до 3 знаков, как в примере
            label=f"{node.symbol}\n({node.probability:.3f})",
            shape="box"
        )
    else:
        # --- ВНУТРЕННИЙ УЗЕЛ (z5z4z3...) ---
        dot.node(
            name=node_id,
            # --- ИСПОЛЬЗУЕМ ПОЛЕ 'combined_name' ---
            label=f"{node.combined_name}\n({node.probability:.3f})",
            shape="box"
        )

    # --- Рекурсия и отрисовка веток ---
    if node.left_child:
        left_id = str(id(node.left_child))
        _build_gv_tree(dot, node.left_child)
        dot.edge(node_id, left_id, label="0")
        
    if node.right_child:
        right_id = str(id(node.right_child))
        _build_gv_tree(dot, node.right_child)
        dot.edge(node_id, right_id, label="1")

# --- ФУНКЦИЯ 1 (СТИЛЬ РИС. 3) ---
def generate_scheme_image(root_node: Node, algo_name: str):
    """
    Генерирует PNG в стиле "Схема" (Рис. 3)
    (Корень внизу, листья вверху, отсортированы по P)
    """
    filename = f"{algo_name.replace(' ', '_')}_Tree_Scheme"
    
    try:
        dot = graphviz.Digraph(comment=f'{algo_name} Scheme')
        dot.attr(rankdir='BT') # Снизу-вверх
        
        _build_gv_tree(dot, root_node)
        
        # Хак для сортировки листьев
        all_leaf_nodes = _find_leaves(root_node)
        sorted_leaf_nodes = sorted(all_leaf_nodes, key=lambda n: n.probability, reverse=True)
        sorted_leaf_ids = [str(id(n)) for n in sorted_leaf_nodes]
        
        if len(sorted_leaf_ids) > 1:
            with dot.subgraph() as s:
                s.attr(rank='max') # 'max' - самый верхний ранг
                for i in range(len(sorted_leaf_ids)):
                    s.node(sorted_leaf_ids[i])
                    if i > 0:
                        s.edge(sorted_leaf_ids[i-1], sorted_leaf_ids[i], style='invis')
        
        dot.render(filename, format='png', cleanup=True, view=False)
        rprint(f"[bold green]...Изображение (Схема, Рис. 3) сохранено: [cyan]{filename}.png[/cyan][/bold green]")

    except Exception as e:
        _handle_gv_error(e)

# --- ФУНКЦИЯ 2 (СТИЛЬ РИС. 4) ---
def generate_classic_tree_image(root_node: Node, algo_name: str):
    """
    Генерирует PNG в стиле "Кодовое дерево" (Рис. 4)
    (Корень вверху, листья внизу, авто-раскладка)
    """
    filename = f"{algo_name.replace(' ', '_')}_Tree_Classic"
    
    try:
        dot = graphviz.Digraph(comment=f'{algo_name} Classic Tree')
        dot.attr(rankdir='TB') # Сверху-вниз
        
        # Просто строим дерево, без хаков
        _build_gv_tree(dot, root_node)
        
        dot.render(filename, format='png', cleanup=True, view=False)
        rprint(f"[bold green]...Изображение (Дерево, Рис. 4) сохранено: [cyan]{filename}.png[/cyan][/bold green]")

    except Exception as e:
        _handle_gv_error(e)

# --- Вспомогательная функция, чтобы не дублировать код ---
def _handle_gv_error(e: Exception):
    """Обрабатывает ошибки Graphviz"""
    if isinstance(e, graphviz.backend.execute.ExecutableNotFound):
        rprint("\n" + "="*50)
        rprint("[bold red]ОШИБКА: 'dot' executable не найден.[/bold red]")
        rprint("[yellow]Пожалуйста, установите движок Graphviz (https://graphviz.org/download/)[/yellow]")
        rprint("[dim]  Для Windows (в choco): [cyan]choco install graphviz[/cyan][/dim]")
        rprint("[dim]  Для macOS (в brew):   [cyan]brew install graphviz[/cyan][/dim]")
        rprint("[dim]  Для Linux (apt):      [cyan]sudo apt-get install graphviz[/cyan][/dim]")
        rprint("="*50 + "\n")
    elif isinstance(e, ImportError):
        rprint("[bold red]Ошибка: Библиотека 'graphviz' не установлена.[/bold red]")
        rprint("[yellow]Пожалуйста, выполните: [cyan]pip install graphviz[/cyan][/yellow]")
    else:
        rprint(f"[bold red]Не удалось сгенерировать изображение дерева: {e}[/bold red]")