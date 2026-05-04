import psutil
from utils.logger import logger

class SystemMonitor:
    def __init__(self):
        self.cpu_count = psutil.cpu_count()
        logger.info(f"Initialized SystemMonitor. CPU Count: {self.cpu_count}")

    def get_system_metrics(self):
        """
        Returns overall CPU and Memory usage percentages.
        """
        cpu_usage = psutil.cpu_percent(interval=0.1)
        mem_info = psutil.virtual_memory()
        return {
            "cpu_percent": cpu_usage,
            "memory_percent": mem_info.percent,
            "memory_used_mb": mem_info.used / (1024 * 1024),
            "memory_total_mb": mem_info.total / (1024 * 1024)
        }

    def get_top_processes(self, limit=5, sort_by="cpu"):
        """
        Returns a list of the top resource-consuming processes.
        """
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                pinfo = proc.info
                # Exclude system idle and system processes (PID 0 and 4 on Windows)
                if pinfo['pid'] in (0, 4):
                    continue
                processes.append(pinfo)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        
        # Sort the processes based on the chosen metric
        if sort_by == "cpu":
            processes.sort(key=lambda x: x['cpu_percent'] or 0.0, reverse=True)
        elif sort_by == "memory":
            processes.sort(key=lambda x: x['memory_percent'] or 0.0, reverse=True)
            
        return processes[:limit]
