Overview

Task Manager Pro is a Python-based task management application built using PyQt5. It allows users to add, filter, update, and delete tasks while maintaining an organized workflow.

Features

- Add new tasks with descriptions and priorities
- Mark tasks as completed or incomplete
- Search and filter tasks by priority and status
- Save and load tasks from a JSON file
- Animated UI with a modern dark theme
- Splash screen with a loading bar
- Responsive table for viewing and managing tasks

Installation

Prerequisites

Ensure you have Python installed (Python 3.7+ is recommended). You also need to install the required dependencies:


pip install PyQt5


Running the Application

After installing dependencies, run the script using:

python task_manager.py


Usage Guide

1. Adding a Task:

   - Enter the task description.
   - Select the priority (High, Medium, Low).
   - Click the "Add Task" button.

2. Filtering Tasks:

   - Use the search bar to find tasks.
   - Choose sorting order (by insertion order or priority).
   - Filter tasks by status (All, Completed, Incomplete).

3. Managing Tasks:

   - Double-click the status column to toggle completion.
   - Select tasks and use the "Complete Selected" or "Delete Selected" button.

4. Saving and Loading Tasks:

   - Tasks are saved automatically to `tasks.json` upon closing the application.
   - Tasks are loaded automatically when reopening the application.

 UI and Design

- Dark-themed interface with a modern look.
- Animated buttons and smooth transitions.
- Splash screen with a progress indicator.

 File Structure

```
📁 TaskManagerPro
│-- task_manager.py    # Main application script
│-- tasks.json         # Stores task data
│-- app_icon.png       # Application icon
│-- splash.png         # Splash screen image
```

 Customization

- Modify `apply_styles()` to change colors and fonts.
- Update `splash.png` and `app_icon.png` to use custom images.
- Modify `priority_combo` to add more priority levels.

 Future Enhancements

- Implement notifications for due tasks.
- Add support for task deadlines and reminders.
- Export tasks to CSV or Excel.

 License

This project is open-source under the MIT License.

---

Authors:
Ahmed Al-Amare

Ibrahim BenHalim

Abdelhaseeb ELjamal\
Version:** 1.0.0\


