import psutil
import os
from utils.logger import logger

class ResourceController:
    def __init__(self, cpu_threshold=50.0, memory_threshold=80.0):
        # Setting CPU threshold slightly lower for the prototype so it's easier to trigger
        self.cpu_threshold = cpu_threshold
        self.memory_threshold = memory_threshold

    def _set_low_priority(self, proc):
        """
        Cross-platform method to lower process priority.
        Returns True if successful, False otherwise.
        """
        try:
            if os.name == 'nt':
                # Windows priority classes
                below_normal = getattr(psutil, 'BELOW_NORMAL_PRIORITY_CLASS', 16384)
                current_priority = proc.nice()
                
                if current_priority == below_normal:
                    return False # Already low priority
                
                proc.nice(below_normal)
                return True
            else:
                # Linux/macOS nice values (higher nice = lower priority)
                current_nice = proc.nice()
                if current_nice >= 10:
                    return False # Already nice enough
                
                proc.nice(10) # Set to a lower priority
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            # It's common to get AccessDenied for system processes, so we log as debug instead of error
            logger.debug(f"Failed to change priority for PID {proc.pid} ({proc.name()}): {type(e).__name__}")
            return False

    def evaluate_and_adjust(self, top_processes):
        """
        Evaluates the top processes against thresholds and lowers priority if needed.
        """
        adjusted_processes = []
        for pinfo in top_processes:
            cpu_usage = pinfo.get('cpu_percent') or 0.0
            mem_usage = pinfo.get('memory_percent') or 0.0
            
            if cpu_usage > self.cpu_threshold or mem_usage > self.memory_threshold:
                try:
                    proc = psutil.Process(pinfo['pid'])
                    if self._set_low_priority(proc):
                        logger.warning(f"ACTION TAKEN: Lowered priority of PID {pinfo['pid']} ({pinfo['name']}). "
                                       f"CPU: {cpu_usage:.1f}%, Mem: {mem_usage:.1f}%")
                        adjusted_processes.append(pinfo['pid'])
                except psutil.NoSuchProcess:
                    pass
        return adjusted_processes
