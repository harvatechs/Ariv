#!/usr/bin/env python3
"""
VRAM Monitor - Real-time GPU Memory Tracking for Maha-System
Essential for Google Colab users to prevent OOM crashes
"""

import torch
import time
import logging
from datetime import datetime
from typing import Optional, Callable
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("VRAMMonitor")

class VRAMMonitor:
    """Real-time VRAM monitoring with alerting and logging"""

    def __init__(self, alert_threshold_gb: float = 14.0, log_file: Optional[str] = None):
        self.alert_threshold = alert_threshold_gb * (1024**3)
        self.log_file = log_file
        self.history = []
        self.peak_usage = 0
        self.start_time = None

    def start_monitoring(self, interval_sec: float = 1.0):
        """Start background monitoring"""
        import threading
        self.start_time = time.time()
        self._stop_event = threading.Event()

        def monitor_loop():
            while not self._stop_event.is_set():
                stats = self._get_stats()
                self.history.append(stats)

                if stats['allocated_bytes'] > self.peak_usage:
                    self.peak_usage = stats['allocated_bytes']

                if stats['allocated_bytes'] > self.alert_threshold:
                    logger.warning(f"🚨 VRAM ALERT: {stats['allocated_gb']:.2f}GB")

                time.sleep(interval_sec)

        self._thread = threading.Thread(target=monitor_loop, daemon=True)
        self._thread.start()
        logger.info(f"📊 VRAM monitoring started")

    def stop_monitoring(self):
        """Stop monitoring and return summary"""
        if hasattr(self, '_stop_event'):
            self._stop_event.set()
            self._thread.join(timeout=1.0)

        duration = time.time() - self.start_time if self.start_time else 0
        summary = {
            "duration_sec": duration,
            "peak_gb": self.peak_usage / (1024**3),
            "samples": len(self.history)
        }

        if self.log_file:
            with open(self.log_file, 'w') as f:
                json.dump({"summary": summary, "history": self.history}, f)

        return summary

    def _get_stats(self):
        if not torch.cuda.is_available():
            return {"available": False}
        return {
            "timestamp": datetime.now().isoformat(),
            "allocated_bytes": torch.cuda.memory_allocated(),
            "allocated_gb": torch.cuda.memory_allocated() / (1024**3),
            "total_gb": torch.cuda.get_device_properties(0).total_memory / (1024**3),
        }

if __name__ == "__main__":
    monitor = VRAMMonitor()
    monitor.start_monitoring()
    time.sleep(3)
    print(monitor.stop_monitoring())
