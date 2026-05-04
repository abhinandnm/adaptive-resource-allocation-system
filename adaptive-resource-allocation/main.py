import time
from core.monitor import SystemMonitor
from core.controller import ResourceController
from utils.logger import logger

def main():
    logger.info("Starting Adaptive Resource Allocation System...")
    monitor = SystemMonitor()
    controller = ResourceController(cpu_threshold=50.0)
    
    try:
        while True:
            # 1. Gather System Metrics
            sys_metrics = monitor.get_system_metrics()
            logger.info(f"System CPU: {sys_metrics['cpu_percent']}% | "
                        f"Memory: {sys_metrics['memory_percent']}% "
                        f"({sys_metrics['memory_used_mb']:.1f}MB / {sys_metrics['memory_total_mb']:.1f}MB)")
            
            # 2. Get Top 3 Processes by CPU
            top_procs = monitor.get_top_processes(limit=3, sort_by="cpu")
            logger.info("Top Processes (by CPU):")
            for p in top_procs:
                logger.info(f"  PID: {p['pid']} | Name: {p['name']} | "
                            f"CPU: {p['cpu_percent']}% | Mem: {p['memory_percent']:.1f}%")
                            
            # 3. Adaptive Control: Evaluate and adjust priorities
            controller.evaluate_and_adjust(top_procs)
                
            print("-" * 50)
            
            # Sleep before next tick
            time.sleep(2)
            
    except KeyboardInterrupt:
        logger.info("System terminated by user.")

if __name__ == "__main__":
    main()
