import tkinter as tk
from tkinter import messagebox, ttk
import random
import json
import os

# Файл для хранения истории
HISTORY_FILE = "task_history.json"

# Предопределенные задачи с категориями
DEFAULT_TASKS = [
    {"text": "Прочитать статью", "type": "Учёба"},
    {"text": "Сделать зарядку", "type": "Спорт"},
    {"text": "Написать код", "type": "Работа"},
    {"text": "Проверить почту", "type": "Работа"},
    {"text": "Пробежка на свежем воздухе", "type": "Спорт"},
    {"text": "Изучить новую тему", "type": "Учёба"},
    {"text": "Помыть посуду", "type": "Дом"},
    {"text": "Позвонить другу", "type": "Личное"},
    {"text": "Сделать stretch-упражнения", "type": "Спорт"},
    {"text": "Прочитать книгу", "type": "Учёба"}
]

class TaskGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Random Task Generator")
        self.root.geometry("500x500")
        self.root.resizable(True, True)

        # Загрузка истории или создание новой
        self.history = self.load_history()

        # Список всех доступных задач
        self.tasks = DEFAULT_TASKS.copy()

        # Инициализация интерфейса
        self.setup_ui()

    def setup_ui(self):
        # --- Верхняя панель: генерация задачи ---
        top_frame = tk.Frame(self.root)
        top_frame.pack(pady=10, fill="x", padx=10)

        self.generate_btn = tk.Button(top_frame, text="🎲 Сгенерировать задачу",
                                      font=("Arial", 12), command=self.generate_task)
        self.generate_btn.pack(side="left", padx=5)

        self.task_label = tk.Label(top_frame, text="", font=("Arial", 14, "bold"),
                                   wraplength=400, fg="#2c3e50")
        self.task_label.pack(side="left", padx=20, fill="x", expand=True)

        # --- Панель фильтрации ---
        filter_frame = tk.Frame(self.root)
        filter_frame.pack(pady=5, fill="x", padx=10)

        tk.Label(filter_frame, text="Фильтр по типу:", font=("Arial", 10)).pack(side="left", padx=5)
        self.filter_var = tk.StringVar(value="Все")
        self.filter_combo = ttk.Combobox(filter_frame, textvariable=self.filter_var,
                                          values=["Все", "Учёба", "Спорт", "Работа", "Дом", "Личное"],
                                          state="readonly", width=15)
        self.filter_combo.pack(side="left", padx=5)
        self.filter_combo.bind("<<ComboboxSelected>>", self.apply_filter)

        self.filter_btn = tk.Button(filter_frame, text="Применить фильтр", command=self.apply_filter)
        self.filter_btn.pack(side="left", padx=5)

        # --- Панель добавления новой задачи ---
        add_frame = tk.Frame(self.root)
        add_frame.pack(pady=5, fill="x", padx=10)

        tk.Label(add_frame, text="Новая задача:", font=("Arial", 10)).pack(side="left", padx=5)
        self.new_task_entry = tk.Entry(add_frame, width=30, font=("Arial", 10))
        self.new_task_entry.pack(side="left", padx=5)

        tk.Label(add_frame, text="Тип:", font=("Arial", 10)).pack(side="left", padx=5)
        self.type_var = tk.StringVar(value="Учёба")
        self.type_combo = ttk.Combobox(add_frame, textvariable=self.type_var,
                                        values=["Учёба", "Спорт", "Работа", "Дом", "Личное"],
                                        state="readonly", width=10)
        self.type_combo.pack(side="left", padx=5)

        self.add_btn = tk.Button(add_frame, text="➕ Добавить", command=self.add_task)
        self.add_btn.pack(side="left", padx=5)

        # --- История задач (с прокруткой) ---
        history_frame = tk.Frame(self.root)
        history_frame.pack(fill="both", expand=True, padx=10, pady=10)

        tk.Label(history_frame, text="История задач:", font=("Arial", 12, "bold")).pack(anchor="w")

        # Создаём Listbox с прокруткой
        list_frame = tk.Frame(history_frame)
        list_frame.pack(fill="both", expand=True)

        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")

        self.history_listbox = tk.Listbox(list_frame, font=("Arial", 10),
                                           yscrollcommand=scrollbar.set,
                                           selectmode="single")
        self.history_listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.history_listbox.yview)

        # Нижняя панель с кнопками управления
        bottom_frame = tk.Frame(self.root)
        bottom_frame.pack(pady=5, fill="x", padx=10)

        self.clear_history_btn = tk.Button(bottom_frame, text="🗑 Очистить историю",
                                            command=self.clear_history, bg="#e74c3c", fg="white")
        self.clear_history_btn.pack(side="left", padx=5)

        self.save_btn = tk.Button(bottom_frame, text="💾 Сохранить", command=self.save_history)
        self.save_btn.pack(side="left", padx=5)

        self.delete_btn = tk.Button(bottom_frame, text="❌ Удалить выбранное",
                                     command=self.delete_selected)
        self.delete_btn.pack(side="left", padx=5)

        # Загружаем историю в интерфейс
        self.refresh_history_list()

    def generate_task(self):
        """Генерация случайной задачи из списка"""
        if not self.tasks:
            messagebox.showwarning("Нет задач", "Список задач пуст. Добавьте новые задачи.")
            return

        task = random.choice(self.tasks)
        self.task_label.config(text=f"📋 {task['text']}")

        # Добавляем в историю
        self.history.append(task)
        self.refresh_history_list()
        self.save_history()

    def apply_filter(self, event=None):
        """Фильтрация истории по типу задачи"""
        filter_type = self.filter_var.get()
        self.refresh_history_list(filter_type)

    def refresh_history_list(self, filter_type=None):
        """Обновление отображения истории в Listbox"""
        self.history_listbox.delete(0, tk.END)

        for idx, task in enumerate(self.history):
            if filter_type and filter_type != "Все":
                if task["type"] != filter_type:
                    continue
            display_text = f"{idx+1}. [{task['type']}] {task['text']}"
            self.history_listbox.insert(tk.END, display_text)

    def add_task(self):
        """Добавление новой задачи в список"""
        text = self.new_task_entry.get().strip()
        task_type = self.type_var.get()

        if not text:
            messagebox.showerror("Ошибка", "Задача не может быть пустой!")
            return

        # Проверка на дубликаты
        for task in self.tasks:
            if task["text"].lower() == text.lower() and task["type"] == task_type:
                messagebox.showwarning("Предупреждение", "Такая задача уже существует!")
                return

        new_task = {"text": text, "type": task_type}
        self.tasks.append(new_task)
        self.new_task_entry.delete(0, tk.END)

        messagebox.showinfo("Успех", f"Задача '{text}' добавлена в категорию '{task_type}'")

    def delete_selected(self):
        """Удаление выбранной задачи из истории"""
        selection = self.history_listbox.curselection()
        if not selection:
            messagebox.showwarning("Выбор", "Пожалуйста, выберите задачу для удаления.")
            return

        index = selection[0]
        filter_type = self.filter_var.get()
        # Находим реальный индекс в истории с учётом фильтра
        real_idx = -1
        count = -1
        for i, task in enumerate(self.history):
            if filter_type == "Все" or task["type"] == filter_type:
                count += 1
                if count == index:
                    real_idx = i
                    break

        if real_idx >= 0:
            removed = self.history.pop(real_idx)
            self.refresh_history_list(filter_type)
            self.save_history()
            messagebox.showinfo("Удалено", f"Задача '{removed['text']}' удалена из истории.")

    def clear_history(self):
        """Очистка всей истории"""
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите очистить всю историю?"):
            self.history.clear()
            self.refresh_history_list()
            self.save_history()

    def load_history(self):
        """Загрузка истории из JSON-файла"""
        if os.path.exists(HISTORY_FILE):
            try:
                with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return []
        return []

    def save_history(self):
        """Сохранение истории в JSON-файл"""
        try:
            with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                json.dump(self.history, f, ensure_ascii=False, indent=2)
        except IOError as e:
            messagebox.showerror("Ошибка сохранения", f"Не удалось сохранить историю: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = TaskGeneratorApp(root)
    root.mainloop()
