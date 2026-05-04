import tkinter as tk
from tkinter import ttk
import threading
import time
from core.monitor import SystemMonitor
from core.controller import ResourceController

class MainWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Adaptive Resource Monitor")
        self.root.geometry("750x500")
        
        # Core components
        self.monitor = SystemMonitor()
        self.controller = ResourceController(cpu_threshold=50.0)
        
        self.is_running = True
        
        self.setup_ui()
        
        # Start background update thread
        self.update_thread = threading.Thread(target=self.update_loop, daemon=True)
        self.update_thread.start()

    def setup_ui(self):
        # Header Frame
        header_frame = tk.Frame(self.root, pady=10)
        header_frame.pack(fill=tk.X)
        
        self.lbl_cpu = tk.Label(header_frame, text="CPU: 0%", font=("Helvetica", 14, "bold"))
        self.lbl_cpu.pack(side=tk.LEFT, padx=20)
        
        self.lbl_mem = tk.Label(header_frame, text="Mem: 0%", font=("Helvetica", 14, "bold"))
        self.lbl_mem.pack(side=tk.LEFT, padx=20)
        
        # Table Frame
        table_frame = tk.Frame(self.root, padx=10, pady=10)
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        # Treeview for processes
        columns = ("pid", "name", "cpu", "mem", "status")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        self.tree.heading("pid", text="PID")
        self.tree.heading("name", text="Process Name")
        self.tree.heading("cpu", text="CPU (%)")
        self.tree.heading("mem", text="Memory (%)")
        self.tree.heading("status", text="Status")
        
        self.tree.column("pid", width=80, anchor=tk.CENTER)
        self.tree.column("name", width=250, anchor=tk.W)
        self.tree.column("cpu", width=100, anchor=tk.CENTER)
        self.tree.column("mem", width=100, anchor=tk.CENTER)
        self.tree.column("status", width=150, anchor=tk.CENTER)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Scrollbar for tree
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Tag for lowered priority
        self.tree.tag_configure('lowered', foreground='red')

    def update_loop(self):
        while self.is_running:
            # Gather metrics
            sys_metrics = self.monitor.get_system_metrics()
            top_procs = self.monitor.get_top_processes(limit=20)
            
            # Action: check if any process needs lower priority
            adjusted_pids = self.controller.evaluate_and_adjust(top_procs)
            
            # Update UI safely using after
            try:
                self.root.after(0, self.refresh_ui, sys_metrics, top_procs, adjusted_pids)
            except tk.TclError:
                # App was closed
                break
                
            time.sleep(2)

    def refresh_ui(self, sys_metrics, top_procs, adjusted_pids):
        # Update headers
        self.lbl_cpu.config(text=f"CPU: {sys_metrics['cpu_percent']}%")
        self.lbl_mem.config(text=f"Memory: {sys_metrics['memory_percent']}% "
                                 f"({sys_metrics['memory_used_mb']:.1f} MB / {sys_metrics['memory_total_mb']:.1f} MB)")
        
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Insert new items
        for p in top_procs:
            pid = p['pid']
            name = p['name']
            cpu = p['cpu_percent'] or 0.0
            mem = p.get('memory_percent') or 0.0
            status = "Lowered Priority" if pid in adjusted_pids else "Normal"
            
            tags = ('lowered',) if pid in adjusted_pids else ()
            
            self.tree.insert("", tk.END, values=(pid, name, f"{cpu:.1f}", f"{mem:.1f}", status), tags=tags)

    def on_close(self):
        self.is_running = False
        self.root.destroy()
