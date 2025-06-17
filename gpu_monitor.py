
import torch
import time
import psutil

def monitor_performance():
    """Monitor GPU and system performance during AI inference"""
    if not torch.cuda.is_available():
        print("No GPU available for monitoring")
        return
    
    print("🖥️ Performance Monitor Started")
    print("Press Ctrl+C to stop")
    print("-" * 50)
    
    try:
        while True:
            # GPU stats
            gpu_memory_used = torch.cuda.memory_allocated() / (1024**2)
            gpu_memory_total = torch.cuda.get_device_properties(0).total_memory / (1024**2)
            gpu_utilization = (gpu_memory_used / gpu_memory_total) * 100
            
            # System stats
            cpu_percent = psutil.cpu_percent()
            memory_percent = psutil.virtual_memory().percent
            
            print(f"\rGPU: {gpu_utilization:.1f}% ({gpu_memory_used:.0f}MB) | "
                  f"CPU: {cpu_percent:.1f}% | RAM: {memory_percent:.1f}%", end="")
            
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\n📊 Monitoring stopped")

if __name__ == "__main__":
    monitor_performance()
