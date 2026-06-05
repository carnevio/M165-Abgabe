from datetime import datetime
import psutil

class Power:
    def __init__(self, cpu=None, ram_total=None, ram_used=None, timestamp=None):
                                                                    
        if cpu is None:
            self.cpu = float(psutil.cpu_percent(interval=None))
        else:
            self.cpu = float(cpu)

                                                                           
        if ram_total is None or ram_used is None:
            memory = psutil.virtual_memory()
            if ram_total is None:
                self.ram_total = int(memory.total)
            else:
                self.ram_total = int(ram_total)
            
            if ram_used is None:
                self.ram_used = int(memory.used)
            else:
                self.ram_used = int(ram_used)
        else:
            self.ram_total = int(ram_total)
            self.ram_used = int(ram_used)

                                                              
        if timestamp is None:
            self.timestamp = datetime.now()
        else:
            self.timestamp = timestamp

    def to_document(self):
        return {
            "cpu": self.cpu,
            "ram_total": self.ram_total,
            "ram_used": self.ram_used,
            "timestamp": self.timestamp,
        }

