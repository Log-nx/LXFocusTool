#!/usr/bin/env python3
"""
Focus Tool - macOS Edition
A minimalist focus and productivity application for macOS
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
import threading
import time
import logging
from datetime import datetime
import subprocess
import sys

# Set up logging
_env_level = os.getenv('FOCUS_LOG_LEVEL')
if os.getenv('FOCUS_DEBUG', '').strip() in ('1', 'true', 'TRUE') and not _env_level:
    _env_level = 'DEBUG'
_level = getattr(logging, (_env_level or 'INFO').upper(), logging.INFO)
logging.basicConfig(
    level=_level,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('focus_tool.log')
    ]
)
logger = logging.getLogger(__name__)

class CustomButton(tk.Frame):
    """Custom button widget that works on macOS with proper colors"""
    def __init__(self, parent, text="", bg="#4a9eff", fg="white", command=None, **kwargs):
        super().__init__(parent, bg=bg, relief='raised', borderwidth=2, cursor='hand2')
        
        self.command = command
        self.default_bg = bg
        self.hover_bg = self.adjust_color(bg, 1.2)
        self.active_bg = self.adjust_color(bg, 0.8)
        
        # Label inside frame
        self.label = tk.Label(self, text=text, bg=bg, fg=fg,
                            font=("Helvetica Neue", 10, "bold"),
                            padx=20, pady=8)
        self.label.pack(expand=True, fill='both')
        
        # Bind events
        self.bind('<Button-1>', self.on_click)
        self.label.bind('<Button-1>', self.on_click)
        self.bind('<Enter>', self.on_enter)
        self.label.bind('<Enter>', self.on_enter)
        self.bind('<Leave>', self.on_leave)
        self.label.bind('<Leave>', self.on_leave)
    
    def adjust_color(self, hex_color, factor):
        """Lighten or darken a color"""
        try:
            hex_color = hex_color.lstrip('#')
            r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            r = min(255, int(r * factor))
            g = min(255, int(g * factor))
            b = min(255, int(b * factor))
            return f'#{r:02x}{g:02x}{b:02x}'
        except:
            return hex_color
    
    def on_click(self, event):
        self.configure(relief='sunken')
        self.label.configure(bg=self.active_bg)
        self.configure(bg=self.active_bg)
        self.after(100, self.reset_color)
        if self.command:
            self.command()
    
    def on_enter(self, event):
        self.label.configure(bg=self.hover_bg)
        self.configure(bg=self.hover_bg)
    
    def on_leave(self, event):
        self.label.configure(bg=self.default_bg)
        self.configure(bg=self.default_bg)
    
    def reset_color(self):
        self.configure(relief='raised')
        self.label.configure(bg=self.default_bg)
        self.configure(bg=self.default_bg)
    
    def config(self, **kwargs):
        if 'state' in kwargs:
            state = kwargs['state']
            if state == 'disabled':
                self.label.configure(fg='#888888', bg='#2a2a2a')
                self.configure(bg='#2a2a2a')
                self.command = None
            elif state == 'normal':
                self.label.configure(fg='white', bg=self.default_bg)
                self.configure(bg=self.default_bg)
        if 'bg' in kwargs:
            self.default_bg = kwargs['bg']
            self.label.configure(bg=kwargs['bg'])
            self.configure(bg=kwargs['bg'])

class FeatureBox(tk.Frame):
    """Custom frame widget with title bar for organizing features"""
    def __init__(self, parent, title, **kwargs):
        super().__init__(parent, **kwargs)
        self.title = title
        logger.info(f"Creating FeatureBox: {title}")
        self.setup_box()
    
    def setup_box(self):
        # Box styling for macOS
        self.configure(bg='#2d2d2d', relief='flat', borderwidth=0)
        
        # Title bar
        title_frame = tk.Frame(self, bg='#4a9eff', height=28)
        title_frame.pack(fill='x', pady=(0, 1))
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(title_frame, text=self.title, 
                              font=("Helvetica Neue", 10, "bold"),
                              bg='#4a9eff', fg='#ffffff')
        title_label.pack(side='left', padx=12, pady=4)
        
        # Content area
        self.content_frame = tk.Frame(self, bg='#2d2d2d')
        self.content_frame.pack(fill='both', expand=True, padx=1, pady=(0, 1))
        
        logger.info(f"FeatureBox {self.title} setup complete")

class FocusTool:
    def __init__(self, root):
        self.root = root
        self.root.title("Focus Tool - macOS")
        
        logger.info("Initializing FocusTool for macOS")
        
        # macOS fonts
        self.default_font = "Helvetica Neue"
        self.title_font = "Helvetica Neue"
        
        # Setup custom button styles for macOS
        self.setup_button_styles()
        
        # Load saved window size or use default
        self.load_window_config()
        
        self.root.resizable(True, True)
        self.root.minsize(400, 600)
        
        # Set dark theme colors
        self.root.configure(bg='#1e1e1e')
        
        # macOS dock integration
        self.root.lift()
        
        # Center window if no saved position
        if not hasattr(self, 'saved_x') or not hasattr(self, 'saved_y'):
            self.center_window()
        else:
            self.root.geometry(f'{self.saved_width}x{self.saved_height}+{self.saved_x}+{self.saved_y}')
        
        # Initialize data
        self.tasks = []
        self.timer_running = False
        self.time_remaining = 50 * 60
        self.original_time_minutes = 50
        self.timer_thread = None
        
        self.load_tasks()
        self.setup_ui()
        self.update_timer_display()
        
        logger.info("FocusTool initialization complete")
    
    def setup_button_styles(self):
        """Setup custom ttk button styles that work on macOS"""
        style = ttk.Style()
        
        # Define custom button styles with colors
        button_configs = {
            'Cyan.TButton': {'background': '#17a2b8', 'foreground': 'white'},
            'Green.TButton': {'background': '#28a745', 'foreground': 'white'},
            'Orange.TButton': {'background': '#fd7e14', 'foreground': 'white'},
            'Purple.TButton': {'background': '#6f42c1', 'foreground': 'white'},
            'Blue.TButton': {'background': '#4a9eff', 'foreground': 'white'},
            'Red.TButton': {'background': '#dc3545', 'foreground': 'white'},
            'Gray.TButton': {'background': '#6c757d', 'foreground': 'white'},
            'Dark.TButton': {'background': '#3a3a3a', 'foreground': 'white'},
        }
        
        for style_name, colors in button_configs.items():
            style.configure(style_name,
                          background=colors['background'],
                          foreground=colors['foreground'],
                          borderwidth=0,
                          relief='flat',
                          font=(self.default_font, 10, 'bold'))
            style.map(style_name,
                     background=[('active', colors['background']),
                                ('pressed', colors['background'])])
        
        logger.info("Custom button styles configured")
    
    def load_window_config(self):
        """Load saved window configuration"""
        try:
            if os.path.exists('window_config.json'):
                with open('window_config.json', 'r') as f:
                    config = json.load(f)
                    self.saved_width = config.get('width', 450)
                    self.saved_height = config.get('height', 700)
                    self.saved_x = config.get('x', None)
                    self.saved_y = config.get('y', None)
                    logger.info(f"Loaded window config: {self.saved_width}x{self.saved_height}")
                self.root.geometry(f"{self.saved_width}x{self.saved_height}")
            else:
                self.saved_width = 450
                self.saved_height = 700
                self.root.geometry("450x700")
                logger.info("No saved config, using default size")
        except Exception as e:
            logger.error(f"Error loading window config: {e}")
            self.saved_width = 450
            self.saved_height = 700
            self.root.geometry("450x700")
    
    def save_window_config(self):
        """Save current window configuration"""
        try:
            geometry = self.root.geometry()
            
            if 'x' in geometry:
                parts = geometry.split('+')
                size_part = parts[0]
                
                if 'x' in size_part:
                    width, height = map(int, size_part.split('x'))
                    
                    if len(parts) >= 3:
                        x, y = map(int, parts[1:3])
                    else:
                        x = self.root.winfo_x()
                        y = self.root.winfo_y()
                    
                    config = {
                        'width': width,
                        'height': height,
                        'x': x,
                        'y': y
                    }
                    
                    with open('window_config.json', 'w') as f:
                        json.dump(config, f, indent=2)
                    
                    logger.debug(f"Window config saved: {width}x{height} at ({x}, {y})")
                
        except Exception as e:
            logger.error(f"Error saving window config: {e}")
    
    def center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        logger.info(f"Window centered at ({x}, {y}) with size {width}x{height}")
    
    def setup_ui(self):
        logger.info("Setting up macOS UI")
        
        # Color scheme
        bg_color = '#1e1e1e'
        
        # Main container with scrollbar
        container = tk.Frame(self.root, bg=bg_color)
        container.pack(fill='both', expand=True)
        
        # Scrollbar
        scrollbar = tk.Scrollbar(container)
        scrollbar.pack(side='right', fill='y')
        
        # Canvas for scrolling
        canvas = tk.Canvas(container, bg=bg_color, highlightthickness=0, yscrollcommand=scrollbar.set)
        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=canvas.yview)
        
        # Main frame inside canvas
        main_frame = tk.Frame(canvas, bg=bg_color, padx=20, pady=20)
        canvas_window = canvas.create_window((0, 0), window=main_frame, anchor='nw')
        
        # Configure scrolling
        def configure_scroll(event=None):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.itemconfig(canvas_window, width=canvas.winfo_width())
        
        main_frame.bind('<Configure>', configure_scroll)
        canvas.bind('<Configure>', configure_scroll)
        
        # Bind mouse wheel
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", on_mousewheel)
        
        logger.info("Main frame created")
        
        # Timer Feature Box
        self.timer_box = FeatureBox(main_frame, "Timer")
        self.timer_box.pack(fill='x', pady=(0, 20))
        self.setup_timer_section()
        
        # Task Management Feature Box
        self.task_box = FeatureBox(main_frame, "Task Management")
        self.task_box.pack(fill='both', expand=True, pady=(0, 20))
        self.setup_task_section()
        
        # Quick Launch Feature Box
        self.app_box = FeatureBox(main_frame, "Quick Launch")
        self.app_box.pack(fill='x', pady=(0, 20))
        self.setup_app_section()
        
        # Status bar
        status_frame = tk.Frame(main_frame, bg=bg_color)
        status_frame.pack(fill='x', pady=(20, 0))
        
        status_label = tk.Label(status_frame, text="Ready to focus!", 
                               font=(self.default_font, 9),
                               bg=bg_color, fg='#ffffff',
                               anchor='center')
        status_label.pack(fill='x')
        
        self.refresh_task_list()
        
        logger.info("macOS UI setup complete")
    
    def setup_timer_section(self):
        logger.info("Setting up timer section")
        content = self.timer_box.content_frame
        
        # Timer display - use lighter background for better visibility on macOS
        timer_display_frame = tk.Frame(content, bg='#2d2d2d')
        timer_display_frame.pack(pady=(25, 25))
        
        self.timer_label = tk.Label(timer_display_frame, text="50:00", 
                                   font=(self.title_font, 42, "bold"), 
                                   bg='#2d2d2d', fg='#4a9eff')
        self.timer_label.pack(pady=10)
        
        # Timer preset buttons
        time_select_frame = tk.Frame(content, bg='#2d2d2d')
        time_select_frame.pack(pady=(0, 20))
        
        preset_frame = tk.Frame(time_select_frame, bg='#2d2d2d')
        preset_frame.pack()
        
        CustomButton(preset_frame, text="20m", bg='#17a2b8', 
                    command=lambda: self.set_timer(20)).pack(side='left', padx=(0, 10))
        
        CustomButton(preset_frame, text="50m", bg='#28a745',
                    command=lambda: self.set_timer(50)).pack(side='left', padx=(0, 10))
        
        CustomButton(preset_frame, text="120m", bg='#fd7e14',
                    command=lambda: self.set_timer(120)).pack(side='left', padx=(0, 10))
        
        CustomButton(preset_frame, text="Custom", bg='#6f42c1',
                    command=self.set_custom_timer).pack(side='left', padx=(0, 10))
        
        # Timer control buttons
        button_frame = tk.Frame(content, bg='#2d2d2d')
        button_frame.pack(pady=(0, 25))
        
        top_button_frame = tk.Frame(button_frame, bg='#2d2d2d')
        top_button_frame.pack()
        
        self.start_button = CustomButton(top_button_frame, text="Start", 
                                        bg='#4a9eff', command=self.start_timer)
        self.start_button.pack(side='left', padx=(0, 15))
        
        self.stop_button = CustomButton(top_button_frame, text="Stop", 
                                        bg='#dc3545', command=self.stop_timer)
        self.stop_button.config(state='disabled')
        self.stop_button.pack(side='left', padx=(15, 0))
        
        self.reset_button = CustomButton(button_frame, text="Reset", 
                                         bg='#6c757d', command=self.reset_timer)
        self.reset_button.pack(pady=(20, 0))
        
        logger.info("Timer section setup complete")
    
    def setup_task_section(self):
        logger.info("Setting up task section")
        content = self.task_box.content_frame
        
        # Task input
        input_frame = tk.Frame(content, bg='#2d2d2d')
        input_frame.pack(fill='x', padx=20, pady=(20, 15))
        
        # Entry with better macOS visibility
        self.task_entry = tk.Entry(input_frame, 
                                  font=(self.default_font, 10),
                                  bg='#ffffff', fg='#000000',
                                  insertbackground='#000000',
                                  relief='solid', borderwidth=1,
                                  highlightthickness=1,
                                  highlightbackground='#4a9eff',
                                  highlightcolor='#4a9eff')
        self.task_entry.pack(side='left', fill='x', expand=True, padx=(0, 15))
        self.task_entry.bind('<Return>', lambda e: self.add_task())
        
        CustomButton(input_frame, text="Add Task", 
                     bg='#4a9eff', command=self.add_task).pack(side='right')
        
        # Task list
        list_frame = tk.Frame(content, bg='#2d2d2d')
        list_frame.pack(fill='both', expand=True, padx=20, pady=(0, 15))
        
        # Listbox with better macOS visibility - use light background
        self.task_listbox = tk.Listbox(list_frame, 
                                       font=(self.default_font, 9),
                                       bg='#f5f5f5', fg='#000000',
                                       selectbackground='#4a9eff',
                                       selectforeground='#ffffff',
                                       relief='solid', borderwidth=1,
                                       highlightthickness=1,
                                       highlightbackground='#4a9eff',
                                       highlightcolor='#4a9eff')
        self.task_listbox.pack(fill='both', expand=True)
        
        # Task action buttons
        button_frame = tk.Frame(content, bg='#2d2d2d')
        button_frame.pack(pady=(0, 20))
        
        top_button_frame = tk.Frame(button_frame, bg='#2d2d2d')
        top_button_frame.pack()
        
        CustomButton(top_button_frame, text="Complete", 
                     bg='#28a745', command=self.complete_task).pack(side='left', padx=(0, 15))
        
        CustomButton(top_button_frame, text="Delete", 
                     bg='#dc3545', command=self.delete_task).pack(side='left', padx=(15, 0))
        
        CustomButton(button_frame, text="Clear All", 
                     bg='#6c757d', command=self.clear_tasks).pack(pady=(15, 0))
        
        logger.info("Task section setup complete")
    
    def setup_app_section(self):
        logger.info("Setting up app section")
        content = self.app_box.content_frame
        
        # App input
        input_frame = tk.Frame(content, bg='#2d2d2d')
        input_frame.pack(fill='x', padx=20, pady=(20, 15))
        
        # Entry with better macOS visibility
        self.app_entry = tk.Entry(input_frame, 
                                 font=(self.default_font, 10),
                                 bg='#ffffff', fg='#000000',
                                 insertbackground='#000000',
                                 relief='solid', borderwidth=1,
                                 highlightthickness=1,
                                 highlightbackground='#4a9eff',
                                 highlightcolor='#4a9eff')
        self.app_entry.pack(side='left', fill='x', expand=True, padx=(0, 15))
        self.app_entry.insert(0, "TextEdit")
        
        CustomButton(input_frame, text="Launch App", 
                     bg='#4a9eff', command=self.launch_app).pack(side='right')
        
        CustomButton(content, text="Browse Files", 
                     bg='#17a2b8', command=self.browse_app).pack(pady=(0, 20))
        
        logger.info("App section setup complete")
    
    # Timer Methods
    def start_timer(self):
        if not self.timer_running:
            logger.info("Starting timer")
            self.timer_running = True
            self.start_button.config(state="disabled")
            self.stop_button.config(state="normal")
            self.timer_thread = threading.Thread(target=self.timer_loop, daemon=True)
            self.timer_thread.start()
    
    def stop_timer(self):
        logger.info("Stopping timer")
        self.timer_running = False
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")
    
    def set_timer(self, minutes):
        logger.info(f"Setting timer to {minutes} minutes")
        self.stop_timer()
        self.time_remaining = minutes * 60
        self.original_time_minutes = minutes
        self.update_timer_display()
    
    def set_custom_timer(self):
        logger.info("Opening custom timer dialog")
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Custom Timer")
        dialog.geometry("300x150")
        dialog.configure(bg='#2d2d2d')
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        
        dialog.geometry("+%d+%d" % (self.root.winfo_rootx() + 75, self.root.winfo_rooty() + 275))
        
        input_frame = tk.Frame(dialog, bg='#2d2d2d')
        input_frame.pack(pady=20)
        
        tk.Label(input_frame, text="Enter minutes:", 
                font=(self.default_font, 10), bg='#2d2d2d', fg='#ffffff').pack()
        
        time_entry = tk.Entry(input_frame, font=(self.default_font, 12), width=10)
        time_entry.pack(pady=10)
        time_entry.focus()
        time_entry.bind('<Return>', lambda e: self.apply_custom_timer(dialog, time_entry))
        
        button_frame = tk.Frame(dialog, bg='#2d2d2d')
        button_frame.pack(pady=10)
        
        CustomButton(button_frame, text="Set", 
                     bg='#4a9eff',
                     command=lambda: self.apply_custom_timer(dialog, time_entry)).pack(side='left', padx=(0, 10))
        
        CustomButton(button_frame, text="Cancel", 
                     bg='#6c757d',
                     command=dialog.destroy).pack(side='left')
    
    def apply_custom_timer(self, dialog, time_entry):
        try:
            minutes = int(time_entry.get().strip())
            if minutes > 0 and minutes <= 1440:
                logger.info(f"Setting custom timer to {minutes} minutes")
                self.stop_timer()
                self.time_remaining = minutes * 60
                self.original_time_minutes = minutes
                self.update_timer_display()
                dialog.destroy()
            else:
                messagebox.showerror("Invalid Time", "Please enter a time between 1 and 1440 minutes (24 hours)")
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid number of minutes")
    
    def reset_timer(self):
        logger.info("Resetting timer")
        self.stop_timer()
        self.time_remaining = 50 * 60
        self.original_time_minutes = 50
        self.update_timer_display()
    
    def timer_loop(self):
        logger.info("Timer loop started")
        while self.timer_running and self.time_remaining > 0:
            time.sleep(1)
            self.time_remaining -= 1
            self.root.after(0, self.update_timer_display)
            
            if self.time_remaining <= 0:
                self.root.after(0, self.timer_complete)
                break
        logger.info("Timer loop ended")
    
    def update_timer_display(self):
        minutes = self.time_remaining // 60
        seconds = self.time_remaining % 60
        self.timer_label.config(text=f"{minutes:02d}:{seconds:02d}")
    
    def timer_complete(self):
        logger.info("Timer completed")
        self.timer_running = False
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")
        
        messagebox.showinfo("Timer Complete", f"{self.original_time_minutes}-minute focus session completed!")
        
        self.time_remaining = 50 * 60
        self.original_time_minutes = 50
        self.update_timer_display()
    
    # Task Methods
    def add_task(self):
        task_text = self.task_entry.get().strip()
        if task_text:
            logger.info(f"Adding task: {task_text}")
            task = {
                'text': task_text,
                'created': datetime.now().isoformat(),
                'completed': False
            }
            self.tasks.append(task)
            self.task_entry.delete(0, tk.END)
            self.refresh_task_list()
            self.save_tasks()
    
    def complete_task(self):
        selection = self.task_listbox.curselection()
        if selection:
            index = selection[0]
            if index < len(self.tasks):
                self.tasks[index]['completed'] = not self.tasks[index]['completed']
                self.refresh_task_list()
                self.save_tasks()
    
    def delete_task(self):
        selection = self.task_listbox.curselection()
        if selection:
            index = selection[0]
            if index < len(self.tasks):
                logger.info(f"Deleting task: {self.tasks[index]['text']}")
                del self.tasks[index]
                self.refresh_task_list()
                self.save_tasks()
    
    def clear_tasks(self):
        logger.info("Clearing all tasks")
        if messagebox.askyesno("Clear Tasks", "Are you sure you want to clear all tasks?"):
            self.tasks = []
            self.refresh_task_list()
            self.save_tasks()
    
    def refresh_task_list(self):
        logger.debug(f"Refreshing task list with {len(self.tasks)} tasks")
        self.task_listbox.delete(0, tk.END)
        for i, task in enumerate(self.tasks):
            status = "✓ " if task['completed'] else "□ "
            display_text = f"{status}{task['text']}"
            self.task_listbox.insert(tk.END, display_text)
            if task['completed']:
                self.task_listbox.itemconfig(i, fg='#28a745')
    
    # App Launcher Methods
    def launch_app(self):
        app_name = self.app_entry.get().strip()
        if app_name:
            logger.info(f"Launching application: {app_name}")
            try:
                subprocess.Popen(['open', '-a', app_name])
                logger.info(f"Successfully launched {app_name}")
            except Exception as e:
                logger.error(f"Failed to launch {app_name}: {str(e)}")
                messagebox.showerror("Error", f"Could not launch {app_name}: {str(e)}")
    
    def browse_app(self):
        logger.info("Opening file browser")
        filename = filedialog.askopenfilename(
            title="Select Application",
            filetypes=[("Applications", "*.app"), ("All files", "*.*")],
            initialdir="/Applications"
        )
        if filename:
            logger.info(f"Selected file: {filename}")
            self.app_entry.delete(0, tk.END)
            self.app_entry.insert(0, filename)
    
    # Data Persistence Methods
    def save_tasks(self):
        try:
            with open('tasks.json', 'w') as f:
                json.dump(self.tasks, f, indent=2)
            logger.debug(f"Saved {len(self.tasks)} tasks to file")
        except Exception as e:
            logger.error(f"Error saving tasks: {e}")
    
    def load_tasks(self):
        try:
            if os.path.exists('tasks.json'):
                with open('tasks.json', 'r') as f:
                    self.tasks = json.load(f)
                logger.info(f"Loaded {len(self.tasks)} tasks from file")
            else:
                logger.info("No tasks file found, starting with empty task list")
        except Exception as e:
            logger.error(f"Error loading tasks: {e}")
            self.tasks = []

def main():
    try:
        logger.info("Starting Focus Tool application for macOS")
        root = tk.Tk()
        app = FocusTool(root)
        
        def on_closing():
            logger.info("Application closing")
            try:
                app.save_tasks()
                app.save_window_config()
            except Exception as e:
                logger.error(f"Error during cleanup: {e}")
            finally:
                root.destroy()
        
        root.protocol("WM_DELETE_WINDOW", on_closing)
        logger.info("Entering main loop")
        root.mainloop()
        logger.info("Application closed")
        
    except Exception as e:
        logger.error(f"Critical error in main: {e}")
        import traceback
        traceback.print_exc()
        print(f"\nCritical error: {e}")
        print("Press Enter to exit...")
        input()
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\nFatal error: {e}")
        import traceback
        traceback.print_exc()
        print("\nPress Enter to exit...")
        input()
        sys.exit(1)
