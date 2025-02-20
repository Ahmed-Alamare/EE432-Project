import sys
import json
from PyQt5.QtCore import (
    Qt, QAbstractTableModel, QPropertyAnimation, QSequentialAnimationGroup,
    pyqtProperty, QObject, QModelIndex, QSize, QUrl, QTimer
)
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QComboBox,
    QCheckBox, QTableView, QHeaderView, QHBoxLayout, QVBoxLayout,
    QRadioButton, QAbstractItemView, QMessageBox, QSplashScreen, QGroupBox,
    QGraphicsOpacityEffect, QStyleFactory, QProgressBar, QStatusBar
)
from PyQt5.QtGui import QFont, QColor, QIcon, QPixmap, QPainter, QLinearGradient


# ====================
# DATA MODELS
# ====================
class Task:
    def __init__(self, description, priority, status=False):
        self.description = description
        self.priority = priority
        self.status = status


class TaskTableModel(QAbstractTableModel):
    def __init__(self, tasks=None):
        super(TaskTableModel, self).__init__()
        self.headers = ['Task', 'Priority', 'Status']
        self.tasks = tasks or []

    def data(self, index, role):
        if not index.isValid():
            return None

        task = self.tasks[index.row()]
        column = index.column()

        if role == Qt.DisplayRole:
            if column == 0:
                return task.description
            elif column == 1:
                return task.priority
            elif column == 2:
                return '✅ Completed' if task.status else '❌ Incomplete'

        if role == Qt.TextAlignmentRole:
            return int(Qt.AlignLeft | Qt.AlignVCenter) if column == 0 else int(Qt.AlignCenter)

        return None

    def setData(self, index, value, role):
        if not index.isValid():
            return False

        task = self.tasks[index.row()]
        column = index.column()

        if role == Qt.EditRole and column == 2:
            task.status = not task.status
            self.dataChanged.emit(index, index, [Qt.DisplayRole])
            return True

        return False

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled

        if index.column() == 2:
            return Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable
        else:
            return Qt.ItemIsSelectable | Qt.ItemIsEnabled

    def rowCount(self, index=QModelIndex()):
        return len(self.tasks)

    def columnCount(self, index=QModelIndex()):
        return 3

    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.headers[section]
        return None

    def addTask(self, task):
        self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount())
        self.tasks.append(task)
        self.endInsertRows()

    def removeTask(self, row):
        self.beginRemoveRows(QModelIndex(), row, row)
        del self.tasks[row]
        self.endRemoveRows()

    def updateData(self, tasks):
        self.beginResetModel()
        self.tasks = tasks
        self.endResetModel()


# ====================
# MAIN APPLICATION
# ====================
class TaskManagerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Task Manager Pro")
        self.resize(1000, 720)
        self.setWindowIcon(QIcon("app_icon.png"))
        self.all_tasks = self.load_tasks()
        self.init_ui()
        self.apply_styles()
        self.setup_animations()
        self.apply_filters()

    def load_tasks(self):
        try:
            with open('tasks.json', 'r') as f:
                data = json.load(f)
                return [Task(t['description'], t['priority'], t['status']) for t in data]
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def save_tasks(self):
        data = [{'description': t.description, 'priority': t.priority, 'status': t.status}
                for t in self.all_tasks]
        with open('tasks.json', 'w') as f:
            json.dump(data, f, indent=4)

    def closeEvent(self, event):
        self.save_tasks()
        event.accept()

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        self.setLayout(main_layout)

        header = QLabel("Task Manager Pro")
        header.setFont(QFont('Segoe UI', 18, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(header)

        input_group = QGroupBox("New Task")
        input_layout = QHBoxLayout()
        input_group.setLayout(input_layout)

        self.task_input = QLineEdit()
        self.task_input.setPlaceholderText("Enter task description...")
        self.priority_combo = QComboBox()
        self.priority_combo.addItems(['🚨 High', '⚠️ Medium', '✅ Low'])

        self.add_button = QPushButton("Add Task")
        self.add_button.clicked.connect(self.add_task)
        self.add_button.setStyleSheet("background-color: #4CAF50; color: white;")

        input_layout.addWidget(self.task_input, 60)
        input_layout.addWidget(self.priority_combo, 20)
        input_layout.addWidget(self.add_button, 20)
        main_layout.addWidget(input_group)

        control_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search tasks...")
        self.search_input.textChanged.connect(self.apply_filters)

        filter_group = QGroupBox("Filters")
        filter_layout = QHBoxLayout()
        filter_group.setLayout(filter_layout)

        self.display_mode = QComboBox()
        self.display_mode.addItems(['Insertion Order', 'Priority'])
        self.display_mode.currentIndexChanged.connect(self.apply_filters)

        self.filter_status = QComboBox()
        self.filter_status.addItems(['All Tasks', 'Completed', 'Incomplete'])
        self.filter_status.currentIndexChanged.connect(self.apply_filters)

        # Toggle Complete/Incomplete Button
        self.toggle_status_button = QPushButton("✅ Complete Selected")
        self.toggle_status_button.clicked.connect(self.toggle_selected_tasks_status)
        self.toggle_status_button.setStyleSheet("background-color: #2196F3; color: white;")

        # Delete Button
        self.delete_button = QPushButton("🗑️ Delete Selected")
        self.delete_button.clicked.connect(self.delete_selected_tasks)
        self.delete_button.setStyleSheet("background-color: #FF4444; color: white;")

        filter_layout.addWidget(QLabel("Sort By:"))
        filter_layout.addWidget(self.display_mode)
        filter_layout.addWidget(QLabel("Show:"))
        filter_layout.addWidget(self.filter_status)

        control_layout.addWidget(self.search_input, 50)
        control_layout.addWidget(filter_group, 40)
        control_layout.addWidget(self.toggle_status_button, 10)  # Add Toggle Button
        control_layout.addWidget(self.delete_button, 10)
        main_layout.addLayout(control_layout)

        self.table_model = TaskTableModel(self.all_tasks)
        self.table_view = QTableView()
        self.table_view.setModel(self.table_model)
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_view.verticalHeader().hide()
        self.table_view.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table_view.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.table_view.setAlternatingRowColors(True)
        self.table_view.doubleClicked.connect(self.toggle_task_status)
        self.table_view.selectionModel().selectionChanged.connect(self.update_toggle_button_text)
        main_layout.addWidget(self.table_view)

        self.status_bar = QStatusBar()
        self.task_count_label = QLabel("Total Tasks: 0")
        self.status_bar.addWidget(self.task_count_label)
        main_layout.addWidget(self.status_bar)

    def apply_filters(self):
        search_text = self.search_input.text().lower()
        status_filter = self.filter_status.currentIndex()
        tasks = [task for task in self.all_tasks
                 if search_text in task.description.lower() and
                 (status_filter == 0 or
                  (status_filter == 1 and task.status) or
                  (status_filter == 2 and not task.status))]

        if self.display_mode.currentIndex() == 1:
            priority_order = {'🚨 High': 0, '⚠️ Medium': 1, '✅ Low': 2}
            tasks.sort(key=lambda x: priority_order[x.priority])

        self.table_model.updateData(tasks)
        self.task_count_label.setText(f"Total Tasks: {len(tasks)}")

    def add_task(self):
        description = self.task_input.text().strip()
        if not description:
            QMessageBox.warning(self, "Input Error", "Task description cannot be empty!")
            return

        priority = self.priority_combo.currentText()
        new_task = Task(description, priority)
        self.all_tasks.append(new_task)
        self.apply_filters()
        self.task_input.clear()
        self.add_anim.start()

    def toggle_task_status(self, index):
        if index.column() == 2:
            self.table_model.setData(index, None, Qt.EditRole)

    def update_toggle_button_text(self):
        """Update the toggle button text based on the selected tasks' status."""
        selected = self.table_view.selectionModel().selectedRows()
        if not selected:
            self.toggle_status_button.setText("✅ Complete Selected")
            return

        # Check if all selected tasks are completed
        all_completed = all(self.table_model.tasks[index.row()].status for index in selected)
        self.toggle_status_button.setText("❌ Mark as Incomplete" if all_completed else "✅ Complete Selected")

    def toggle_selected_tasks_status(self):
        """Toggle the status of selected tasks between completed and incomplete."""
        selected = self.table_view.selectionModel().selectedRows()
        if not selected:
            QMessageBox.warning(self, "No Selection", "Please select tasks to toggle status!")
            return

        # Determine the new status based on the current button text
        new_status = self.toggle_status_button.text() == "✅ Complete Selected"

        for index in selected:
            task = self.table_model.tasks[index.row()]
            task.status = new_status

        self.apply_filters()
        self.update_toggle_button_text()

    def delete_selected_tasks(self):
        selected = self.table_view.selectionModel().selectedRows()
        if not selected:
            QMessageBox.warning(self, "No Selection", "Please select tasks to delete!")
            return

        confirm = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Delete {len(selected)} selected task(s)?",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirm == QMessageBox.Yes:
            for index in sorted(selected, reverse=True):
                task = self.table_model.tasks[index.row()]
                if task in self.all_tasks:
                    self.all_tasks.remove(task)
            self.apply_filters()

    def apply_styles(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #2D2D2D;
                color: #FFFFFF;
            }
            QGroupBox {
                border: 1px solid #3E3E3E;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QTableView {
                background-color: #1E1E1E;
                alternate-background-color: #2A2A2A;
                selection-background-color: #3E3E3E;
                border: none;
            }
            QHeaderView::section {
                background-color: #007ACC;
                color: white;
                padding: 5px;
            }
            QLineEdit {
                padding: 5px;
                border: 1px solid #3E3E3E;
                border-radius: 3px;
            }
            QPushButton[text="✅ Complete Selected"], QPushButton[text="❌ Mark as Incomplete"] {
                padding: 5px;
                border-radius: 3px;
                min-width: 120px;
            }
            QPushButton[text="🗑️ Delete Selected"] {
                padding: 5px;
                border-radius: 3px;
                min-width: 120px;
            }
            QTableView::item:selected {
                background-color: #FF4444;
                color: white;
            }
            QProgressBar {
                border: 2px solid #007ACC;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #007ACC;
            }
        """)

    def setup_animations(self):
        self.add_button.setGraphicsEffect(QGraphicsOpacityEffect())
        self.add_anim = QPropertyAnimation(self.add_button.graphicsEffect(), b"opacity")
        self.add_anim.setDuration(1000)
        self.add_anim.setKeyValueAt(0, 1.0)
        self.add_anim.setKeyValueAt(0.5, 0.3)
        self.add_anim.setKeyValueAt(1, 1.0)


# ====================
# SPLASH SCREEN
# ====================
class SplashScreen(QSplashScreen):
    def __init__(self):
        pixmap = QPixmap("splash.png").scaled(600, 400)
        super().__init__(pixmap)
        self.progress = QProgressBar(self)
        self.progress.setGeometry(50, 350, 500, 20)
        self.progress.setStyleSheet("""
            QProgressBar {
                border: 2px solid #007ACC;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #007ACC;
            }
        """)
        self.progress.setValue(0)


def main():
    app = QApplication(sys.argv)
    splash = SplashScreen()
    splash.show()

    # Fixed splash screen progress using QTimer
    timer = QTimer()
    progress = 0

    def update_progress():
        nonlocal progress
        if progress < 100:
            splash.progress.setValue(progress)
            progress += 1
            timer.singleShot(30, update_progress)
        else:
            timer.stop()

    timer.singleShot(0, update_progress)

    window = TaskManagerApp()
    splash.finish(window)
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()