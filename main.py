# main.py

import math
# --- Импорты наших модулей ---
import input_handler
import algorithms
import metrics
# --- ИМПОРТИРУЕМ НАШ ПАРАМЕТР ОКРУГЛЕНИЯ ---
from metrics import ROUND_DIGITS

# --- Импорты для "красоты" ---
from rich.console import Console
from rich.table import Table
from rich import print as rprint
from rich.panel import Panel

def _build_codes_table(
    probabilities: dict, 
    generated_codes: dict, 
    symbols_list: list, 
    title: str
) -> Table:
    """Вспомогательная функция для создания итоговых таблиц."""
    
    table = Table(title=title)
    table.add_column("Символ (z)", style="cyan", no_wrap=True)
    table.add_column("Вероятность (p)", style="magenta")
    table.add_column("Кодовое слово", style="yellow")
    table.add_column("Длина (L)", style="green", justify="right")
    
    for symbol in symbols_list:
        prob = probabilities[symbol]
        code = generated_codes[symbol]
        length = len(code)
        
        table.add_row(
            symbol,
            f"{prob:.{ROUND_DIGITS}f}", # Используем округление
            code,
            str(length)
        )
    return table

def main():
    """
    Главная "оркестровая" функция программы.
    """
    console = Console()
    rprint("[bold green]Запуск программы кодирования Хаффмана...[/bold green]")
    rprint("="*50)

    # --- ШАГ 1: ПОЛУЧЕНИЕ ДАННЫХ ---
    rprint("[bold blue]Шаг 1: Ввод данных...[/bold blue]")
    probabilities = input_handler.get_probabilities()

    if not probabilities:
        rprint("[bold red]Ошибка: Вероятности не получены. Выход.[/bold red]")
        return

    # --- ШАГ 2: ПОСТРОЕНИЕ ДЕРЕВА ---
    rprint("\n[bold blue]Шаг 2: Построение дерева Хаффмана...[/bold blue]")
    try:
        huffman_tree_root = algorithms.build_huffman_tree(probabilities)
        rprint("[green]...Дерево успешно построено.[/green]")
    except Exception as e:
        rprint(f"[bold red]Критическая ошибка при построении дерева: {e}[/bold red]")
        return

    # --- ШАГ 3: ГЕНЕРАЦИЯ КОДОВ ---
    rprint("\n[bold blue]Шаг 3: Генерация кодов из дерева...[/bold blue]")
    try:
        generated_codes = algorithms.generate_codes_from_tree(huffman_tree_root)
        rprint("[green]...Коды успешно сгенерированы.[/green]")
    except Exception as e:
        rprint(f"[bold red]Критическая ошибка при генерации кодов: {e}[/bold red]")
        return

    # --- ШАГ 4: РАСЧЕТ МЕТРИК ("МАТАН") ---
    rprint("\n[bold blue]Шаг 4: Расчет метрик...[/bold blue]")
    
    try:
        # --- H (Энтропия) ---
        h_result, h_gen, h_exp, h_sub = metrics.calculate_entropy(probabilities)
        console.print(
            Panel(
                f"[dim]{h_gen}[/dim]\n[dim]{h_exp}[/dim]\n{h_sub}\n\n"
                f"[bold]H = {h_result:.{ROUND_DIGITS}f} бит[/bold] [dim]| (raw: {h_result})[/dim]",
                title="[bold yellow]H (Энтропия)[/bold yellow]",
                border_style="yellow",
                padding=(1, 2)
            )
        )

        # --- L_avg (Средняя длина) ---
        l_result, l_gen, l_exp, l_sub = metrics.calculate_average_length(probabilities, generated_codes)
        console.print(
            Panel(
                f"[dim]{l_gen}[/dim]\n[dim]{l_exp}[/dim]\n{l_sub}\n\n"
                f"[bold]L_avg = {l_result:.{ROUND_DIGITS}f} бит/символ[/bold] [dim]| (raw: {l_result})[/dim]",
                title="[bold green]L_avg (Средняя длина)[/bold green]",
                border_style="green",
                padding=(1, 2)
            )
        )
        
        # --- r (Избыточность) ---
        r_result, r_gen, r_sub = metrics.calculate_redundancy(l_result, h_result)
        console.print(
            Panel(
                f"[dim]{r_gen}[/dim]\n{r_sub}\n\n"
                f"[bold]r = {r_result:.{ROUND_DIGITS}f} бит[/bold] [dim]| (raw: {r_result})[/dim]",
                title="[bold cyan]r (Избыточность)[/bold cyan]",
                border_style="cyan",
                padding=(1, 2)
            )
        )

        # --- K (Неравенство Крафта) ---
        k_result, k_gen, k_exp, k_sub = metrics.calculate_kraft_inequality(generated_codes)
        
        # Не будем показывать raw, если K=1.0, чтобы не мозолить глаза
        raw_k_str = f"[dim]| (raw: {k_result})[/dim]" if not math.isclose(k_result, 1.0) else ""
        
        if math.isclose(k_result, 1.0) or k_result < 1.0:
            kraft_status = (
                f"[bold green]K = {k_result:.{ROUND_DIGITS}f} (≤ 1.0)[/bold green] {raw_k_str}\n"
                f"[green]Неравенство выполняется, код однозначно декодируем.[/green]"
            )
        else:
            kraft_status = (
                f"[bold red]K = {k_result:.{ROUND_DIGITS}f} (> 1.0)[/bold red] {raw_k_str}\n"
                f"[red]Ошибка! Код НЕ является однозначно декодируемым.[/red]"
            )
        
        console.print(
            Panel(
                f"[dim]{k_gen}[/dim]\n[dim]{k_exp}[/dim]\n{k_sub}\n\n{kraft_status}",
                title="[bold magenta]K (Неравенство Крафта)[/bold magenta]",
                border_style="magenta",
                padding=(1, 2)
            )
        )
    except Exception as e:
        rprint(f"[bold red]Критическая ошибка при расчете метрик: {e}[/bold red]")


    # --- ШАГ 5: ВЫВОД ИТОГОВЫХ ТАБЛИЦ ---
    rprint("\n[bold blue]Шаг 5: Итоговые коды[/bold blue]")
    
    # --- Таблица 1 (Сортировка по P) ---
    sorted_by_prob = sorted(
        probabilities.keys(),
        key=lambda symbol: probabilities[symbol],
        reverse=True
    )
    table1 = _build_codes_table(
        probabilities, 
        generated_codes, 
        sorted_by_prob, 
        "[bold]Коды (отсортировано по P ↓)[/bold]"
    )
    console.print(table1)

    # --- Таблица 2 (Сортировка по Z) ---
    sorted_by_name = sorted(
        probabilities.keys(),
        key=lambda z: int(z[1:])
    )
    table2 = _build_codes_table(
        probabilities, 
        generated_codes, 
        sorted_by_name, 
        "[bold]Коды (отсортировано по Z ↑)[/bold]"
    )
    console.print(table2)


if __name__ == "__main__":
    main()