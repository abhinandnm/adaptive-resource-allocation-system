import time
import math

def stress_cpu():
    print("Starting CPU Stress Test...")
    print("This process will consume high CPU to trigger the Adaptive Resource System.")
    print("Press Ctrl+C to stop.")
    
    try:
        while True:
            # A tight loop to consume CPU cycles
            math.factorial(100000)
    except KeyboardInterrupt:
        print("\nStopping stress test.")

if __name__ == "__main__":
    stress_cpu()
