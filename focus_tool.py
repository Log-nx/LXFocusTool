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

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('focus_tool.log')
    ]
)
logger = logging.getLogger(__name__)

class HexagonWave:
    def __init__(self, canvas_width, canvas_height):
        self.x = random.randint(0, canvas_width)
        self.y = random.randint(0, canvas_height)
        self.size = random.randint(6, 12)  # Smaller hexagons
        self.phase = random.uniform(0, 2 * 3.14159)  # Random starting phase
        self.speed = random.uniform(0.01, 0.02)  # Much slower wave speed
        self.opacity = random.uniform(0.05, 0.15)  # Much more subtle opacity
        logger.debug(f"Created hexagon at ({self.x}, {self.y}) with size {self.size}")
    
    def update(self, canvas_width, canvas_height):
        # Slowly change the phase for wave effect
        self.phase += self.speed
        if self.phase > 2 * 3.14159:
            self.phase = 0
        
        # Calculate wave opacity (fade in and out)
        self.current_opacity = self.opacity * (0.3 + 0.7 * math.sin(self.phase))
        
        # Much rarer position reset for better performance
        if random.random() < 0.0001:  # Very rare reset
            self.x = random.randint(0, canvas_width)
            self.y = random.randint(0, canvas_height)

class AnimatedBackground(tk.Canvas):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.hexagons = []
        self.animation_running = False
        logger.info("Initializing AnimatedBackground with hexagon waves")
        self.setup_animation()
    
    def setup_animation(self):
        self.configure(bg='#1e1e1e', highlightthickness=0)
        self.bind('<Configure>', self.on_resize)
        self.create_hexagons()
        self.start_animation()
        logger.info("Hexagon wave animation setup complete")
    
    def create_hexagons(self):
        canvas_width = self.winfo_width() or 450
        canvas_height = self.winfo_height() or 700
        
        # Create fewer hexagons for much better performance
        for i in range(8):  # Reduced from 15 to 8
            hexagon = HexagonWave(canvas_width, canvas_height)
            self.hexagons.append(hexagon)
        logger.info(f"Created {len(self.hexagons)} hexagons")
    
    def on_resize(self, event):
        if event.width > 1 and event.height > 1:
            logger.debug(f"Canvas resize event: {event.width}x{event.height}")
            self.delete("hexagon")
            self.create_hexagons()
    
    def start_animation(self):
        self.animation_running = True
        logger.info("Starting hexagon wave animation")
        self.animate_frame()
    
    def stop_animation(self):
        self.animation_running = False
        logger.info("Stopping hexagon wave animation")
    
    def draw_hexagon(self, x, y, size, opacity):
        """Draw a hexagon at the given position with the given size and opacity"""
        try:
            # Validate coordinates and size
            if not (isinstance(x, (int, float)) and isinstance(y, (int, float)) and isinstance(size, (int, float))):
                return
            if size <= 0 or opacity <= 0:
                return
            
            # Calculate hexagon points
            points = []
            for i in range(6):
                angle = i * 3.14159 / 3
                px = x + size * math.cos(angle)
                py = y + size * math.sin(angle)
                points.extend([px, py])
            
            # Use simple color with stipple for opacity effect instead of hex color
            color = '#4a9eff'
            self.create_polygon(
                points,
                fill='',
                outline=color,
                width=1,
                tags="hexagon",
                stipple='gray50' if opacity < 0.2 else 'gray25'
            )
        except Exception as e:
            logger.error(f"Error drawing hexagon: {e}")
    
    def animate_frame(self):
        if not self.animation_running:
            return
        
        try:
            self.delete("hexagon")
            canvas_width = self.winfo_width() or 450
            canvas_height = self.winfo_height() or 700
            
            for hexagon in self.hexagons:
                try:
                    hexagon.update(canvas_width, canvas_height)
                    
                    # Only draw if opacity is visible enough
                    if hexagon.current_opacity > 0.05:
                        self.draw_hexagon(
                            hexagon.x, 
                            hexagon.y, 
                            hexagon.size, 
                            hexagon.current_opacity
                        )
                except Exception as e:
                    logger.error(f"Error updating hexagon: {e}")
                    continue
            
            # Much slower frame rate for better performance
            self.after(33, self.animate_frame)  # 30fps instead of 10fps
            
        except Exception as e:
            logger.error(f"Error in animation frame: {e}")
            # Try to continue animation
            if self.animation_running:
                self.after(33, self.animate_frame)  # 30fps

class CustomTitleBar(tk.Frame):
    def __init__(self, parent, title, **kwargs):
        super().__init__(parent, **kwargs)
        self.parent = parent
        self.title = title
        self.is_expanded = True
        logger.info(f"Initializing CustomTitleBar for {title}")
        self.setup_title_bar()
    
    def setup_title_bar(self):
        # Title bar background with glass effect
        self.configure(bg='#1a1a1a', height=35)
        
        # Title text
        title_label = tk.Label(self, text=self.title, 
                              font=("Segoe UI", 11, "bold"),
                              bg='#1a1a1a', fg='#ffffff')
        title_label.pack(side='left', padx=(15, 0), pady=8)
        
        # Window control buttons
        button_frame = tk.Frame(self, bg='#1a1a1a')
        button_frame.pack(side='right', padx=(0, 10))
        
        # Minimize button
        min_btn = tk.Button(button_frame, text="─", 
                           font=("Segoe UI", 9, "bold"),
                           bg='#1a1a1a', fg='#ffffff',
                           relief='flat', borderwidth=0,
                           width=4, height=1,
                           command=self.minimize,
                           activebackground='#333333',
                           activeforeground='#ffffff')
        min_btn.pack(side='left', padx=2)
        
        # Expand/Collapse button
        self.expand_btn = tk.Button(button_frame, text="□", 
                                   font=("Segoe UI", 9, "bold"),
                                   bg='#1a1a1a', fg='#ffffff',
                                   relief='flat', borderwidth=0,
                                   width=4, height=1,
                                   command=self.toggle_expand,
                                   activebackground='#333333',
                                   activeforeground='#ffffff')
        self.expand_btn.pack(side='left', padx=2)
        
        # Close button
        close_btn = tk.Button(button_frame, text="×", 
                             font=("Segoe UI", 9, "bold"),
                             bg='#1a1a1a', fg='#ffffff',
                             relief='flat', borderwidth=0,
                             width=4, height=1,
                             command=self.close,
                             activebackground='#dc3545',
                             activeforeground='#ffffff')
        close_btn.pack(side='left', padx=2)
        
        # Bind mouse events for dragging
        self.bind('<Button-1>', self.start_drag)
        self.bind('<B1-Motion>', self.on_drag)
        title_label.bind('<Button-1>', self.start_drag)
        title_label.bind('<B1-Motion>', self.on_drag)
        
        logger.info("Title bar setup complete")
    
    def start_drag(self, event):
        self.x = event.x
        self.y = event.y
        logger.debug(f"Drag started at ({self.x}, {self.y})")
    
    def on_drag(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.parent.winfo_x() + deltax
        y = self.parent.winfo_y() + deltay
        self.parent.geometry(f"+{x}+{y}")
        logger.debug(f"Dragging to ({x}, {y})")
    
    def minimize(self):
        logger.info("Minimizing window")
        self.parent.iconify()
    
    def toggle_expand(self):
        logger.info(f"Toggle expand called. Current state: {'expanded' if self.is_expanded else 'collapsed'}")
        
        if self.is_expanded:
            # Compact mode - show only title bar and timer
            logger.info("Collapsing to compact mode")
            self.parent.geometry("450x200")
            self.expand_btn.config(text="□")
            self.is_expanded = False
            
            # Hide task and app sections
            if hasattr(self.parent, 'task_box'):
                logger.info("Hiding task box")
                self.parent.task_box.pack_forget()
            else:
                logger.warning("Task box not found")
                
            if hasattr(self.parent, 'app_box'):
                logger.info("Hiding app box")
                self.parent.app_box.pack_forget()
            else:
                logger.warning("App box not found")
        else:
            # Full mode - show all sections
            logger.info("Expanding to full mode")
            self.parent.geometry("450x700")
            self.expand_btn.config(text="□")
            self.is_expanded = True
            
            # Show task and app sections
            if hasattr(self.parent, 'task_box'):
                logger.info("Showing task box")
                self.parent.task_box.pack(fill='x', pady=(0, 20))
            else:
                logger.warning("Task box not found")
                
            if hasattr(self.parent, 'app_box'):
                logger.info("Showing app box")
                self.parent.app_box.pack(fill='x', pady=(0, 20))
            else:
                logger.warning("App box not found")
        
        logger.info(f"Expand state changed to: {'expanded' if self.is_expanded else 'collapsed'}")
    
    def close(self):
        logger.info("Closing application")
        self.parent.quit()

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
        
        # Remove default window decorations
        self.root.overrideredirect(True)
        
        # Set window transparency and modern look
        self.root.attributes('-alpha', 0.95)
        self.root.configure(bg='#1e1e1e')
        
        # Center the window on screen (only if no saved position)
        if not hasattr(self, 'saved_x') or not hasattr(self, 'saved_y'):
            self.center_window()
        else:
            # Use saved position
            self.root.geometry(f'{self.saved_width}x{self.saved_height}+{self.saved_x}+{self.saved_y}')
        
        self.tasks = []
        self.timer_running = False
        self.time_remaining = 50 * 60
        self.timer_thread = None
        
        self.load_tasks()
        self.setup_ui()
        self.update_timer_display()
        
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
            logger.debug(f"Raw geometry string: {geometry}")
            
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
                    
                    logger.info(f"Saved window config: {width}x{height} at ({x}, {y})")
                else:
                    logger.warning(f"Invalid geometry format: {geometry}")
            else:
                logger.warning(f"Geometry string missing 'x': {geometry}")
                
        except Exception as e:
            logger.error(f"Error saving window config: {e}")
            logger.error(f"Geometry string was: {geometry}")
    
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
        
        # Custom title bar
        self.title_bar = CustomTitleBar(self.root, "Focus Tool", bg='#1a1a1a')
        self.title_bar.pack(fill='x')
        logger.info("Title bar created and packed")
        
        # Main container with glass padding
        main_frame = tk.Frame(self.root, bg=bg_color, padx=20, pady=20)
        main_frame.pack(fill='both', expand=True)
        logger.info("Main frame created and packed")
        
        # Animated background - place it behind the main content
        self.background = AnimatedBackground(main_frame, width=410, height=660)
        self.background.place(relx=0, rely=0, relwidth=1, relheight=1)
        logger.info("Animated background placed behind UI")
        
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
        
        # Setup resize functionality
        self.setup_resize_functionality()
        
        # Bind window resize event
        self.root.bind('<Configure>', self.on_window_resize)
        
        logger.info("UI setup complete")
    
    def setup_resize_functionality(self):
        """Setup proper resize functionality for the borderless window"""
        logger.info("Setting up resize functionality")
        
        # Create resize handles
        self.create_resize_handles()
        
        logger.info("Resize functionality setup complete")
    
    def create_resize_handles(self):
        """Create visual resize handles around the window"""
        logger.info("Creating resize handles")
        
        # Create corner resize handles directly on the root window
        self.create_corner_handle('nw', 0, 0, 10, 10)      # Top-left
        self.create_corner_handle('ne', 1, 0, 10, 10)      # Top-right
        self.create_corner_handle('sw', 0, 1, 10, 10)      # Bottom-left
        self.create_corner_handle('se', 1, 1, 10, 10)      # Bottom-right
        
        # Create edge resize handles - make them much smaller
        self.create_edge_handle('n', 0.5, 0, 0.1, 0.01)    # Top
        self.create_edge_handle('s', 0.5, 1, 0.1, 0.01)    # Bottom
        self.create_edge_handle('e', 1, 0.5, 0.01, 0.1)    # Right
        self.create_edge_handle('w', 0, 0.5, 0.01, 0.1)    # Left
        
        logger.info("Resize handles created")
    
    def create_corner_handle(self, position, relx, rely, width, height):
        """Create a corner resize handle"""
        handle = tk.Frame(self.root, bg='#4a9eff', width=width, height=height)
        handle.place(relx=relx, rely=rely, anchor='nw' if position == 'nw' else 'ne' if position == 'ne' else 'sw' if position == 'sw' else 'se')
        handle.configure(cursor='sizing')
        
        # Bind resize events
        handle.bind('<Button-1>', lambda e, pos=position: self.start_resize(e, pos))
        handle.bind('<B1-Motion>', lambda e, pos=position: self.on_resize(e, pos))
        
        logger.debug(f"Created corner handle: {position}")
    
    def create_edge_handle(self, position, relx, rely, relwidth, relheight):
        """Create an edge resize handle"""
        handle = tk.Frame(self.root, bg='#4a9eff')
        handle.place(relx=relx, rely=rely, relwidth=relwidth, relheight=relheight, anchor='center')
        
        if position in ['n', 's']:
            handle.configure(cursor='sb_v_double_arrow')
        else:
            handle.configure(cursor='sb_h_double_arrow')
        
        # Bind resize events
        handle.bind('<Button-1>', lambda e, pos=position: self.start_resize(e, pos))
        handle.bind('<B1-Motion>', lambda e, pos=position: self.on_resize(e, pos))
        
        logger.debug(f"Created edge handle: {position}")
    
    def start_resize(self, event, position=None):
        """Start resize operation"""
        if not position:
            # Determine position based on mouse location
            x, y = event.x, event.y
            width, height = self.root.winfo_width(), self.root.winfo_height()
            
            if x < 10 and y < 10:
                position = 'nw'
            elif x > width - 10 and y < 10:
                position = 'ne'
            elif x < 10 and y > height - 10:
                position = 'sw'
            elif x > width - 10 and y > height - 10:
                position = 'se'
            elif x < 10:
                position = 'w'
            elif x > width - 10:
                position = 'e'
            elif y < 10:
                position = 'n'
            elif y > height - 10:
                position = 's'
            else:
                return  # Not on a resize area
        
        self.resize_position = position
        self.start_x = event.x_root
        self.start_y = event.y_root
        self.start_width = self.root.winfo_width()
        self.start_height = self.root.winfo_height()
        
        logger.debug(f"Resize started from {position} at ({self.start_x}, {self.start_y})")
    
    def on_resize(self, event, position=None):
        """Handle resize operation"""
        if not hasattr(self, 'resize_position'):
            return
        
        position = position or getattr(self, 'resize_position', None)
        if not position:
            return
        
        delta_x = event.x_root - self.start_x
        delta_y = event.y_root - self.start_y
        
        new_width = self.start_width
        new_height = self.start_height
        
        # Calculate new dimensions based on resize position
        if position in ['e', 'ne', 'se']:
            new_width = max(400, self.start_width + delta_x)
        elif position in ['w', 'nw', 'sw']:
            new_width = max(400, self.start_width - delta_x)
        
        if position in ['s', 'sw', 'se']:
            new_height = max(600, self.start_height + delta_y)
        elif position in ['n', 'nw', 'ne']:
            new_height = max(600, self.start_height - delta_y)
        
        # Apply new geometry
        if new_width != self.start_width or new_height != self.start_height:
            self.root.geometry(f"{new_width}x{new_height}")
            logger.debug(f"Resized to {new_width}x{new_height} from {position}")
    
    def setup_timer_section(self):
        logger.info("Setting up timer section")
        content = self.timer_box.content_frame
        
        # Timer display with glass styling
        self.timer_label = tk.Label(content, text="50:00", 
                                   font=("Segoe UI", 42, "bold"), 
                                   bg='#2d2d2d', fg='#4a9eff',
                                   pady=25)
        self.timer_label.pack(pady=(25, 25))
        
        # Timer buttons with proper layout
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
        
        # Task list with glass styling
        list_frame = tk.Frame(content, bg='#2d2d2d')
        list_frame.pack(fill='both', expand=True, padx=20, pady=(0, 15))
        
        self.task_listbox = tk.Listbox(list_frame, 
                                      height=6, 
                                      font=("Segoe UI", 9),
                                      bg='#1e1e1e', fg='#ffffff',
                                      selectbackground='#4a9eff',
                                      selectforeground='#ffffff',
                                      relief='flat', borderwidth=1,
                                      highlightthickness=1,
                                      highlightbackground='#4a9eff',
                                      highlightcolor='#4a9eff')
        self.task_listbox.pack(fill='both', expand=True)
        
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
    
    def on_window_resize(self, event):
        if event.widget == self.root:
            # Update background canvas size
            if hasattr(self, 'background'):
                self.background.configure(width=event.width-40, height=event.height-70)
            
            # Ensure minimum size is maintained
            if event.width < 400:
                self.root.geometry(f"400x{event.height}")
                logger.info(f"Enforcing minimum width: 400x{event.height}")
            if event.height < 600:
                self.root.geometry(f"{event.width}x600")
                logger.info(f"Enforcing minimum height: {event.width}x600")
            
            # Save window config after resize (but don't log every resize)
            self.save_window_config()
    
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
    
    def reset_timer(self):
        logger.info("Resetting timer")
        self.stop_timer()
        self.time_remaining = 50 * 60
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
        messagebox.showinfo("Timer Complete", "50-minute focus session completed!")
        self.time_remaining = 50 * 60
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
                if hasattr(app, 'background'):
                    app.background.stop_animation()
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
