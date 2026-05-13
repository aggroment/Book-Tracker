import json
import os
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import font as tkfont
from datetime import datetime

# ------------------ Класс приложения ------------------
class BookTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Book Tracker - Трекер прочитанных книг")
        self.root.geometry("950x650")
        self.root.resizable(True, True)

        # Файл для хранения данных
        self.data_file = "books.json"

        # Загружаем данные
        self.books = self.load_books()

        # Жанры (предустановленные)
        self.genres = ['Художественная литература', 'Детектив', 'Фантастика',
                      'Научная литература', 'Поэзия', 'Биография', 'История',
                      'Психология', 'Бизнес', 'Философия', 'Приключения', 'Другое']

        # Создание интерфейса
        self.create_widgets()

        # Обновление таблицы
        self.refresh_table()
        self.update_stats()

    def create_widgets(self):
        """Создание всех элементов интерфейса"""
        # Основной контейнер
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # === Панель ввода ===
        input_frame = ttk.LabelFrame(main_frame, text="Добавить книгу", padding=10)
        input_frame.pack(fill=tk.X, pady=(0, 10))

        # Название книги
        ttk.Label(input_frame, text="Название книги:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.title_entry = ttk.Entry(input_frame, width=30)
        self.title_entry.grid(row=0, column=1, padx=5, pady=5)

        # Автор
        ttk.Label(input_frame, text="Автор:").grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        self.author_entry = ttk.Entry(input_frame, width=25)
        self.author_entry.grid(row=0, column=3, padx=5, pady=5)

        # Жанр
        ttk.Label(input_frame, text="Жанр:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.genre_var = tk.StringVar(value=self.genres[0])
        self.genre_combo = ttk.Combobox(input_frame, textvariable=self.genre_var,
                                        values=self.genres, width=28, state="readonly")
        self.genre_combo.grid(row=1, column=1, padx=5, pady=5)

        # Количество страниц
        ttk.Label(input_frame, text="Кол-во страниц:").grid(row=1, column=2, padx=5, pady=5, sticky=tk.W)
        self.pages_entry = ttk.Entry(input_frame, width=15)
        self.pages_entry.grid(row=1, column=3, padx=5, pady=5)

        # Кнопка Добавить
        self.add_btn = tk.Button(input_frame, text="📚 Добавить книгу",
                                 bg='#27ae60', fg='white',
                                 font=('Arial', 10, 'bold'),
                                 command=self.add_book)
        self.add_btn.grid(row=1, column=4, padx=10, pady=5)

        # === Панель фильтрации ===
        filter_frame = ttk.LabelFrame(main_frame, text="Фильтрация", padding=10)
        filter_frame.pack(fill=tk.X, pady=(0, 10))

        # Фильтр по жанру
        ttk.Label(filter_frame, text="Жанр:").grid(row=0, column=0, padx=5, pady=5)
        self.filter_genre = ttk.Combobox(filter_frame, values=['Все'] + self.genres,
                                         width=25, state="readonly")
        self.filter_genre.grid(row=0, column=1, padx=5, pady=5)
        self.filter_genre.set('Все')

        # Фильтр по количеству страниц
        ttk.Label(filter_frame, text="Кол-во страниц:").grid(row=0, column=2, padx=5, pady=5)

        self.filter_pages_op = tk.StringVar(value=">")
        pages_op_frame = ttk.Frame(filter_frame)
        pages_op_frame.grid(row=0, column=3, padx=5, pady=5)

        ttk.Radiobutton(pages_op_frame, text=">", variable=self.filter_pages_op,
                       value=">", command=self.apply_filter).pack(side=tk.LEFT, padx=2)
        ttk.Radiobutton(pages_op_frame, text=">=", variable=self.filter_pages_op,
                       value=">=", command=self.apply_filter).pack(side=tk.LEFT, padx=2)
        ttk.Radiobutton(pages_op_frame, text="=", variable=self.filter_pages_op,
                       value="=", command=self.apply_filter).pack(side=tk.LEFT, padx=2)
        ttk.Radiobutton(pages_op_frame, text="<", variable=self.filter_pages_op,
                       value="<", command=self.apply_filter).pack(side=tk.LEFT, padx=2)
        ttk.Radiobutton(pages_op_frame, text="<=", variable=self.filter_pages_op,
                       value="<=", command=self.apply_filter).pack(side=tk.LEFT, padx=2)

        self.filter_pages_value = ttk.Entry(filter_frame, width=8)
        self.filter_pages_value.grid(row=0, column=4, padx=5, pady=5)

        # Кнопки фильтрации
        self.filter_btn = tk.Button(filter_frame, text="Применить фильтр",
                                    bg='#3498db', fg='white',
                                    command=self.apply_filter)
        self.filter_btn.grid(row=0, column=5, padx=10, pady=5)

        self.reset_btn = tk.Button(filter_frame, text="Сбросить",
                                   bg='#e74c3c', fg='white',
                                   command=self.reset_filter)
        self.reset_btn.grid(row=0, column=6, padx=5, pady=5)

        # === Таблица книг ===
        table_frame = ttk.LabelFrame(main_frame, text="Список прочитанных книг", padding=10)
        table_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Создание таблицы Treeview
        columns = ('id', 'title', 'author', 'genre', 'pages', 'date')
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=15)

        # Настройка колонок
        self.tree.heading('id', text='ID')
        self.tree.heading('title', text='Название')
        self.tree.heading('author', text='Автор')
        self.tree.heading('genre', text='Жанр')
        self.tree.heading('pages', text='Страниц')
        self.tree.heading('date', text='Дата добавления')

        self.tree.column('id', width=40, anchor=tk.CENTER)
        self.tree.column('title', width=200, anchor=tk.W)
        self.tree.column('author', width=150, anchor=tk.W)
        self.tree.column('genre', width=150, anchor=tk.W)
        self.tree.column('pages', width=80, anchor=tk.CENTER)
        self.tree.column('date', width=100, anchor=tk.CENTER)

        # Добавление скроллбара
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Контекстное меню для удаления
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Удалить книгу", command=self.delete_selected)
        self.tree.bind("<Button-3>", self.show_context_menu)

        # === Панель статистики ===
        stats_frame = ttk.LabelFrame(main_frame, text="Статистика", padding=10)
        stats_frame.pack(fill=tk.X)

        self.stats_label = ttk.Label(stats_frame, text="", font=('Arial', 11))
        self.stats_label.pack()

        # Кнопки управления данными
        control_frame = ttk.Frame(stats_frame)
        control_frame.pack(fill=tk.X, pady=(5, 0))

        self.save_btn = tk.Button(control_frame, text="💾 Сохранить в JSON",
                                  bg='#2c3e50', fg='white',
                                  command=self.save_to_file)
        self.save_btn.pack(side=tk.LEFT, padx=5)

        self.load_btn = tk.Button(control_frame, text="📂 Загрузить из JSON",
                                  bg='#2c3e50', fg='white',
                                  command=self.load_from_file)
        self.load_btn.pack(side=tk.LEFT, padx=5)

        self.clear_btn = tk.Button(control_frame, text="🗑️ Очистить всё",
                                   bg='#e74c3c', fg='white',
                                   command=self.clear_all)
        self.clear_btn.pack(side=tk.RIGHT, padx=5)

    def load_books(self):
        """Загрузка книг из JSON файла"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Добавляем ID, если нет
                    for i, book in enumerate(data, 1):
                        if 'id' not in book:
                            book['id'] = i
                        if 'date' not in book:
                            book['date'] = datetime.now().strftime("%Y-%m-%d")
                    return data
            except Exception as e:
                print(f"Ошибка загрузки: {e}")
                return []
        return []

    def save_books(self):
        """Сохранение книг в JSON файл"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.books, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить данные: {e}")
            return False

    def validate_inputs(self, title, author, pages_str):
        """Валидация входных данных"""
        # Проверка на пустые поля
        if not title.strip():
            messagebox.showerror("Ошибка", "Название книги не может быть пустым!")
            return False

        if not author.strip():
            messagebox.showerror("Ошибка", "Имя автора не может быть пустым!")
            return False

        # Проверка количества страниц
        if not pages_str.strip():
            messagebox.showerror("Ошибка", "Введите количество страниц!")
            return False

        try:
            pages = int(pages_str)
            if pages <= 0:
                messagebox.showerror("Ошибка", "Количество страниц должно быть положительным числом!")
                return False
            if pages > 10000:
                if not messagebox.askyesno("Подтверждение",
                                          "Вы ввели очень большое количество страниц (>10000). Продолжить?"):
                    return False
        except ValueError:
            messagebox.showerror("Ошибка", "Количество страниц должно быть целым числом!")
            return False

        return True

    def add_book(self):
        """Добавление новой книги"""
        title = self.title_entry.get()
        author = self.author_entry.get()
        genre = self.genre_var.get()
        pages_str = self.pages_entry.get()

        # Валидация
        if not self.validate_inputs(title, author, pages_str):
            return

        pages = int(pages_str)

        # Создание записи
        new_id = max([book['id'] for book in self.books] + [0]) + 1
        book = {
            'id': new_id,
            'title': title.strip(),
            'author': author.strip(),
            'genre': genre,
            'pages': pages,
            'date': datetime.now().strftime("%Y-%m-%d %H:%M")
        }

        self.books.append(book)
        self.save_books()

        # Очистка полей
        self.title_entry.delete(0, tk.END)
        self.author_entry.delete(0, tk.END)
        self.pages_entry.delete(0, tk.END)

        # Обновление
        self.refresh_table()
        self.update_stats()
        messagebox.showinfo("Успех", f"Книга \"{title}\" добавлена!")

    def delete_selected(self):
        """Удаление выбранной книги"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите книгу для удаления!")
            return

        if messagebox.askyesno("Подтверждение", "Удалить выбранную(ые) книгу(и)?"):
            for item in selected:
                book_id = int(self.tree.item(item)['values'][0])
                self.books = [book for book in self.books if book['id'] != book_id]

            # Перенумерация ID
            for i, book in enumerate(self.books, 1):
                book['id'] = i

            self.save_books()
            self.refresh_table()
            self.update_stats()
            messagebox.showinfo("Успех", "Книга(и) удалена!")

    def show_context_menu(self, event):
        """Показать контекстное меню"""
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)

    def get_filtered_books(self):
        """Получение отфильтрованных книг"""
        filtered = self.books.copy()

        # Фильтр по жанру
        genre_filter = self.filter_genre.get()
        if genre_filter != 'Все':
            filtered = [book for book in filtered if book['genre'] == genre_filter]

        # Фильтр по количеству страниц
        pages_value = self.filter_pages_value.get().strip()
        if pages_value:
            try:
                pages_num = int(pages_value)
                op = self.filter_pages_op.get()

                if op == '>':
                    filtered = [book for book in filtered if book['pages'] > pages_num]
                elif op == '>=':
                    filtered = [book for book in filtered if book['pages'] >= pages_num]
                elif op == '=':
                    filtered = [book for book in filtered if book['pages'] == pages_num]
                elif op == '<':
                    filtered = [book for book in filtered if book['pages'] < pages_num]
                elif op == '<=':
                    filtered = [book for book in filtered if book['pages'] <= pages_num]
            except ValueError:
                pass  # Игнорируем неверный ввод

        return filtered

    def refresh_table(self):
        """Обновление таблицы"""
        # Очистка таблицы
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Добавление отфильтрованных записей
        for book in self.get_filtered_books():
            self.tree.insert('', tk.END, values=(
                book['id'],
                book['title'],
                book['author'],
                book['genre'],
                book['pages'],
                book['date']
            ))

    def update_stats(self):
        """Обновление статистики"""
        filtered = self.get_filtered_books()
        total = len(filtered)

        if total == 0:
            self.stats_label.config(text="📊 Нет книг для отображения")
            return

        total_pages = sum(book['pages'] for book in filtered)
        avg_pages = total_pages // total if total > 0 else 0

        # Статистика по жанрам
        genre_stats = {}
        for book in filtered:
            genre_stats[book['genre']] = genre_stats.get(book['genre'], 0) + 1

        # Формирование текста статистики
        stats_text = f"📚 Всего книг: {total} | 📖 Всего страниц: {total_pages} | "
        stats_text += f"📊 Среднее: {avg_pages} стр.\n"

        if genre_stats:
            # Показываем топ-3 жанра
            top_genres = sorted(genre_stats.items(), key=lambda x: x[1], reverse=True)[:3]
            stats_text += "🏆 Популярные жанры: "
            stats_text += ", ".join([f"{genre} ({count})" for genre, count in top_genres])

        self.stats_label.config(text=stats_text)

    def apply_filter(self):
        """Применение фильтров"""
        # Валидация ввода страниц
        pages_value = self.filter_pages_value.get().strip()
        if pages_value:
            try:
                pages_num = int(pages_value)
                if pages_num < 0:
                    messagebox.showerror("Ошибка", "Количество страниц не может быть отрицательным!")
                    return
            except ValueError:
                if pages_value:  # Если не пустое, но не число
                    messagebox.showerror("Ошибка", "Введите число для фильтрации по страницам!")
                    return

        self.refresh_table()
        self.update_stats()

    def reset_filter(self):
        """Сброс фильтров"""
        self.filter_genre.set('Все')
        self.filter_pages_value.delete(0, tk.END)
        self.filter_pages_op.set('>')
        self.refresh_table()
        self.update_stats()

    def save_to_file(self):
        """Сохранение в JSON файл (с возможностью выбора)"""
        if self.save_books():
            messagebox.showinfo("Успех", f"Данные сохранены в файл {self.data_file}")

    def load_from_file(self):
        """Загрузка из JSON файла"""
        if os.path.exists(self.data_file):
            try:
                self.books = self.load_books()
                self.refresh_table()
                self.update_stats()
                messagebox.showinfo("Успех", f"Данные загружены из файла {self.data_file}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить данные: {e}")
        else:
            messagebox.showwarning("Предупреждение", f"Файл {self.data_file} не найден!")

    def clear_all(self):
        """Очистка всех данных"""
        if messagebox.askyesno("Подтверждение",
                              "Вы уверены, что хотите удалить ВСЕ книги? Это действие необратимо!"):
            self.books = []
            self.save_books()
            self.refresh_table()
            self.update_stats()
            messagebox.showinfo("Успех", "Все книги удалены!")


# ------------------ Запуск приложения ------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = BookTracker(root)
    root.mainloop()
