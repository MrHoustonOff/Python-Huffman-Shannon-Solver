# main.py

import math
# --- Импорты наших модулей ---
import input_handler
import algorithms
import metrics
import visualizer  # <-- Наш визуализатор
from metrics import ROUND_DIGITS

# --- Импорты для "красоты" ---
from rich.console import Console
from rich.table import Table
from rich import print as rprint
from rich.panel import Panel

# --- Словарь алгоритмов ---
ALGORITHMS = {
    "1": "Хаффман",
    "2": "Шеннон-Фано",
}

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
            f"{prob:.{ROUND_DIGITS}f}",
            code,
            str(length)
        )
    return table

def select_algorithm(previous_algo_name: str = None) -> str | None:
    """
    Отображает меню выбора алгоритма.
    """
    console = Console()
    rprint("\n" + "="*50)
    console.print("[bold]Выберите алгоритм для расчета:[/bold]")
    
    options = {}
    
    if previous_algo_name:
        # Режим "повторного запуска"
        other_algo_key = "2" if previous_algo_name == "Хаффман" else "1"
        other_algo_name = ALGORITHMS[other_algo_key]
        
        console.print(f"[bold green] [1] Рассчитать также для {other_algo_name}[/bold green]")
        console.print(f" [2] Рассчитать еще раз для {previous_algo_name}")
        
        options = {
            "1": other_algo_name,
            "2": previous_algo_name,
            "0": None # Выход
        }
    else:
        # Режим "первого запуска"
        console.print(f" [1] {ALGORITHMS['1']}")
        console.print(f" [2] {ALGORITHMS['2']}")
        options = {
            "1": ALGORITHMS['1'],
            "2": ALGORITHMS['2'],
            "0": None # Выход
        }
        
    console.print(f" [0] Выход из программы")
    
    while True:
        choice = console.input(f"Введите (0-{len(options)-1}): ")
        if choice in options:
            return options[choice] # Вернет Имя или None
        else:
            rprint("[red]Неверный ввод, попробуйте снова.[/red]")


def run_calculation_flow(algo_name: str, probabilities: dict):
    """
    Запускает полный цикл расчета (Шаги 2-5) для выбранного алгоритма.
    """
    console = Console()
    
    rprint(
        Panel(
            f"[bold white on blue] --- {algo_name.upper()} --- [/bold white on blue]",
            expand=False,
            padding=(0, 10)
        )
    )

    # --- ШАГ 2: ПОСТРОЕНИЕ ДЕРЕВА ---
    rprint(f"\n[bold blue]Шаг 2 ({algo_name}): Построение дерева...[/bold blue]")
    tree_root = None
    try:
        if algo_name == "Хаффман":
            tree_root = algorithms.build_huffman_tree(probabilities)
        elif algo_name == "Шеннон-Фано":
            # --- ИСПРАВЛЕННЫЙ ВЫЗОВ ---
            tree_root = algorithms.build_shannon_fano_tree(probabilities)
            
        if tree_root is None:
             rprint("[bold red]Ошибка: Не удалось построить дерево.[/bold red]")
             return
        rprint("[green]...Дерево успешно построено.[/green]")
        
    except Exception as e:
        rprint(f"[bold red]Критическая ошибка при построении дерева ({algo_name}): {e}[/bold red]")
        return

    # --- ШАГ 3: ГЕНЕРАЦИЯ КОДОВ И ВИЗУАЛИЗАЦИЯ ---
    
    rprint(f"\n[bold blue]Шаг 3 ({algo_name}): Генерация кодов и изображений...[/bold blue]")
    generated_codes = {}
    try:
        # 1. Генерируем коды (теперь это общий шаг)
        rprint("[dim]...Генерируем коды из дерева...[/dim]")
        generated_codes = algorithms.generate_codes_from_tree(tree_root)
        rprint("[green]...Коды успешно сгенерированы.[/green]")
        
        # 2. Визуализация
        rprint("[dim]...Запускаем генерацию изображений...[/dim]")
        if algo_name == "Хаффман":
            # --- ИСПРАВЛЕННЫЕ ВЫЗОВЫ ---
            visualizer.generate_scheme_image(tree_root, algo_name)
            visualizer.generate_classic_tree_image(tree_root, algo_name)
        elif algo_name == "Шеннон-Фано":
            # --- ИСПРАВЛЕННЫЙ ВЫЗОВ ---
            visualizer.generate_classic_tree_image(tree_root, algo_name)
            
    except Exception as e:
        rprint(f"[bold red]Критическая ошибка на Шаге 3: {e}[/bold red]")
        return

    # --- ШАГ 4: РАСЧЕТ МЕТРИК ("МАТАН") ---
    rprint(f"\n[bold blue]Шаг 4 ({algo_name}): Расчет метрик...[/bold blue]")
    try:
        h_result, h_gen, h_exp, h_sub = metrics.calculate_entropy(probabilities)
        console.print(Panel(f"[dim]{h_gen}[/dim]\n[dim]{h_exp}[/dim]\n{h_sub}\n\n[bold]H = {h_result:.{ROUND_DIGITS}f} бит[/bold] [dim]| (raw: {h_result})[/dim]", title=f"[bold yellow]H (Энтропия)[/bold yellow]", border_style="yellow", padding=(1, 2)))

        l_result, l_gen, l_exp, l_sub = metrics.calculate_average_length(probabilities, generated_codes)
        console.print(Panel(f"[dim]{l_gen}[/dim]\n[dim]{l_exp}[/dim]\n{l_sub}\n\n[bold]L_avg = {l_result:.{ROUND_DIGITS}f} бит/символ[/bold] [dim]| (raw: {l_result})[/dim]", title=f"[bold green]L_avg (Средняя длина)[/bold green]", border_style="green", padding=(1, 2)))
        
        r_result, r_gen, r_sub = metrics.calculate_redundancy(l_result, h_result)
        console.print(Panel(f"[dim]{r_gen}[/dim]\n{r_sub}\n\n[bold]r = {r_result:.{ROUND_DIGITS}f} бит[/bold] [dim]| (raw: {r_result})[/dim]", title=f"[bold cyan]r (Избыточность)[/bold cyan]", border_style="cyan", padding=(1, 2)))

        k_result, k_gen, k_exp, k_sub = metrics.calculate_kraft_inequality(generated_codes)
        raw_k_str = f"[dim]| (raw: {k_result})[/dim]" if not math.isclose(k_result, 1.0) else ""
        if math.isclose(k_result, 1.0) or k_result < 1.0:
            kraft_status = (f"[bold green]K = {k_result:.{ROUND_DIGITS}f} (≤ 1.0)[/bold green] {raw_k_str}\n[green]Неравенство выполняется, код однозначно декодируем.[/green]")
        else:
            kraft_status = (f"[bold red]K = {k_result:.{ROUND_DIGITS}f} (> 1.0)[/bold red] {raw_k_str}\n[red]Ошибка! Код НЕ является однозначно декодируемым.[/red]")
        console.print(Panel(f"[dim]{k_gen}[/dim]\n[dim]{k_exp}[/dim]\n{k_sub}\n\n{kraft_status}", title=f"[bold magenta]K (Неравенство Крафта)[/bold magenta]", border_style="magenta", padding=(1, 2)))
    
    except Exception as e:
        rprint(f"[bold red]Критическая ошибка при расчете метрик ({algo_name}): {e}[/bold red]")


    # --- ШАГ 5: ВЫВОД ИТОГОВЫХ ТАБЛИЦ ---
    rprint(f"\n[bold blue]Шаг 5 ({algo_name}): Итоговые коды[/bold blue]")
    
    sorted_by_prob = sorted(probabilities.keys(), key=lambda symbol: probabilities[symbol], reverse=True)
    table1 = _build_codes_table(probabilities, generated_codes, sorted_by_prob, f"[bold]Коды ({algo_name}) (отсортировано по P ↓)[/bold]")
    console.print(table1)

    sorted_by_name = sorted(probabilities.keys(), key=lambda z: int(z[1:]))
    table2 = _build_codes_table(probabilities, generated_codes, sorted_by_name, f"[bold]Коды ({algo_name}) (отсортировано по Z ↑)[/bold]")
    console.print(table2)


def main():
    """
    Главная "оркестровая" функция программы.
    """
    console = Console()
    rprint("[bold green]Запуск программы кодирования...[/bold green]")
    rprint("="*50)

    # --- ШАГ 1: ПОЛУЧЕНИЕ ДАННЫХ (ОДИН РАЗ) ---
    rprint("[bold blue]Шаг 1: Ввод данных...[/bold blue]")
    probabilities = input_handler.get_probabilities()
    if not probabilities:
        rprint("[bold red]Ошибка: Вероятности не получены. Выход.[/bold red]")
        return

    # --- ГЛАВНЫЙ ЦИКЛ (ЗАПУСК АЛГОРИТМОВ) ---
    last_algo_run = None
    while True:
        # Спрашиваем, что делать
        algo_to_run = select_algorithm(last_algo_run)
        
        if algo_to_run is None:
            # Пользователь выбрал [0] Выход
            break
            
        # Запускаем полный цикл расчета
        run_calculation_flow(algo_to_run, probabilities)
        
        # Запоминаем, что мы только что запустили
        last_algo_run = algo_to_run

    rprint("\n[bold green]Программа завершена. Удачной атты![/bold green]")


if __name__ == "__main__":
    print(
        r'''
<-. (`-')     (`-')  (`-').->                       (`-').->(`-')                <-. (`-')_ 
   \(OO )_ <-.(OO )  (OO )__      .->        .->    ( OO)_  ( OO).->       .->      \( OO) )
,--./  ,-.),------,),--. ,'-'(`-')----. ,--.(,--.  (_)--\_) /    '._  (`-')----. ,--./ ,--/ 
|   `.'   ||   /`. '|  | |  |( OO).-.  '|  | |(`-')/    _ / |'--...__)( OO).-.  '|   \ |  | 
|  |'.'|  ||  |_.' ||  `-'  |( _) | |  ||  | |(OO )\_..`--. `--.  .--'( _) | |  ||  . '|  |)
|  |   |  ||  .   .'|  .-.  | \|  |)|  ||  | | |  \.-._)   \   |  |    \|  |)|  ||  |\    | 
|  |   |  ||  |\  \ |  | |  |  '  '-'  '\  '-'(_ .'\       /   |  |     '  '-'  '|  | \   | 
`--'   `--'`--' '--'`--' `--'   `-----'  `-----'    `-----'    `--'      `-----' `--'  `--' 
''')
    main()