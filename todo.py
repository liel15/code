import json
import os
import sys
from datetime import datetime, timedelta
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.box import ROUNDED, DOUBLE, SIMPLE_HEAVY
from rich.text import Text
from rich.align import Align
from rich.columns import Columns
from rich.progress import Progress, BarColumn, TextColumn
from rich.prompt import Prompt, Confirm, IntPrompt
from rich.status import Status
import inquirer

sys.stdout.reconfigure(encoding='utf-8')

console = Console()
DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "todos.json")

def load_todos():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_todos(todos):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(todos, f, ensure_ascii=False, indent=2)

def get_priority_color(priority):
    return {"high": "red", "medium": "yellow", "low": "green"}.get(priority, "white")

def get_priority_icon(priority):
    return {"high": "[bold red]▲[/bold red]", "medium": "[bold yellow]●[/bold yellow]", "low": "[bold green]▼[/bold green]"}.get(priority, "○")

def get_due_info(todo):
    if not todo.get("due_date"):
        return ""
    due = datetime.strptime(todo["due_date"], "%Y-%m-%d")
    days_left = (due - datetime.now()).days
    if days_left < 0:
        return f"[bold red]마감지남 ({abs(days_left)}일 전)[/bold red]"
    elif days_left == 0:
        return "[bold yellow]오늘 마감![/bold yellow]"
    elif days_left <= 3:
        return f"[bold yellow]{days_left}일 남음[/bold yellow]"
    else:
        return f"[dim]~ {todo['due_date']}[/dim]"

def show_banner():
    banner = Panel(
        Align.center(Text("TODO MANAGER", style="bold cyan")),
        box=DOUBLE,
        border_style="cyan",
        padding=(0, 1)
    )
    console.print(banner)

def show_stats(todos):
    total = len(todos)
    if total == 0:
        console.print(Panel("[yellow]할일이 없습니다.[/yellow]", border_style="yellow"))
        return
    
    completed = sum(1 for t in todos if t["completed"])
    pending = total - completed
    progress = int((completed / total) * 100) if total > 0 else 0
    
    high = sum(1 for t in todos if t["priority"] == "high" and not t["completed"])
    medium = sum(1 for t in todos if t["priority"] == "medium" and not t["completed"])
    low = sum(1 for t in todos if t["priority"] == "low" and not t["completed"])
    overdue = sum(1 for t in todos if t.get("due_date") and not t["completed"] and 
                  datetime.strptime(t["due_date"], "%Y-%m-%d") < datetime.now())
    
    stats_table = Table.grid(padding=1)
    stats_table.add_column()
    stats_table.add_column()
    
    stats_table.add_row("전체", f"[bold]{total}[/bold]")
    stats_table.add_row("완료", f"[bold green]{completed}[/bold green]")
    stats_table.add_row("대기", f"[bold yellow]{pending}[/bold yellow]")
    stats_table.add_row("진행률", f"[bold cyan]{progress}%[/bold cyan]")
    
    priority_text = Text()
    priority_text.append("높음: ", style="red")
    priority_text.append(f"{high}  ", style="bold red")
    priority_text.append("보통: ", style="yellow")
    priority_text.append(f"{medium}  ", style="bold yellow")
    priority_text.append("낮음: ", style="green")
    priority_text.append(f"{low}", style="bold green")
    
    with Progress(BarColumn(bar_width=40), TextColumn("[progress.percentage]{task.percentage:>3.0f}%"), transient=True) as progress_bar:
        task = progress_bar.add_task("", total=100)
        progress_bar.update(task, completed=progress)
    
    panel_content = Table.grid()
    panel_content.add_row(stats_table)
    panel_content.add_row(priority_text)
    if overdue > 0:
        panel_content.add_row(Text(f"⚠ 마감 지난 할일: {overdue}개", style="bold red"))
    
    console.print(Panel(panel_content, title="[bold]📊 통계[/bold]", border_style="blue", box=ROUNDED))

def list_todos(filter_by=None):
    todos = load_todos()
    
    if filter_by == "completed":
        todos = [t for t in todos if t["completed"]]
    elif filter_by == "pending":
        todos = [t for t in todos if not t["completed"]]
    
    if not todos:
        console.print(Panel("[yellow]할일이 없습니다.[/yellow]", border_style="yellow"))
        return
    
    table = Table(title="[bold]TODO LIST[/bold]", box=ROUNDED, border_style="cyan", show_lines=True)
    table.add_column("#", style="dim", width=4, justify="center")
    table.add_column("상태", width=6, justify="center")
    table.add_column("우선순위", width=8, justify="center")
    table.add_column("할일", style="bold", min_width=20)
    table.add_column("생성일", style="dim", width=16)
    table.add_column("마감일", width=20)
    
    for todo in todos:
        status = "[bold green]✓[/bold green]" if todo["completed"] else "[bold red]✗[/bold red]"
        color = get_priority_color(todo["priority"])
        icon = get_priority_icon(todo["priority"])
        due_info = get_due_info(todo)
        
        title_display = f"[{color}]{todo['title']}[/{color}]" if not todo["completed"] else f"[dim strike]{todo['title']}[/dim strike]"
        
        table.add_row(
            str(todo["id"]),
            status,
            f"[{color}]{icon}[/{color}]",
            title_display,
            todo["created_at"],
            due_info
        )
    
    console.print(table)

def interactive_menu():
    show_banner()
    todos = load_todos()
    show_stats(todos)
    console.print()
    
    while True:
        console.print("[bold cyan]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/bold cyan]")
        console.print("[1] 📋 할일 목록 보기")
        console.print("[2] ➕ 할일 추가")
        console.print("[3] ✅ 완료 처리")
        console.print("[4] 🗑️  할일 삭제")
        console.print("[5] 📊 통계 보기")
        console.print("[0] 🚪 종료")
        console.print("[bold cyan]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/bold cyan]")
        
        try:
            choice = input("\n선택 (기본값: 1): ").strip() or "1"
            if choice not in ["0", "1", "2", "3", "4", "5"]:
                console.print("[red]잘못된 선택입니다.[/red]")
                continue
        except EOFError:
            break
        
        if choice == "0":
            console.print("[yellow]안녕히 가세요![/yellow]")
            break
        
        elif choice == "1":
            console.print()
            list_todos()
            input("\n[Enter]를 눌러 계속...")
            console.clear()
        
        elif choice == "2":
            console.print("\n[bold]할일 추가[/bold]")
            title = input("할일 내용: ").strip()
            if not title:
                console.print("[red]내용을 입력하세요.[/red]")
                continue
            
            console.print("우선순위: [1] 높음 [2] 보통 [3] 낮음")
            p_choice = input("선택 (기본값: 2): ").strip() or "2"
            priority_map = {"1": "high", "2": "medium", "3": "low"}
            priority = priority_map.get(p_choice, "medium")
            
            due_days = None
            set_due = input("마감일 설정? (y/N): ").strip().lower()
            if set_due == 'y':
                try:
                    due_days = int(input("며칠 후 마감? (기본값: 7): ").strip() or "7")
                except ValueError:
                    due_days = 7
            
            todos = load_todos()
            due_date = None
            if due_days is not None:
                due_date = (datetime.now() + timedelta(days=due_days)).strftime("%Y-%m-%d")
            
            todo = {
                "id": len(todos) + 1,
                "title": title,
                "completed": False,
                "priority": priority,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "due_date": due_date,
                "completed_at": None
            }
            todos.append(todo)
            save_todos(todos)
            console.print(f"[bold green]✓ 추가됨: {title}[/bold green]")
            
        elif choice == "3":
            todos = load_todos()
            pending = [t for t in todos if not t["completed"]]
            if not pending:
                console.print("[yellow]완료할 할일이 없습니다.[/yellow]")
                continue
            
            console.print("\n[bold]완료할 할일 선택:[/bold]")
            for t in pending:
                color = get_priority_color(t["priority"])
                console.print(f"  [{color}]{t['id']}. {t['title']}[/{color}]")
            
            try:
                todo_id = int(input("\nID 입력: "))
            except ValueError:
                console.print("[red]잘못된 ID입니다.[/red]")
                continue
            
            for todo in todos:
                if todo["id"] == todo_id:
                    todo["completed"] = True
                    todo["completed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
                    save_todos(todos)
                    console.print(f"[bold green]✓ 완료: {todo['title']}[/bold green]")
                    break
            else:
                console.print("[red]ID를 찾을 수 없습니다.[/red]")
        
        elif choice == "4":
            todos = load_todos()
            if not todos:
                console.print("[yellow]삭제할 할일이 없습니다.[/yellow]")
                continue
            
            console.print("\n[bold]삭제할 할일 선택:[/bold]")
            for t in todos:
                color = get_priority_color(t["priority"])
                status = "✓" if t["completed"] else ""
                console.print(f"  [{color}]{t['id']}. {t['title']} {status}[/{color}]")
            
            try:
                todo_id = int(input("\nID 입력: "))
            except ValueError:
                console.print("[red]잘못된 ID입니다.[/red]")
                continue
            
            confirm = input("정말 삭제하시겠습니까? (y/N): ").strip().lower()
            if confirm == 'y':
                for i, todo in enumerate(todos):
                    if todo["id"] == todo_id:
                        deleted = todos.pop(i)
                        save_todos(todos)
                        console.print(f"[bold red]✗ 삭제됨: {deleted['title']}[/bold red]")
                        break
                else:
                    console.print("[red]ID를 찾을 수 없습니다.[/red]")
        
        elif choice == "5":
            console.print()
            show_stats(load_todos())
            input("\n[Enter]를 눌러 계속...")
        
        console.print()

if __name__ == "__main__":
    interactive_menu()
