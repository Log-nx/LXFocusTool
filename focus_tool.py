import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
import threading
import time
import random
import logging
from datetime import datetime, timedelta
import subprocess
import sys
import math # Added for math.sin and math.cos
import ctypes

# Set up logging (default INFO; enable DEBUG with env FOCUS_DEBUG=1 or FOCUS_LOG_LEVEL=DEBUG)
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

class HexagonGrid:
    def __init__(self, x, y, size):
        self.x = x
        self.y = y
        self.size = size

class StaticHexagonBackground(tk.Canvas):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.hexagons = []
        self.grid_spacing = 40  # Spacing between hexagons
        self.hexagon_size = 8   # Size of each hexagon
        logger.info("Initializing StaticHexagonBackground with hexagon grid")
        self.setup_background()
    
    def setup_background(self):
        self.configure(bg='#1e1e1e', highlightthickness=0)
        self.bind('<Configure>', self.on_resize)
        self.create_hexagon_grid()
        logger.info("Static hexagon grid background setup complete")
    
    def create_hexagon_grid(self):
        # Get actual canvas dimensions, with fallback to default
        canvas_width = self.winfo_width() or 410
        canvas_height = self.winfo_height() or 660
        
        # Ensure we have valid dimensions
        if canvas_width < 10 or canvas_height < 10:
            canvas_width = 410
            canvas_height = 660
        
        self.hexagons = []
        
        # Create a regular grid of hexagons
        for y in range(0, canvas_height + self.grid_spacing, self.grid_spacing):
            for x in range(0, canvas_width + self.grid_spacing, self.grid_spacing):
                # Offset every other row for proper hexagon grid
                offset_x = x + (self.grid_spacing // 2) if (y // self.grid_spacing) % 2 == 1 else x
                hexagon = HexagonGrid(offset_x, y, self.hexagon_size)
                self.hexagons.append(hexagon)
        
        # Draw all hexagons immediately
        self.draw_all_hexagons()
        logger.info(f"Created and drew {len(self.hexagons)} hexagons in grid pattern")
    
    def on_resize(self, event):
        if event.width > 1 and event.height > 1:
            # Only redraw if the size actually changed significantly
            current_width = self.winfo_width()
            current_height = self.winfo_height()
            
            # Check if we need to redraw (avoid excessive redrawing)
            if (abs(current_width - event.width) > 10 or 
                abs(current_height - event.height) > 10):
                # Clear existing hexagons and redraw
                self.delete("hexagon")
                # Small delay to ensure canvas is properly sized
                self.after(50, self.create_hexagon_grid)
    
    def draw_hexagon(self, x, y, size):
        """Draw a hexagon at the given position with the given size"""
        try:
            # Validate coordinates and size
            if not (isinstance(x, (int, float)) and isinstance(y, (int, float)) and isinstance(size, (int, float))):
                return
            if size <= 0:
                return
            
            # Calculate hexagon points
            points = []
            for i in range(6):
                angle = i * 3.14159 / 3
                px = x + size * math.cos(angle)
                py = y + size * math.sin(angle)
                points.extend([px, py])
            
            # Use dark grey color for static grid
            color = '#404040'  # Dark grey
            self.create_polygon(
                points,
                fill='',
                outline=color,
                width=1,
                tags="hexagon"
            )
        except Exception as e:
            # Reduced logging for better performance
            pass
    
    def draw_all_hexagons(self):
        """Draw all hexagons in the grid"""
        for hexagon in self.hexagons:
            self.draw_hexagon(hexagon.x, hexagon.y, hexagon.size)



class FeatureBox(tk.Frame):
    def __init__(self, parent, title, **kwargs):
        super().__init__(parent, **kwargs)
        self.title = title
        logger.info(f"Creating FeatureBox: {title}")
        self.setup_box()
    
    def setup_box(self):
        # Box styling with glass effect
        self.configure(bg='#2d2d2d', relief='flat', borderwidth=0)
        
        # Title bar with glass accent
        title_frame = tk.Frame(self, bg='#4a9eff', height=28)
        title_frame.pack(fill='x', pady=(0, 1))
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(title_frame, text=self.title, 
                              font=("Segoe UI", 9, "bold"),
                              bg='#4a9eff', fg='#ffffff')
        title_label.pack(side='left', padx=12, pady=4)
        
        # Content area with glass background
        self.content_frame = tk.Frame(self, bg='#2d2d2d')
        self.content_frame.pack(fill='both', expand=True, padx=1, pady=(0, 1))
        
        logger.info(f"FeatureBox {self.title} setup complete")

class FocusTool:
    def __init__(self, root):
        self.root = root
        self.root.title("Focus Tool")
        
        # Load saved window size or use default
        self.load_window_config()
        
        self.root.resizable(True, True)
        self.root.minsize(400, 600)
        
        logger.info("Initializing FocusTool")
        
        # Set window properties for modern look while maintaining taskbar presence
        self.root.attributes('-alpha', 0.95)
        self.root.configure(bg='#1e1e1e')
        
        # Keep Windows native title bar for proper taskbar presence
        self.root.title("Focus Tool")
        
        # Ensure the window appears in the taskbar and Alt+Tab switcher
        self.ensure_taskbar_presence()
        
        # Center the window on screen (only if no saved position)
        if not hasattr(self, 'saved_x') or not hasattr(self, 'saved_y'):
            self.center_window()
        else:
            # Use saved position
            self.root.geometry(f'{self.saved_width}x{self.saved_height}+{self.saved_x}+{self.saved_y}')
        
        self.tasks = []
        self.timer_running = False
        self.time_remaining = 50 * 60
        self.original_time_minutes = 50  # Store original time for completion message
        self.timer_thread = None
        
        self.load_tasks()
        self.setup_ui()
        self.update_timer_display()
        
        # No need for delayed Windows setup since we're keeping native title bar
        
        logger.info("FocusTool initialization complete")
    
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
                # Set initial geometry
                self.root.geometry(f"{self.saved_width}x{self.saved_height}")
            else:
                # Default size
                self.saved_width = 450
                self.saved_height = 700
                self.root.geometry("450x700")
                logger.info("No saved config, using default size")
        except Exception as e:
            logger.error(f"Error loading window config: {e}")
            # Fallback to default
            self.saved_width = 450
            self.saved_height = 700
            self.root.geometry("450x700")
    
    def save_window_config(self):
        """Save current window configuration"""
        try:
            # Get current window state
            geometry = self.root.geometry()
            
            # Parse geometry string (e.g., "450x700+100+200" or "450x700")
            if 'x' in geometry:
                parts = geometry.split('+')
                size_part = parts[0]
                
                if 'x' in size_part:
                    width, height = map(int, size_part.split('x'))
                    
                    # Check if we have position information
                    if len(parts) >= 3:
                        x, y = map(int, parts[1:3])
                    else:
                        # No position info, use current position
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
                    
                    # Only log when actually saving, not during the save process
                    logger.debug(f"Window config saved: {width}x{height} at ({x}, {y})")
                else:
                    # Reduced logging for better performance
                    pass
            else:
                # Reduced logging for better performance
                pass
                
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
        logger.info("Setting up UI")
        
        # Custom color scheme for glass effect
        bg_color = '#1e1e1e'
        frame_bg = '#2d2d2d'
        accent_color = '#4a9eff'
        text_color = '#ffffff'
        secondary_text = '#b0b0b0'
        
        # No custom title bar - using Windows native one
        logger.info("Using Windows native title bar")
        
        # Create scrollable main container with dark-mode scrollbar
        # Canvas for scrolling
        self.main_canvas = tk.Canvas(self.root, bg=bg_color, highlightthickness=0)
        self.main_canvas.pack(side='left', fill='both', expand=True)
        
        # Main container with glass padding (adjusted for native title bar)
        main_frame = tk.Frame(self.main_canvas, bg=bg_color, padx=20, pady=20)
        self.main_canvas.create_window((0, 0), window=main_frame, anchor='nw')
        
        # Configure canvas scrolling
        main_frame.bind('<Configure>', lambda e: self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all")))
        
        # Dark-mode scrollbar for main window (only visible on hover)
        self.main_scrollbar = tk.Scrollbar(self.root, 
                                          orient='vertical',
                                          bg='#606060',
                                          activebackground='#4a9eff',
                                          troughcolor='#2d2d2d',
                                          width=12,
                                          relief='flat',
                                          borderwidth=0)
        self.main_scrollbar.pack(side='right', fill='y')
        
        # Configure scrollbar
        self.main_scrollbar.config(command=self.main_canvas.yview)
        self.main_canvas.config(yscrollcommand=self.main_scrollbar.set)
        
        # Initially hide main scrollbar
        self.main_scrollbar.pack_forget()
        
        # Bind scrollbar hover events
        self.main_scrollbar.bind('<Enter>', self.show_main_scrollbar)
        self.main_scrollbar.bind('<Leave>', self.hide_main_scrollbar)
        
        # Check if main scrollbar should be available
        self.check_main_scrollbar_need()
        
        logger.info("Scrollable main frame with hover scrollbar created and packed")
        
        # Static hexagon background - place it behind the main content
        self.background = StaticHexagonBackground(main_frame, width=410, height=680)
        self.background.place(relx=0, rely=0, relwidth=1, relheight=1)
        # Ensure the background is visible and properly configured
        self.background.configure(bg='#1e1e1e', highlightthickness=0)
        logger.info("Static hexagon background placed behind UI")
        
        # Configure grid weights for responsive layout
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)
        
        # Timer Feature Box
        self.timer_box = FeatureBox(main_frame, "Timer")
        self.timer_box.pack(fill='x', pady=(0, 20))
        self.setup_timer_section()
        logger.info("Timer box created and packed")
        
        # Task Management Feature Box
        self.task_box = FeatureBox(main_frame, "Task Management")
        self.task_box.pack(fill='x', pady=(0, 20))
        self.setup_task_section()
        logger.info("Task box created and packed")
        
        # Quick Launch Feature Box
        self.app_box = FeatureBox(main_frame, "Quick Launch")
        self.app_box.pack(fill='x', pady=(0, 20))
        self.setup_app_section()
        logger.info("App box created and packed")
        
        # Status bar
        status_frame = tk.Frame(main_frame, bg=bg_color)
        status_frame.pack(fill='x', pady=(20, 0))
        
        status_label = tk.Label(status_frame, text="Ready to focus!", 
                               font=("Segoe UI", 9),
                               bg=bg_color, fg=secondary_text,
                               anchor='center')
        status_label.pack(fill='x')
        
        self.refresh_task_list()
        
        # Bind window resize event (no saving here to avoid spam)
        self.root.bind('<Configure>', self.on_window_resize)
        
        # Bind mouse wheel scrolling for main window when hovering over content
        self.main_canvas.bind('<MouseWheel>', self.on_main_scroll)
        self.main_canvas.bind('<Button-4>', self.on_main_scroll)
        self.main_canvas.bind('<Button-5>', self.on_main_scroll)

        # No custom resize handles needed with native title bar
        
        logger.info("UI setup complete")
    

    
    def setup_timer_section(self):
        logger.info("Setting up timer section")
        content = self.timer_box.content_frame
        
        # Timer display with glass styling
        self.timer_label = tk.Label(content, text="50:00", 
                                   font=("Segoe UI", 42, "bold"), 
                                   bg='#2d2d2d', fg='#4a9eff',
                                   pady=25)
        self.timer_label.pack(pady=(25, 25))
        
        # Timer selection buttons
        time_select_frame = tk.Frame(content, bg='#2d2d2d')
        time_select_frame.pack(pady=(0, 20))
        
        # Preset time buttons
        preset_frame = tk.Frame(time_select_frame, bg='#2d2d2d')
        preset_frame.pack()
        
        time_20_btn = tk.Button(preset_frame, text="20m", 
                                font=("Segoe UI", 9, "bold"),
                                bg='#17a2b8', fg='#ffffff',
                                relief='flat', borderwidth=0,
                                padx=15, pady=8,
                                command=lambda: self.set_timer(20),
                                activebackground='#138496',
                                activeforeground='#ffffff')
        time_20_btn.pack(side='left', padx=(0, 10))
        
        time_50_btn = tk.Button(preset_frame, text="50m", 
                                font=("Segoe UI", 9, "bold"),
                                bg='#28a745', fg='#ffffff',
                                relief='flat', borderwidth=0,
                                padx=15, pady=8,
                                command=lambda: self.set_timer(50),
                                activebackground='#218838',
                                activeforeground='#ffffff')
        time_50_btn.pack(side='left', padx=(0, 10))
        
        time_120_btn = tk.Button(preset_frame, text="120m", 
                                 font=("Segoe UI", 9, "bold"),
                                 bg='#fd7e14', fg='#ffffff',
                                 relief='flat', borderwidth=0,
                                 padx=15, pady=8,
                                 command=lambda: self.set_timer(120),
                                 activebackground='#e8690b',
                                 activeforeground='#ffffff')
        time_120_btn.pack(side='left', padx=(0, 10))
        
        custom_btn = tk.Button(preset_frame, text="Custom", 
                               font=("Segoe UI", 9, "bold"),
                               bg='#6f42c1', fg='#ffffff',
                               relief='flat', borderwidth=0,
                               padx=15, pady=8,
                               command=self.set_custom_timer,
                               activebackground='#5a32a3',
                               activeforeground='#ffffff')
        custom_btn.pack(side='left', padx=(0, 10))
        
        # Timer control buttons with proper layout
        button_frame = tk.Frame(content, bg='#2d2d2d')
        button_frame.pack(pady=(0, 25))
        
        # Top row buttons
        top_button_frame = tk.Frame(button_frame, bg='#2d2d2d')
        top_button_frame.pack()
        
        self.start_button = tk.Button(top_button_frame, text="Start", 
                                     font=("Segoe UI", 10, "bold"),
                                     bg='#4a9eff', fg='#ffffff',
                                     relief='flat', borderwidth=0,
                                     padx=25, pady=10,
                                     command=self.start_timer,
                                     activebackground='#3a8eef',
                                     activeforeground='#ffffff')
        self.start_button.pack(side='left', padx=(0, 15))
        
        self.stop_button = tk.Button(top_button_frame, text="Stop", 
                                    font=("Segoe UI", 10, "bold"),
                                    bg='#666666', fg='#ffffff',
                                    relief='flat', borderwidth=0,
                                    padx=25, pady=10,
                                    state="disabled",
                                    command=self.stop_timer,
                                    activebackground='#555555',
                                    activeforeground='#ffffff')
        self.stop_button.pack(side='left', padx=(15, 0))
        
        # Reset button on separate row
        self.reset_button = tk.Button(button_frame, text="Reset", 
                                     font=("Segoe UI", 10, "bold"),
                                     bg='#555555', fg='#ffffff',
                                     relief='flat', borderwidth=0,
                                     padx=25, pady=10,
                                     command=self.reset_timer,
                                     activebackground='#444444',
                                     activeforeground='#ffffff')
        self.reset_button.pack(pady=(20, 0))
        
        logger.info("Timer section setup complete")
    
    def setup_task_section(self):
        logger.info("Setting up task section")
        content = self.task_box.content_frame
        
        # Task input with glass styling
        input_frame = tk.Frame(content, bg='#2d2d2d')
        input_frame.pack(fill='x', padx=20, pady=(20, 15))
        
        self.task_entry = tk.Entry(input_frame, 
                                  font=("Segoe UI", 10),
                                  bg='#1e1e1e', fg='#ffffff',
                                  insertbackground='#ffffff',
                                  relief='flat', borderwidth=1,
                                  highlightthickness=1,
                                  highlightbackground='#4a9eff',
                                  highlightcolor='#4a9eff')
        self.task_entry.pack(side='left', fill='x', expand=True, padx=(0, 15))
        self.task_entry.bind('<Return>', lambda e: self.add_task())
        
        add_button = tk.Button(input_frame, text="Add Task", 
                              font=("Segoe UI", 10, "bold"),
                              bg='#4a9eff', fg='#ffffff',
                              relief='flat', borderwidth=0,
                              padx=20, pady=8,
                              command=self.add_task,
                              activebackground='#3a8eef',
                              activeforeground='#ffffff')
        add_button.pack(side='right')
        
                # Task list with glass styling and scrollbar
        list_frame = tk.Frame(content, bg='#2d2d2d')
        list_frame.pack(fill='both', expand=True, padx=20, pady=(0, 15))
        
        # Create scrollbar frame with proper spacing
        scrollbar_frame = tk.Frame(list_frame, bg='#2d2d2d', width=12)
        scrollbar_frame.pack(side='right', fill='y', padx=(5, 0))
        scrollbar_frame.pack_propagate(False)
        
        # Mini scrollbar (only visible when needed) - make it more visible
        self.task_scrollbar = tk.Scrollbar(scrollbar_frame, 
                                          orient='vertical',
                                          bg='#606060',
                                          activebackground='#4a9eff',
                                          troughcolor='#2d2d2d',
                                          width=8,
                                          relief='flat',
                                          borderwidth=0)
        self.task_scrollbar.pack(fill='y', expand=True)
        
        # Initially hide scrollbar
        self.task_scrollbar.pack_forget()
        
        # Task listbox with scrollbar
        self.task_listbox = tk.Listbox(list_frame, 
                                       height=6, 
                                       font=("Segoe UI", 9),
                                       bg='#1e1e1e', fg='#ffffff',
                                       selectbackground='#4a9eff',
                                       selectforeground='#ffffff',
                                       relief='flat', borderwidth=1,
                                       highlightthickness=1,
                                       highlightbackground='#4a9eff',
                                       highlightcolor='#4a9eff',
                                       yscrollcommand=self.task_scrollbar.set)
        self.task_listbox.pack(side='left', fill='both', expand=True)
        
        # Configure scrollbar
        self.task_scrollbar.config(command=self.task_listbox.yview)
        
        # Bind mouse wheel scrolling to both listbox and scrollbar frame
        self.task_listbox.bind('<MouseWheel>', self.on_task_scroll)
        self.task_listbox.bind('<Button-4>', self.on_task_scroll)
        self.task_listbox.bind('<Button-5>', self.on_task_scroll)
        
        # Also bind to scrollbar frame to catch events
        scrollbar_frame.bind('<MouseWheel>', self.on_task_scroll)
        scrollbar_frame.bind('<Button-4>', self.on_task_scroll)
        scrollbar_frame.bind('<Button-5>', self.on_task_scroll)
        
        # Task action buttons with proper layout
        button_frame = tk.Frame(content, bg='#2d2d2d')
        button_frame.pack(pady=(0, 20))
        
        # Top row buttons
        top_button_frame = tk.Frame(button_frame, bg='#2d2d2d')
        top_button_frame.pack()
        
        complete_button = tk.Button(top_button_frame, text="Complete", 
                                   font=("Segoe UI", 9, "bold"),
                                   bg='#28a745', fg='#ffffff',
                                   relief='flat', borderwidth=0,
                                   padx=18, pady=8,
                                   command=self.complete_task,
                                   activebackground='#218838',
                                   activeforeground='#ffffff')
        complete_button.pack(side='left', padx=(0, 15))
        
        delete_button = tk.Button(top_button_frame, text="Delete", 
                                 font=("Segoe UI", 9, "bold"),
                                 bg='#dc3545', fg='#ffffff',
                                 relief='flat', borderwidth=0,
                                 padx=18, pady=8,
                                 command=self.delete_task,
                                 activebackground='#c82333',
                                 activeforeground='#ffffff')
        delete_button.pack(side='left', padx=(15, 0))
        
        # Clear button on separate row
        clear_button = tk.Button(button_frame, text="Clear All", 
                                font=("Segoe UI", 9, "bold"),
                                bg='#6c757d', fg='#ffffff',
                                relief='flat', borderwidth=0,
                                padx=18, pady=8,
                                command=self.clear_tasks,
                                activebackground='#5a6268',
                                activeforeground='#ffffff')
        clear_button.pack(pady=(15, 0))
        
        logger.info("Task section setup complete")
    
    def setup_app_section(self):
        logger.info("Setting up app section")
        content = self.app_box.content_frame
        
        # App input with glass styling
        input_frame = tk.Frame(content, bg='#2d2d2d')
        input_frame.pack(fill='x', padx=20, pady=(20, 15))
        
        self.app_entry = tk.Entry(input_frame, 
                                 font=("Segoe UI", 10),
                                 bg='#1e1e1e', fg='#ffffff',
                                 insertbackground='#ffffff',
                                 relief='flat', borderwidth=1,
                                 highlightthickness=1,
                                 highlightbackground='#4a9eff',
                                 highlightcolor='#4a9eff')
        self.app_entry.pack(side='left', fill='x', expand=True, padx=(0, 15))
        self.app_entry.insert(0, "notepad.exe")
        
        launch_button = tk.Button(input_frame, text="Launch App", 
                                 font=("Segoe UI", 10, "bold"),
                                 bg='#4a9eff', fg='#ffffff',
                                 relief='flat', borderwidth=0,
                                 padx=20, pady=8,
                                 command=self.launch_app,
                                 activebackground='#3a8eef',
                                 activeforeground='#ffffff')
        launch_button.pack(side='right')
        
        # Browse button with glass styling
        browse_button = tk.Button(content, text="Browse Files", 
                                 font=("Segoe UI", 10, "bold"),
                                 bg='#17a2b8', fg='#ffffff',
                                 relief='flat', borderwidth=0,
                                 padx=25, pady=10,
                                 command=self.browse_app,
                                 activebackground='#138496',
                                 activeforeground='#ffffff')
        browse_button.pack(pady=(0, 20))
        
        logger.info("App section setup complete")
    
    def update_scrollbar_visibility(self):
        """Show or hide scrollbar based on content"""
        try:
            # Check if content exceeds visible area
            if hasattr(self, 'task_listbox') and hasattr(self, 'task_scrollbar'):
                # Get the number of visible items
                visible_count = self.task_listbox.size()
                max_visible = 6  # Height of listbox
                
                if visible_count > max_visible:
                    # Show scrollbar
                    self.task_scrollbar.pack(fill='y', expand=True)
                else:
                    # Hide scrollbar
                    self.task_scrollbar.pack_forget()
        except Exception as e:
            logger.debug(f"Scrollbar visibility update error: {e}")
    
    def show_main_scrollbar(self, event):
        """Show main scrollbar on hover"""
        try:
            if hasattr(self, 'main_scrollbar'):
                self.main_scrollbar.pack(side='right', fill='y')
        except Exception as e:
            logger.debug(f"Show main scrollbar error: {e}")
    
    def hide_main_scrollbar(self, event):
        """Hide main scrollbar when not hovering"""
        try:
            if hasattr(self, 'main_scrollbar'):
                # Small delay to make hiding feel more natural
                self.root.after(200, lambda: self.main_scrollbar.pack_forget() if hasattr(self, 'main_scrollbar') else None)
        except Exception as e:
            logger.debug(f"Hide main scrollbar error: {e}")
    
    def check_main_scrollbar_need(self):
        """Check if main scrollbar is needed and make it available for hover"""
        try:
            if hasattr(self, 'main_canvas') and hasattr(self, 'main_scrollbar'):
                # Get canvas dimensions
                canvas_height = self.main_canvas.winfo_height()
                scroll_region = self.main_canvas.bbox("all")
                
                if scroll_region:
                    content_height = scroll_region[3] - scroll_region[1]
                    
                    # If content is taller than canvas, make scrollbar available for hover
                    if content_height > canvas_height:
                        # Don't show it yet, just make it available for hover
                        pass
                    else:
                        # Content fits, no scrollbar needed
                        self.main_scrollbar.pack_forget()
        except Exception as e:
            logger.debug(f"Check main scrollbar need error: {e}")
    
    def on_main_scroll(self, event):
        """Handle mouse wheel scrolling for main window"""
        try:
            if event.num == 4 or event.delta > 0:  # Scroll up
                self.main_canvas.yview_scroll(-1, "units")
            elif event.num == 5 or event.delta < 0:  # Scroll down
                self.main_canvas.yview_scroll(1, "units")
        except Exception as e:
            logger.debug(f"Main scroll error: {e}")
    
    def on_task_scroll(self, event):
        """Handle mouse wheel scrolling for task list"""
        try:
            if event.num == 4 or event.delta > 0:  # Scroll up
                self.task_listbox.yview_scroll(-1, "units")
            elif event.num == 5 or event.delta < 0:  # Scroll down
                self.task_listbox.yview_scroll(1, "units")
            # Prevent event from propagating to parent widgets
            return "break"
        except Exception as e:
            logger.debug(f"Task scroll error: {e}")
            return "break"
    
    def on_window_resize(self, event):
        if event.widget == self.root:
            # Update background canvas size
            if hasattr(self, 'background'):
                self.background.configure(width=event.width-40, height=event.height-70)
            
            # Ensure minimum size is maintained
            if event.width < 400:
                self.root.geometry(f"400x{event.height}")
            if event.height < 600:
                self.root.geometry(f"{event.width}x600")
            
            # Check if main scrollbar is needed after resize
            self.root.after(100, self.check_main_scrollbar_need)
            
            # Do not save on every resize; saving happens on mouse release

    def ensure_taskbar_presence(self):
        # Initial setup for Windows taskbar presence
        if os.name == 'nt':
            try:
                hwnd = self.root.winfo_id()
                GWL_EXSTYLE = -20
                WS_EX_APPWINDOW = 0x00040000
                WS_EX_TOOLWINDOW = 0x00000080
                SetWindowLong = ctypes.windll.user32.SetWindowLongW
                GetWindowLong = ctypes.windll.user32.GetWindowLongW
                SetWindowPos = ctypes.windll.user32.SetWindowPos
                
                # Get current extended style
                exStyle = GetWindowLong(hwnd, GWL_EXSTYLE)
                # Ensure it's not a tool window and has proper window styles
                exStyle = (exStyle | WS_EX_APPWINDOW) & (~WS_EX_TOOLWINDOW)
                SetWindowLong(hwnd, GWL_EXSTYLE, exStyle)
                
                # Force a style refresh
                SWP_FRAMECHANGED = 0x0020
                SetWindowPos(hwnd, None, 0, 0, 0, 0, SWP_FRAMECHANGED)
                
                logger.debug("Taskbar presence ensured")
            except Exception as e:
                logger.debug(f"ensure_taskbar_presence failed: {e}")


    
    def start_timer(self):
        if not self.timer_running:
            logger.info("Starting timer")
            self.timer_running = True
            self.start_button.config(state="disabled", bg='#666666')
            self.stop_button.config(state="normal", bg='#dc3545')
            self.timer_thread = threading.Thread(target=self.timer_loop, daemon=True)
            self.timer_thread.start()
        else:
            logger.warning("Timer already running")
    
    def stop_timer(self):
        logger.info("Stopping timer")
        self.timer_running = False
        self.start_button.config(state="normal", bg='#4a9eff')
        self.stop_button.config(state="disabled", bg='#666666')
    
    def set_timer(self, minutes):
        """Set timer to specified number of minutes"""
        logger.info(f"Setting timer to {minutes} minutes")
        self.stop_timer()
        self.time_remaining = minutes * 60
        self.original_time_minutes = minutes
        self.update_timer_display()
    
    def set_custom_timer(self):
        """Open dialog for custom timer input"""
        logger.info("Opening custom timer dialog")
        
        # Create custom timer dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Custom Timer")
        dialog.geometry("300x150")
        dialog.configure(bg='#2d2d2d')
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center dialog on parent window
        dialog.geometry("+%d+%d" % (self.root.winfo_rootx() + 75, self.root.winfo_rooty() + 275))
        
        # Input frame
        input_frame = tk.Frame(dialog, bg='#2d2d2d')
        input_frame.pack(pady=20)
        
        tk.Label(input_frame, text="Enter minutes:", 
                font=("Segoe UI", 10), bg='#2d2d2d', fg='#ffffff').pack()
        
        time_entry = tk.Entry(input_frame, font=("Segoe UI", 12), width=10)
        time_entry.pack(pady=10)
        time_entry.focus()
        time_entry.bind('<Return>', lambda e: self.apply_custom_timer(dialog, time_entry))
        
        # Button frame
        button_frame = tk.Frame(dialog, bg='#2d2d2d')
        button_frame.pack(pady=10)
        
        tk.Button(button_frame, text="Set", 
                 font=("Segoe UI", 9, "bold"),
                 bg='#4a9eff', fg='#ffffff',
                 relief='flat', borderwidth=0,
                 padx=20, pady=5,
                 command=lambda: self.apply_custom_timer(dialog, time_entry),
                 activebackground='#3a8eef',
                 activeforeground='#ffffff').pack(side='left', padx=(0, 10))
        
        tk.Button(button_frame, text="Cancel", 
                 font=("Segoe UI", 9, "bold"),
                 bg='#666666', fg='#ffffff',
                 relief='flat', borderwidth=0,
                 padx=20, pady=5,
                 command=dialog.destroy,
                 activebackground='#555555',
                 activeforeground='#ffffff').pack(side='left')
    
    def apply_custom_timer(self, dialog, time_entry):
        """Apply custom timer value from dialog"""
        try:
            minutes = int(time_entry.get().strip())
            if minutes > 0 and minutes <= 1440:  # Max 24 hours
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
        self.start_button.config(state="normal", bg='#4a9eff')
        self.stop_button.config(state="disabled", bg='#666666')
        
        # Use stored original time for completion message
        messagebox.showinfo("Timer Complete", f"{self.original_time_minutes}-minute focus session completed!")
        
        # Reset to default 50 minutes
        self.time_remaining = 50 * 60
        self.original_time_minutes = 50
        self.update_timer_display()
    
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
        else:
            logger.warning("Attempted to add empty task")
    
    def complete_task(self):
        selection = self.task_listbox.curselection()
        if selection:
            index = selection[0]
            if index < len(self.tasks):
                task_text = self.tasks[index]['text']
                self.tasks[index]['completed'] = not self.tasks[index]['completed']
                status = "completed" if self.tasks[index]['completed'] else "uncompleted"
                logger.info(f"Task '{task_text}' {status}")
                self.refresh_task_list()
                self.save_tasks()
            else:
                logger.error(f"Task index {index} out of range")
        else:
            logger.warning("No task selected for completion")
    
    def delete_task(self):
        selection = self.task_listbox.curselection()
        if selection:
            index = selection[0]
            if index < len(self.tasks):
                task_text = self.tasks[index]['text']
                logger.info(f"Deleting task: {task_text}")
                del self.tasks[index]
                self.refresh_task_list()
                self.save_tasks()
            else:
                logger.error(f"Task index {index} out of range")
        else:
            logger.warning("No task selected for deletion")
    
    def clear_tasks(self):
        logger.info("Clearing all tasks")
        if messagebox.askyesno("Clear Tasks", "Are you sure you want to clear all tasks?"):
            self.tasks = []
            self.refresh_task_list()
            self.save_tasks()
            logger.info("All tasks cleared")
        else:
            logger.info("Task clear cancelled by user")
    
    def refresh_task_list(self):
        logger.debug(f"Refreshing task list with {len(self.tasks)} tasks")
        self.task_listbox.delete(0, tk.END)
        for i, task in enumerate(self.tasks):
            status = "✓ " if task['completed'] else "□ "
            display_text = f"{status}{task['text']}"
            self.task_listbox.insert(tk.END, display_text)
            if task['completed']:
                self.task_listbox.itemconfig(i, fg='#28a745')
        
        # Show/hide scrollbar based on content
        self.update_scrollbar_visibility()
    
    def launch_app(self):
        app_name = self.app_entry.get().strip()
        if app_name:
            logger.info(f"Launching application: {app_name}")
            try:
                subprocess.Popen(app_name, shell=True)
                logger.info(f"Successfully launched {app_name}")
            except Exception as e:
                logger.error(f"Failed to launch {app_name}: {str(e)}")
                messagebox.showerror("Error", f"Could not launch {app_name}: {str(e)}")
        else:
            logger.warning("No application name provided")
    
    def browse_app(self):
        logger.info("Opening file browser")
        filename = filedialog.askopenfilename(
            title="Select Application",
            filetypes=[("Executable files", "*.exe"), ("All files", "*.*")]
        )
        if filename:
            logger.info(f"Selected file: {filename}")
            self.app_entry.delete(0, tk.END)
            self.app_entry.insert(0, filename)
        else:
            logger.info("File selection cancelled")
    
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
        logger.info("Starting Focus Tool application")
        root = tk.Tk()
        app = FocusTool(root)
        
        def on_closing():
            logger.info("Application closing")
            try:
                app.save_tasks()
                app.save_window_config() # Save window config on closing
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
