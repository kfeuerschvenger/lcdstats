from datetime import datetime, timezone
import random
import subprocess
import time

class DataGatherer:
    """Gathers system and network metrics, with simulated fallbacks for non-Raspberry environments."""

    # Constants
    HEAVY_GATHER_INTERVAL = 300  # seconds between expensive gathers

    # Shell commands as constants
    PUBLIC_IP_CMD = "curl -s ifconfig.me"
    LOCAL_IP_CMD = "hostname -I | awk '{print $1}'"
    DISK_USAGE_CMD = "df / | awk 'NR==2 {print $5}'"
    TEMP_CMD = "awk '{printf \"%.1f°C\\n\", $1/1000}' /sys/class/thermal/thermal_zone0/temp"
    UPTIME_CMD = "uptime -p | sed -e 's/up //' -e 's/ minutes*/m/g' -e 's/ hours*/h/g' -e 's/ days*/d/g' -e 's/,/ /g'"
    SYSTIME_CMD = "date +\"%H:%M %Z\""
    CPU_USAGE_CMD = (
            "bash -c 'PREV=($(</proc/stat)); sleep 0.2; "
            "CURR=($(</proc/stat)); "
            "IDLE=$((CURR[4]-PREV[4])); "
            "TOTAL=0; for i in {1..9}; do TOTAL=$((TOTAL+CURR[i]-PREV[i])); done; "
            "echo \"scale=2; 100*(1 - $IDLE/$TOTAL)\" | bc | xargs printf \"%s%%\"'"
        )
    RAM_USAGE_CMD = "free | awk '/Mem:/ {printf \"%.1f%%\\n\", ($3/$2)*100}'"

    def __init__(self, is_raspberry: bool = True) -> None:
        """Initialize the DataGatherer with a flag indicating if it's running on a Raspberry Pi."""
        self.is_raspberry = is_raspberry

        # Caches for infrequently-changing values
        self._caches = {
            'public_ip': {'value': '', 'timestamp': 0},
            'local_ip':  {'value': '', 'timestamp': 0},
            'disk':      {'value': '', 'timestamp': 0},
        }

        # State for simulated metrics
        self._sim_cpu = 5.0
        self._sim_mem = 35.0
        self._sim_temp = 65.0

    def _run_cached(self, key: str, cmd: str) -> str:
        """Run a shell command if cache is stale, else return cached value."""
        cache = self._caches[key]
        now = time.time()
        if now - cache['timestamp'] > self.HEAVY_GATHER_INTERVAL:
            output = subprocess.check_output(cmd, shell=True).decode().strip()
            cache.update(value=output, timestamp=now)
        return cache['value']

    def get_public_ip(self) -> str:
        """Return the public IP, cached for HEAVY_GATHER_INTERVAL seconds."""
        if not self.is_raspberry:
            return f"138.36.96.{random.randint(1,254)}"
        return self._run_cached('public_ip', self.PUBLIC_IP_CMD)

    def get_local_ip(self) -> str:
        """Return the local IP, cached for HEAVY_GATHER_INTERVAL seconds."""
        if not self.is_raspberry:
            return f"192.168.0.{random.randint(1,254)}"
        return self._run_cached('local_ip', self.LOCAL_IP_CMD)

    def get_cpu_usage(self) -> str:
        """Return CPU usage as a percentage string."""
        if not self.is_raspberry:
            self._sim_cpu = max(20.0, min(80.0, self._sim_cpu + random.uniform(-5,5)))
            return f"{self._sim_cpu:.1f}%"
        return subprocess.check_output(self.CPU_USAGE_CMD, shell=True).decode().strip()

    def get_mem_usage(self) -> str:
        """Return memory usage as a percentage string."""
        if not self.is_raspberry:
            self._sim_mem = max(40.0, min(90.0, self._sim_mem + random.uniform(-2,2)))
            return f"{self._sim_mem:.1f}%"
        return subprocess.check_output(self.RAM_USAGE_CMD, shell=True).decode().strip()

    def get_disk_usage(self) -> str:
        """Return disk usage of root (/) as a percentage string."""
        if not self.is_raspberry:
            return f"{random.randint(5,15)}%"
        return self._run_cached('disk', self.DISK_USAGE_CMD)

    def get_temperature(self) -> str:
        """Return CPU temperature in Celsius."""
        if not self.is_raspberry:
            self._sim_temp += random.uniform(-1.5,1.5)
            return f"{self._sim_temp:.1f}°C"
        return subprocess.check_output(self.TEMP_CMD, shell=True).decode().strip()

    def get_uptime(self) -> str:
        """Return system uptime in human-readable form."""
        if not self.is_raspberry:
            return "1d 3h 20m"
        return subprocess.check_output(self.UPTIME_CMD, shell=True).decode().strip()

    def get_systime(self) -> str:
        """Return local system time with timezone."""
        if not self.is_raspberry:
            now = datetime.now(timezone.utc).astimezone()
            offset = int(now.strftime('%z')) // 100
            return now.strftime(f"%H:%M GMT{offset:+d}")
        return subprocess.check_output(self.SYSTIME_CMD, shell=True).decode().strip()

    # --- Numeric helpers ---

    def _strip_suffix(self, text: str, suffix: str) -> float:
        """Remove a suffix and convert to float."""
        return float(text.replace(suffix, '').strip())

    def get_metric_value(self, key: str) -> float:
        """Return the numeric value of a metric based on its key."""
        key = key.lower()
        if key == 'cpu':
            return self._strip_suffix(self.get_cpu_usage(), '%') / 100.0
        elif key == 'mem':
            return self._strip_suffix(self.get_mem_usage(), '%') / 100.0
        elif key == 'disk':
            return self._strip_suffix(self.get_disk_usage(), '%') / 100.0
        elif key == 'temp':
            return self._strip_suffix(self.get_temperature(), '°C')
        else:
            return 0.0