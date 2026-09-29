import sys

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QAction, QKeySequence
from PyQt6.QtWidgets import (
    QApplication, QCheckBox, QComboBox, QDialog, QDialogButtonBox,
    QFileDialog, QFormLayout, QGroupBox, QHBoxLayout, QInputDialog, QLabel,
    QLineEdit, QListWidget, QMainWindow, QMessageBox, QProgressBar,
    QPushButton, QRadioButton, QSlider, QSpinBox, QTextEdit, QToolBar,
    QVBoxLayout, QWidget,
)


# ======================================================================
# ЗАВДАННЯ 1
# ======================================================================

class Task1Window(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Завдання 1 — Базові віджети та layouts")
        self.setMinimumSize(520, 560)

        # --- Група 1: форма (QFormLayout) ---
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Введіть ім'я")
        self.name_edit.setToolTip("Ім'я користувача")

        self.combo = QComboBox()
        self.combo.addItems(["Студент", "Викладач", "Гість"])
        self.combo.setCurrentIndex(0)
        self.combo.setToolTip("Оберіть роль")

        self.spin = QSpinBox()
        self.spin.setRange(16, 99)
        self.spin.setValue(18)
        self.spin.setToolTip("Вік (16–99)")

        form = QFormLayout()
        form.addRow("Ім'я:", self.name_edit)
        form.addRow("Роль:", self.combo)
        form.addRow("Вік:", self.spin)
        form_box = QGroupBox("Дані користувача")
        form_box.setLayout(form)

       
        self.check = QCheckBox("Отримувати сповіщення")
        self.check.setChecked(True)
        self.check.setToolTip("Увімкнути/вимкнути сповіщення")

        self.radio_a = QRadioButton("Світла тема")
        self.radio_b = QRadioButton("Темна тема")
        self.radio_a.setChecked(True)
        self.radio_b.setToolTip("Тема оформлення (лише демонстрація)")
        radio_row = QHBoxLayout()
        radio_row.addWidget(self.radio_a)
        radio_row.addWidget(self.radio_b)

        opts = QVBoxLayout()
        opts.addWidget(self.check)
        opts.addLayout(radio_row)  
        opts_box = QGroupBox("Параметри")
        opts_box.setLayout(opts)

     
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(0, 100)
        self.slider.setValue(30)
        self.slider.setToolTip("Перетягніть, щоб змінити прогрес")

        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(30)
        self.slider.valueChanged.connect(self.progress.setValue)

        self.disabled_btn = QPushButton("Недоступна кнопка")
        self.disabled_btn.setEnabled(False)
        self.disabled_btn.setToolTip("Кнопка вимкнена (enabled=False)")

        val_layout = QVBoxLayout()
        val_layout.addWidget(QLabel("Повзунок і прогрес:"))
        val_layout.addWidget(self.slider)
        val_layout.addWidget(self.progress)
        val_layout.addWidget(self.disabled_btn)
        val_box = QGroupBox("Значення")
        val_box.setLayout(val_layout)

    
        self.text = QTextEdit()
        self.text.setPlaceholderText("Тут можна написати коментар...")
        self.text.setToolTip("Багаторядкове поле")

      
        ok_btn = QPushButton("OK")
        ok_btn.setToolTip("Закрити вікно")
        ok_btn.clicked.connect(self.close)
        clear_btn = QPushButton("Очистити текст")
        clear_btn.clicked.connect(self.text.clear)
        buttons = QHBoxLayout()
        buttons.addStretch()
        buttons.addWidget(clear_btn)
        buttons.addWidget(ok_btn)

        
        top = QHBoxLayout()
        top.addWidget(form_box, 1)
        top.addWidget(opts_box, 1)

        main = QVBoxLayout(self)
        main.addLayout(top)
        main.addWidget(val_box)
        main.addWidget(QLabel("Коментар:"))
        main.addWidget(self.text, 1)  
        main.addLayout(buttons)


# ======================================================================
# ЗАВДАННЯ 2
# ======================================================================

COUNTRIES = ["— оберіть —", "Україна", "Польща", "Німеччина", "Інша"]


def validate(name: str, age: int, country_index: int) -> list[str]:
    """Єдине місце валідації. Повертає список помилок (порожній = все ОК)."""
    errors = []
    if not name.strip():
        errors.append("Ім'я не може бути порожнім.")
    elif len(name.strip()) < 2:
        errors.append("Ім'я має містити щонайменше 2 символи.")
    if not (16 <= age <= 99):
        errors.append("Вік має бути в межах 16–99.")
    if country_index <= 0:
        errors.append("Оберіть країну зі списку.")
    return errors


def count_chars(label: QLabel, text: str):
    """Звичайна функція (не метод класу) як слот."""
    label.setText(f"Символів: {len(text)}")


class Task2Window(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Завдання 2 — Інтерактивна форма")
        self.setMinimumWidth(400)

        # Поля вводу: текст, число, список, прапорець, повзунок
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Ім'я")
        self.chars_label = QLabel("Символів: 0")

        self.age_spin = QSpinBox()
        self.age_spin.setRange(0, 120)
        self.age_spin.setValue(18)

        self.country = QComboBox()
        self.country.addItems(COUNTRIES)

        self.level_slider = QSlider(Qt.Orientation.Horizontal)
        self.level_slider.setRange(1, 10)
        self.level_slider.setValue(5)
        self.level_label = QLabel("Рівень: 5")

        self.agree = QCheckBox("Погоджуюсь з умовами")

        self.submit_btn = QPushButton("Підтвердити")
        self.submit_btn.setEnabled(False)
        self.reset_btn = QPushButton("Скинути")
        self.result = QLabel("")
        self.result.setWordWrap(True)

        # Компонування
        form = QFormLayout()
        form.addRow("Ім'я:", self.name_edit)
        form.addRow("", self.chars_label)
        form.addRow("Вік:", self.age_spin)
        form.addRow("Країна:", self.country)
        form.addRow(self.level_label, self.level_slider)
        buttons = QHBoxLayout()
        buttons.addWidget(self.submit_btn)
        buttons.addWidget(self.reset_btn)
        root = QVBoxLayout(self)
        root.addLayout(form)
        root.addWidget(self.agree)
        root.addLayout(buttons)
        root.addWidget(self.result)

        # --- З'єднання сигнал–слот ---
        # 1) вбудований сигнал + звичайна функція як слот
        self.name_edit.textChanged.connect(
            lambda text: count_chars(self.chars_label, text))
        # 2) вбудований сигнал + лямбда: змінює текст іншого віджета
        self.level_slider.valueChanged.connect(
            lambda v: self.level_label.setText(f"Рівень: {v}"))
        # 3) стан прапорця → активація кнопки (властивість іншого віджета)
        self.agree.toggled.connect(self.submit_btn.setEnabled)
        # 4) кнопка «Підтвердити» — метод класу
        self.submit_btn.clicked.connect(self.on_submit)
        # 5) кнопка «Скинути»
        self.reset_btn.clicked.connect(self.reset_form)

    def on_submit(self):
        errors = validate(self.name_edit.text(), self.age_spin.value(),
                          self.country.currentIndex())
        if errors:
            self.result.setStyleSheet("color: #c0392b;")
            self.result.setText("Помилки:\n• " + "\n• ".join(errors))
            QMessageBox.warning(self, "Некоректні дані", "\n".join(errors))
        else:
            self.result.setStyleSheet("color: #27ae60;")
            self.result.setText(
                f"Збережено: {self.name_edit.text().strip()}, "
                f"{self.age_spin.value()} р., {self.country.currentText()}, "
                f"рівень {self.level_slider.value()}.")

    def reset_form(self):
        self.name_edit.clear()
        self.age_spin.setValue(18)
        self.country.setCurrentIndex(0)
        self.level_slider.setValue(5)
        self.agree.setChecked(False)  # заодно вимкне кнопку підтвердження
        self.result.setStyleSheet("")
        self.result.clear()


# ======================================================================
# ЗАВДАННЯ 3
# ======================================================================

class Task3Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Завдання 3 — Текстовий редактор")
        self.resize(700, 480)

     
        self.text = QTextEdit()
        self.setCentralWidget(self.text)

     
        self.act_new = QAction("Новий", self)
        self.act_new.setShortcut(QKeySequence.StandardKey.New)  
        self.act_new.setStatusTip("Очистити документ")
        self.act_new.triggered.connect(self.new_file)

        self.act_open = QAction("Відкрити...", self)
        self.act_open.setShortcut(QKeySequence.StandardKey.Open)  
        self.act_open.setStatusTip("Відкрити текстовий файл")
        self.act_open.triggered.connect(self.open_file)

        self.act_save = QAction("Зберегти як...", self)
        self.act_save.setShortcut(QKeySequence.StandardKey.Save)  
        self.act_save.setStatusTip("Зберегти у файл")
        self.act_save.triggered.connect(self.save_file)

        self.act_exit = QAction("Вихід", self)
        self.act_exit.setShortcut("Ctrl+Q")
        self.act_exit.triggered.connect(self.close)

        self.act_about = QAction("Про програму", self)
        self.act_about.setShortcut("F1")
        self.act_about.triggered.connect(self.about)

        self.act_about_qt = QAction("Про Qt", self)
        self.act_about_qt.triggered.connect(
            lambda: QMessageBox.aboutQt(self))

       
        file_menu = self.menuBar().addMenu("&Файл")
        file_menu.addActions([self.act_new, self.act_open, self.act_save])
        file_menu.addSeparator()
        file_menu.addAction(self.act_exit)
        help_menu = self.menuBar().addMenu("&Довідка")
        help_menu.addActions([self.act_about, self.act_about_qt])

      
        toolbar = QToolBar("Основна")
        self.addToolBar(toolbar)
        toolbar.addActions([self.act_new, self.act_open, self.act_save])
        toolbar.addSeparator()
        toolbar.addAction(self.act_about)

       
        self.counter = QLabel("Символів: 0 | Слів: 0")
        self.statusBar().addPermanentWidget(self.counter)
        self.statusBar().showMessage("Готово", 3000)
        self.text.textChanged.connect(self.update_counter)

    def update_counter(self):
        t = self.text.toPlainText()
        self.counter.setText(f"Символів: {len(t)} | Слів: {len(t.split())}")

    def new_file(self):
        self.text.clear()
        self.statusBar().showMessage("Створено новий документ", 3000)

    def open_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Відкрити файл", "", "Текстові файли (*.txt);;Усі файли (*)")
        if not path:
            self.statusBar().showMessage("Відкриття скасовано", 3000)
            return
        try:
            with open(path, encoding="utf-8") as f:
                self.text.setPlainText(f.read())
            self.statusBar().showMessage(f"Відкрито: {path}", 5000)
        except (OSError, UnicodeDecodeError) as e:
            QMessageBox.critical(self, "Помилка", f"Не вдалося відкрити файл:\n{e}")

    def save_file(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Зберегти файл", "", "Текстові файли (*.txt)")
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self.text.toPlainText())
            self.statusBar().showMessage(f"Збережено: {path}", 5000)
        except OSError as e:
            QMessageBox.critical(self, "Помилка", f"Не вдалося зберегти:\n{e}")

    def about(self):
        QMessageBox.about(self, "Про програму",
                          "Простий текстовий редактор\nЛабораторна робота, PyQt6")


# ======================================================================
# ЗАВДАННЯ 4
# ======================================================================

class InputPanel(QWidget):
    
    item_added = pyqtSignal(str, int)

    def __init__(self):
        super().__init__()
        self.edit = QLineEdit()
        self.edit.setPlaceholderText("Нове завдання")
        self.prio = QSpinBox()
        self.prio.setRange(1, 5)
        self.btn = QPushButton("Додати")
        row = QHBoxLayout(self)
        row.addWidget(self.edit, 1)
        row.addWidget(QLabel("Пріоритет:"))
        row.addWidget(self.prio)
        row.addWidget(self.btn)
        self.btn.clicked.connect(self._emit)
        self.edit.returnPressed.connect(self._emit)

    def _emit(self):
        text = self.edit.text().strip()
        if text:
            self.item_added.emit(text, self.prio.value())
            self.edit.clear()


class FilterPanel(QWidget):
    
    filter_changed = pyqtSignal(str, int)

    def __init__(self):
        super().__init__()
        self.text = QLineEdit()
        self.text.setPlaceholderText("Пошук...")
        self.min_prio = QSpinBox()
        self.min_prio.setRange(1, 5)
        self.reset_btn = QPushButton("Скинути фільтр")
        row = QHBoxLayout(self)
        row.addWidget(self.text, 1)
        row.addWidget(QLabel("Мін. пріоритет:"))
        row.addWidget(self.min_prio)
        row.addWidget(self.reset_btn)
        self.text.textChanged.connect(self._emit)
        self.min_prio.valueChanged.connect(self._emit)
        self.reset_btn.clicked.connect(self.reset)

    def _emit(self, *_):
        self.filter_changed.emit(self.text.text(), self.min_prio.value())

    def reset(self):
        """Програмне скидання: blockSignals запобігає двом каскадним
        емітам (від text і від min_prio); замість них — один явний."""
        for w in (self.text, self.min_prio):
            w.blockSignals(True)
        self.text.clear()
        self.min_prio.setValue(1)
        for w in (self.text, self.min_prio):
            w.blockSignals(False)
        self._emit()


class ListPanel(QWidget):
    
    count_changed = pyqtSignal(int, int)

    def __init__(self):
        super().__init__()
        self._items: list[tuple[str, int]] = []
        self._text, self._min = "", 1
        self.view = QListWidget()
        QVBoxLayout(self).addWidget(self.view)

    def add_item(self, text: str, prio: int):
        self._items.append((text, prio))
        self._refresh()

    def apply_filter(self, text: str, min_prio: int):
        self._text, self._min = text.lower(), min_prio
        self._refresh()

    def _refresh(self):
        self.view.clear()
        for text, prio in self._items:
            if self._text in text.lower() and prio >= self._min:
                self.view.addItem(f"[{prio}] {text}")
        self.count_changed.emit(self.view.count(), len(self._items))


class Task4Window(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Завдання 4 — Кастомні сигнали")
        self.resize(600, 450)

        self.input_panel = InputPanel()
        self.filter_panel = FilterPanel()
        self.list_panel = ListPanel()

        self.live_check = QCheckBox("Живий фільтр (connect/disconnect)")
        self.apply_btn = QPushButton("Застосувати фільтр")
        self.count_label = QLabel("Показано: 0 з 0")
        self.log_label = QLabel("Остання подія: —")

        self._last_filter = ("", 1)
        self._live = False

        f_box = QGroupBox("Фільтр")
        QVBoxLayout(f_box).addWidget(self.filter_panel)
        i_box = QGroupBox("Додавання")
        QVBoxLayout(i_box).addWidget(self.input_panel)
        ctl = QHBoxLayout()
        ctl.addWidget(self.live_check)
        ctl.addWidget(self.apply_btn)
        root = QVBoxLayout(self)
        root.addWidget(i_box)
        root.addWidget(f_box)
        root.addLayout(ctl)
        root.addWidget(self.list_panel, 1)
        root.addWidget(self.count_label)
        root.addWidget(self.log_label)

       
        self.input_panel.item_added.connect(self.list_panel.add_item)
        self.input_panel.item_added.connect(
            lambda t, p: self.log_label.setText(
                f"Остання подія: item_added('{t}', {p})"))
        self.filter_panel.filter_changed.connect(self._remember_filter)
        self.list_panel.count_changed.connect(
            lambda shown, total: self.count_label.setText(
                f"Показано: {shown} з {total}"))
        self.live_check.toggled.connect(self.set_live)
        self.apply_btn.clicked.connect(
            lambda: self.list_panel.apply_filter(*self._last_filter))

    def _remember_filter(self, text: str, prio: int):
        self._last_filter = (text, prio)
        self.log_label.setText(
            f"Остання подія: filter_changed('{text}', {prio})")

    def set_live(self, on: bool):
        """Вмикає/вимикає автоматичне застосування фільтра через
        connect/disconnect. У вимкненому стані фільтр застосовується
        лише кнопкою."""
        if on and not self._live:
            self.filter_panel.filter_changed.connect(
                self.list_panel.apply_filter)
            self.list_panel.apply_filter(*self._last_filter)
            self._live = True
        elif not on and self._live:
            self.filter_panel.filter_changed.disconnect(
                self.list_panel.apply_filter)
            self._live = False
        self.apply_btn.setEnabled(not on)


# ======================================================================
# ЗАВДАННЯ 5
# ======================================================================

STYLE = """
QWidget {
    background-color: #f4f6fb;
    font-family: "Segoe UI", "Ubuntu", sans-serif;
    font-size: 14px;
}
QLabel { color: #2c3e50; }
QLabel#titleLabel {
    font-size: 22px;
    font-weight: bold;
    color: #1a5276;
    padding: 6px 0;
}
QLineEdit, QSpinBox {
    background: white;
    border: 2px solid #bdc3c7;
    border-radius: 6px;
    padding: 5px;
}
QLineEdit:focus, QSpinBox:focus { border-color: #3498db; }
QListWidget {
    background: white;
    border: 2px solid #d5d8dc;
    border-radius: 8px;
}
QListWidget::item { padding: 6px; }
QListWidget::item:selected { background: #aed6f1; color: #1b2631; }
QPushButton {
    background-color: #3498db;
    color: white;
    border: none;
    border-radius: 6px;
    padding: 8px 16px;
}
QPushButton:hover { background-color: #2e86c1; }
QPushButton:pressed { background-color: #21618c; }
QPushButton:disabled { background-color: #d0d3d4; color: #7f8c8d; }
QPushButton#dangerButton { background-color: #e74c3c; }
QPushButton#dangerButton:hover { background-color: #cb4335; }
QPushButton#dangerButton:pressed { background-color: #922b21; }
"""


class ContactDialog(QDialog):
    """Власний модальний діалог: ім'я, email, вік."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Новий контакт")
        self.setModal(True)

        self.name = QLineEdit()
        self.name.setPlaceholderText("Ім'я")
        self.email = QLineEdit()
        self.email.setPlaceholderText("name@example.com")
        self.age = QSpinBox()
        self.age.setRange(1, 120)
        self.age.setValue(20)
        self.error = QLabel("")
        self.error.setStyleSheet("color: #c0392b;")  

        form = QFormLayout()
        form.addRow("Ім'я:", self.name)
        form.addRow("Email:", self.email)
        form.addRow("Вік:", self.age)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.try_accept)
        buttons.rejected.connect(self.reject)

        root = QVBoxLayout(self)
        root.addLayout(form)
        root.addWidget(self.error)
        root.addWidget(buttons)

    def try_accept(self):
        if not self.name.text().strip():
            self.error.setText("Введіть ім'я.")
        elif "@" not in self.email.text():
            self.error.setText("Некоректний email.")
        else:
            self.accept()

    def data(self) -> dict:
        return {"name": self.name.text().strip(),
                "email": self.email.text().strip(),
                "age": self.age.value()}


class Task5Window(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Завдання 5 — Діалоги та QSS")
        self.resize(480, 420)

        self.title = QLabel("Мої контакти")
        self.title.setObjectName("titleLabel")
        self.list = QListWidget()
        self.add_btn = QPushButton("Додати контакт...")
        self.rename_btn = QPushButton("Змінити назву...")
        self.clear_btn = QPushButton("Очистити список")
        self.clear_btn.setObjectName("dangerButton")
        self.clear_btn.setEnabled(False)  

        row = QHBoxLayout()
        row.addWidget(self.add_btn)
        row.addWidget(self.rename_btn)
        row.addWidget(self.clear_btn)
        root = QVBoxLayout(self)
        root.addWidget(self.title)
        root.addWidget(self.list, 1)
        root.addLayout(row)

        self.add_btn.clicked.connect(self.add_contact)
        self.rename_btn.clicked.connect(self.rename_list)
        self.clear_btn.clicked.connect(self.clear_list)
      
        if "--no-style" not in sys.argv:
            self.setStyleSheet(STYLE)

    def add_contact(self):
        dlg = ContactDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            d = dlg.data()
            self.list.addItem(f"{d['name']} ({d['age']}) — {d['email']}")
            self.clear_btn.setEnabled(True)

    def rename_list(self):
        text, ok = QInputDialog.getText(
            self, "Назва списку", "Нова назва:", text=self.title.text())
        if ok and text.strip():
            self.title.setText(text.strip())

    def clear_list(self):
        answer = QMessageBox.question(
            self, "Підтвердження", "Видалити всі контакти?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No)
        if answer == QMessageBox.StandardButton.Yes:
            self.list.clear()
            self.clear_btn.setEnabled(False)


# ======================================================================
# Запуск: вікно-меню
# ======================================================================

class Launcher(QWidget):
    TASKS = [
        ("Завдання 1 — Віджети та layouts", Task1Window),
        ("Завдання 2 — Форма, сигнали та слоти", Task2Window),
        ("Завдання 3 — QMainWindow (редактор)", Task3Window),
        ("Завдання 4 — Кастомні сигнали", Task4Window),
        ("Завдання 5 — Діалоги та QSS", Task5Window),
    ]

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Лабораторна PyQt6")
        self.setMinimumWidth(340)
        self._windows = []  
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Оберіть завдання:"))
        for title, cls in self.TASKS:
            btn = QPushButton(title)
            btn.clicked.connect(lambda _=False, c=cls: self.open_task(c))
            layout.addWidget(btn)

    def open_task(self, cls):
        w = cls()
        w.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        w.destroyed.connect(lambda _=None, x=w: None)
        self._windows.append(w)
        w.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    launcher = Launcher()
    launcher.show()
    sys.exit(app.exec())


