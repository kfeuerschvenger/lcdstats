from datetime import datetime, timezone
import subprocess
import random
import time

class DataGatherer:
    HEAVY_GATHER_TIMER = 300  # 5 min

    def __init__(self, is_raspberry=True):
        self.is_raspberry = is_raspberry
        self._public_ip_cache = {"value": "", "timestamp": 0}
        self._local_ip_cache = {"value": "", "timestamp": 0}
        self._disk_usage_cache = {"value": "", "timestamp": 0}
        self._simulated_cpu = 5.0
        self._simulated_mem = 35.0
        self._simulated_temp = 65.0

    def get_public_ip(self):
        if not self.is_raspberry:
            return self.get_simulated_public_ip()

        current_time = time.time()
        if current_time - self._public_ip_cache["timestamp"] > self.HEAVY_GATHER_TIMER:
            cmd = "curl -s ifconfig.me"
            self._public_ip_cache["value"] = subprocess.check_output(cmd, shell=True).decode('utf-8').strip()
            self._public_ip_cache["timestamp"] = current_time
        return self._public_ip_cache["value"]

    def get_local_ip(self):
        if not self.is_raspberry:
            return self.get_simulated_local_ip()

        current_time = time.time()
        if current_time - self._local_ip_cache["timestamp"] > self.HEAVY_GATHER_TIMER:
            cmd = "hostname -I | awk '{print $1}'"
            self._local_ip_cache["value"] = subprocess.check_output(cmd, shell=True).decode('utf-8').strip()
            self._local_ip_cache["timestamp"] = current_time
        return self._local_ip_cache["value"]

    def get_cpu_usage(self):
        if not self.is_raspberry:
            return self.get_simulated_cpu_usage()

        cmd = """bash -c 'PREV=($(</proc/stat)); sleep 0.2; CURR=($(</proc/stat)); IDLE=$((CURR[4] - PREV[4])); TOTAL=0; for i in {1..9}; do TOTAL=$((TOTAL + CURR[i] - PREV[i])); done; echo "scale=2; 100 * (1 - $IDLE / $TOTAL)" | bc | xargs -I{} echo "{}%"'"""
        return subprocess.check_output(cmd, shell=True).decode('utf-8').strip()

    def get_mem_usage(self):
        if not self.is_raspberry:
            return self.get_simulated_mem_usage()

        cmd = "free | awk '/Mem:/ {printf \"%.1f%%\\n\", ($3/$2)*100}'"
        return subprocess.check_output(cmd, shell=True).decode('utf-8').strip()

    def get_disk_usage(self):
        if not self.is_raspberry:
            return self.get_simulated_disk_usage()

        current_time = time.time()
        if current_time - self._disk_usage_cache["timestamp"] > self.HEAVY_GATHER_TIMER:
            cmd = "df / | awk 'NR==2 {print $5}'"
            self._disk_usage_cache["value"] = subprocess.check_output(cmd, shell=True).decode('utf-8').strip()
            self._disk_usage_cache["timestamp"] = current_time
        return self._disk_usage_cache["value"]

    def get_temperature(self):
        if not self.is_raspberry:
            return self.get_simulated_temperature()

        cmd = "awk '{printf \"%.1f°C\\n\", $1/1000}' /sys/class/thermal/thermal_zone0/temp"
        return subprocess.check_output(cmd, shell=True).decode('utf-8').strip()

    def get_uptime(self):
        if not self.is_raspberry:
            return self.get_simulated_uptime()

        cmd = "uptime -p | sed -e 's/up //' -e 's/ minutes*/m/g' -e 's/ hours*/h/g' -e 's/ days*/d/g' -e 's/,/ /g'"
        return subprocess.check_output(cmd, shell=True).decode('utf-8').strip()

    def get_systime(self):
        if not self.is_raspberry:
            return self.get_simulated_systime()

        cmd = "date +\"%H:%M %Z\""
        return subprocess.check_output(cmd, shell=True).decode('utf-8').strip()

    # Simulated data methods

    def get_simulated_public_ip(self):
        return f"138.36.96.{random.randint(1, 254)}"

    def get_simulated_local_ip(self):
        return f"192.168.0.{random.randint(1, 254)}"

    def get_simulated_cpu_usage(self):
        self._simulated_cpu += random.uniform(-5, 5)
        self._simulated_cpu = max(20.0, min(80.0, self._simulated_cpu))
        return f"{self._simulated_cpu:.1f}%"

    def get_simulated_mem_usage(self):
        self._simulated_mem += random.uniform(-2, 2)
        self._simulated_mem = max(40.0, min(90.0, self._simulated_mem))
        return f"{self._simulated_mem:.1f}%"

    def get_simulated_disk_usage(self):
        return f"{random.randint(5, 15)}%"

    def get_simulated_temperature(self):
        self._simulated_temp += random.uniform(-1.5, 1.5)
        return f"{self._simulated_temp:.1f}°C"

    def get_simulated_uptime(self):
        return "1d 3h 20m"

    def get_simulated_systime(self):
        now = datetime.now(timezone.utc).astimezone()
        offset = now.strftime('%z')
        hours_offset = int(offset) // 100
        return now.strftime(f"%H:%M GMT{hours_offset:+d}")
    
    # Just float value methods

    def get_cpu_usage_value(self):
        usage_str = self.get_cpu_usage().replace('%', '')
        return float(usage_str)

    def get_mem_usage_value(self):
        usage_str = self.get_mem_usage().replace('%', '')
        return float(usage_str)

    def get_disk_usage_value(self):
        usage_str = self.get_disk_usage().replace('%', '')
        return float(usage_str)

    def get_temperature_value(self):
        temp_str = self.get_temperature().replace('°C', '')
        return float(temp_str)