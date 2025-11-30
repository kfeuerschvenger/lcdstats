import socket
import json
import threading
import time
import logging
from PIL import Image
import numpy as np
from typing import Optional, Callable, Dict, Any
from queue import Queue, Empty

from devices.device import Device

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Protocol constants
CODE_OK = 0
CODE_BAD_FORMAT = 1
CODE_AUTH_FAILED = 2
CODE_FRAGMENT_MISSING = 3
CODE_INTERNAL_ERROR = 4

# Timeouts and retry configuration
HANDSHAKE_TIMEOUT = 5.0
READY_TIMEOUT = 10.0
ACK_TIMEOUT = 10.0
MAX_RETRIES = 3
CHUNK_SIZE = 4096

# Reconnection backoff
RECONNECT_DELAYS = [1.0, 2.0, 5.0, 10.0, 15.0]

# Logging throttle
VERBOSE_LOG_DURATION = 300.0  # 5 minutes of verbose logging
QUIET_LOG_INTERVAL = 3600.0   # Log every 1 hour when quiet

class ESP32WiFiDisplay(Device):
    """WiFi display client for ESP32 with robust protocol implementation."""

    def __init__(
        self,
        host: str,
        port: int = 8080,
        width: int = 128,
        height: int = 128,
        reconnect_indefinitely: bool = True
    ):
        super().__init__(width, height)
        self.host = host
        self.port = port

        # Connection state
        self.socket: Optional[socket.socket] = None
        self.connected = False
        self.handshake_done = False

        # Device capabilities from handshake
        self.device_width: Optional[int] = None
        self.device_height: Optional[int] = None
        self.device_format: Optional[str] = None
        self.device_endianness: Optional[str] = None

        # Threading
        self.receiver_thread: Optional[threading.Thread] = None
        self.running = False
        self.send_lock = threading.Lock()

        # Response handling
        self.response_queue: Queue = Queue()
        self.pending_responses: Dict[str, threading.Event] = {}

        # Callbacks
        self.on_request_next_screen: Optional[Callable[[str], None]] = None
        self.on_request_stop_sending: Optional[Callable[[], None]] = None

        # Reconnection management
        self.reconnect_attempt = 0
        self.last_screen_id = "screen1"
        self.reconnect_indefinitely = reconnect_indefinitely
        self.first_connection_time = time.time()
        self.last_verbose_log = time.time()
        self.last_quiet_log = time.time()

        # Connection stability tracking
        self.successful_sends = 0
        self.failed_sends = 0
        self.last_successful_send = 0

        # Start connection
        if not self._connect():
            logger.warning("Initial connection failed. Starting reconnect loop...")
            threading.Thread(target=self._reconnect_loop, daemon=True).start()

    def _should_log_verbose(self) -> bool:
        """Determine if we should log verbosely or throttle logs."""
        elapsed = time.time() - self.first_connection_time
        return elapsed < VERBOSE_LOG_DURATION

    def _log_connection_attempt(self, message: str, level: str = "info"):
        """Log connection attempts with throttling after initial period."""
        now = time.time()

        if self._should_log_verbose():
            # Verbose logging for first 5 minutes
            if level == "info":
                logger.info(message)
            elif level == "warning":
                logger.warning(message)
            elif level == "error":
                logger.error(message)
            self.last_verbose_log = now
        else:
            # Quiet mode: log every hour
            if now - self.last_quiet_log >= QUIET_LOG_INTERVAL:
                logger.info(f"[Quiet mode] Still attempting reconnection... (attempt {self.reconnect_attempt + 1})")
                self.last_quiet_log = now

    def _connect(self) -> bool:
        """Establish connection to ESP32 and wait for handshake."""
        try:
            self._log_connection_attempt(f"Connecting to ESP32 at {self.host}:{self.port}")

            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(HANDSHAKE_TIMEOUT)

            try:
                self.socket.connect((self.host, self.port))
            except (ConnectionRefusedError, socket.timeout, OSError) as e:
                self._log_connection_attempt(f"Connection refused or timeout: {e}", "warning")
                self._disconnect()
                return False

            # Wait for handshake
            if not self._receive_handshake():
                self._log_connection_attempt("Handshake failed", "error")
                self._disconnect()
                return False

            # Start receiver thread
            self.running = True
            self.receiver_thread = threading.Thread(target=self._receiver_loop, daemon=True)
            self.receiver_thread.start()

            self.connected = True
            self.reconnect_attempt = 0
            self.successful_sends = 0
            self.failed_sends = 0
            logger.info(f"Connected successfully. Device: {self.device_width}x{self.device_height} {self.device_format} {self.device_endianness}")
            return True

        except Exception as e:
            self._log_connection_attempt(f"Connection failed: {e}", "error")
            self._disconnect()
            return False

    def _receive_handshake(self) -> bool:
        """Receive and parse handshake from ESP32."""
        try:
            line = self._read_line(timeout=HANDSHAKE_TIMEOUT)
            if not line:
                self._log_connection_attempt("No handshake received", "error")
                return False

            data = json.loads(line)

            if data.get("status") != "ready" or data.get("code") != CODE_OK:
                self._log_connection_attempt(f"Invalid handshake: {data}", "error")
                return False

            self.device_width = data.get("width")
            self.device_height = data.get("height")
            self.device_format = data.get("format")
            self.device_endianness = data.get("endianness")

            if not all([self.device_width, self.device_height, self.device_format, self.device_endianness]):
                logger.error("Incomplete handshake data")
                return False

            self.handshake_done = True
            return True

        except json.JSONDecodeError as e:
            logger.error(f"Handshake JSON parse error: {e}")
            return False
        except Exception as e:
            logger.error(f"Handshake error: {e}")
            return False

    def _read_line(self, timeout: float = 5.0) -> Optional[str]:
        """Read a complete line terminated by \\n."""
        if not self.socket:
            return None

        try:
            self.socket.settimeout(timeout)
            buffer = b""

            while True:
                chunk = self.socket.recv(1)
                if not chunk:
                    return None

                buffer += chunk
                if chunk == b'\n':
                    return buffer.decode('utf-8').strip()

        except socket.timeout:
            self._log_connection_attempt("Read line timeout", "warning")
            return None
        except Exception as e:
            logger.error(f"Read line error: {e}")
            return None

    def _receiver_loop(self) -> None:
        """Background thread that receives and processes responses from ESP32."""
        buffer = ""
        consecutive_errors = 0
        max_consecutive_errors = 5

        while self.running and self.socket:
            try:
                self.socket.settimeout(1.0)
                chunk = self.socket.recv(1024)

                if not chunk:
                    logger.warning("Connection closed by ESP32")
                    self._handle_disconnect()
                    break

                # Reset error counter on successful receive
                consecutive_errors = 0

                buffer += chunk.decode('utf-8')

                # Process complete lines
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    line = line.strip()

                    if line:
                        self._process_response(line)

            except socket.timeout:
                # Timeout is normal, just continue
                consecutive_errors = 0
                continue
            except Exception as e:
                consecutive_errors += 1
                if consecutive_errors >= max_consecutive_errors:
                    logger.error(f"Too many consecutive receiver errors ({consecutive_errors}): {e}")
                    self._handle_disconnect()
                    break

        logger.info("Receiver thread stopped")

    def _process_response(self, line: str) -> None:
        """Process a JSON response line from ESP32."""
        try:
            data = json.loads(line)
            logger.debug(f"Received: {data}")

            # Handle commands from ESP32
            command = data.get("command")
            if command == "REQUEST_NEXT_SCREEN":
                last = data.get("last", "")
                if self.on_request_next_screen:
                    threading.Thread(target=self.on_request_next_screen, args=(last,), daemon=True).start()
                return

            elif command == "REQUEST_STOP_SENDING":
                if self.on_request_stop_sending:
                    threading.Thread(target=self.on_request_stop_sending, daemon=True).start()
                return

            # Handle status responses
            status = data.get("status")
            if status:
                self.response_queue.put(data)

                # Signal waiting threads
                for key, event in list(self.pending_responses.items()):
                    if status in key:
                        event.set()

        except json.JSONDecodeError as e:
            logger.warning(f"JSON parse error: {line} - {e}")
        except Exception as e:
            logger.error(f"Response processing error: {e}")

    def _wait_for_response(self, expected_status: str, timeout: float) -> Optional[Dict[str, Any]]:
        """Wait for a specific response from ESP32."""
        event_key = f"{expected_status}_{time.time()}"
        event = threading.Event()
        self.pending_responses[event_key] = event

        try:
            if event.wait(timeout):
                # Get response from queue
                start = time.time()
                while time.time() - start < 1.0:
                    try:
                        response = self.response_queue.get(timeout=0.1)
                        if response.get("status") == expected_status:
                            return response
                    except Empty:
                        continue

            logger.warning(f"Timeout waiting for {expected_status}")
            return None

        finally:
            del self.pending_responses[event_key]

    def _disconnect(self) -> None:
        """Close connection and cleanup."""
        self.connected = False
        self.handshake_done = False
        self.running = False

        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None

    def _handle_disconnect(self) -> None:
        """Handle unexpected disconnection and schedule reconnection."""
        if self.connected:
            logger.warning("Connection lost, scheduling reconnection")
        self._disconnect()

        # Only start new reconnect loop if we should reconnect indefinitely
        if self.reconnect_indefinitely:
            threading.Thread(target=self._reconnect_loop, daemon=True).start()

    def _reconnect_loop(self) -> None:
        """Attempt to reconnect indefinitely with exponential backoff."""
        self.reconnect_attempt = 0

        while not self.connected and self.reconnect_indefinitely:
            # Choose delay with cap
            delay_index = min(self.reconnect_attempt, len(RECONNECT_DELAYS) - 1)
            delay = RECONNECT_DELAYS[delay_index]

            self._log_connection_attempt(f"Reconnecting in {delay:.1f}s (attempt {self.reconnect_attempt + 1})")
            time.sleep(delay)

            if self._connect():
                logger.info("Reconnected successfully")
                return

            self.reconnect_attempt += 1

        if not self.reconnect_indefinitely:
            logger.info("Stopped reconnection attempts (reconnect_indefinitely=False)")

    def _convert_to_rgb565(self, image: Image.Image) -> bytes:
        """Convert PIL image to RGB565 little-endian bytes."""
        # Handle RGBA
        if image.mode == 'RGBA':
            bg = Image.new("RGBA", image.size, (0, 0, 0, 255))
            image = Image.alpha_composite(bg, image)

        # Convert to RGB and resize
        img = image.convert('RGB').resize((self.width, self.height))

        # Convert to RGB565
        arr = np.array(img, dtype=np.uint16)
        r = (arr[:, :, 0] & 0xF8) << 8
        g = (arr[:, :, 1] & 0xFC) << 3
        b = (arr[:, :, 2] & 0xF8) >> 3
        rgb565 = r | g | b

        # Convert to little-endian bytes
        data = rgb565.tobytes()
        return data

    def display(self, image: Image.Image) -> None:
        """Send image to ESP32 display."""
        # Skip if not connected
        if not self.connected or not self.handshake_done:
            return

        # Convert image
        try:
            data = self._convert_to_rgb565(image)
        except Exception as e:
            logger.error(f"Image conversion error: {e}")
            return

        # Send with retries
        for attempt in range(MAX_RETRIES):
            if self._send_display_data(data, self.last_screen_id):
                self.successful_sends += 1
                self.last_successful_send = time.time()
                self.failed_sends = 0  # Reset failure counter on success
                return
            
            self.failed_sends += 1
            logger.warning(f"Display send failed, retry {attempt + 1}/{MAX_RETRIES}")
            time.sleep(0.5)

        # All retries failed
        logger.error(f"Display send failed after all retries (consecutive failures: {self.failed_sends})")
        
        # If we have too many failures, trigger reconnection
        if self.failed_sends >= 3:
            logger.error("Too many consecutive send failures, triggering reconnection")
            self._handle_disconnect()

    def _send_display_data(self, data: bytes, screen_id: str) -> bool:
        """Send display data with protocol handshake."""
        with self.send_lock:
            if not self.connected or not self.socket:
                return False

            try:
                # Send JSON header
                header = {
                    "command": "DISPLAY",
                    "length": len(data),
                    "screen_id": screen_id
                }
                header_str = json.dumps(header) + "\n"
                self.socket.sendall(header_str.encode('utf-8'))

                # Wait for ready response
                response = self._wait_for_response("ready", READY_TIMEOUT)
                if not response or response.get("code") != CODE_OK:
                    logger.error(f"No ready response: {response}")
                    return False

                # Send binary payload in chunks
                total_sent = 0
                while total_sent < len(data):
                    chunk = data[total_sent:total_sent + CHUNK_SIZE]
                    sent = self.socket.send(chunk)
                    total_sent += sent

                logger.debug(f"Sent {total_sent} bytes")

                # Wait for completion response
                response = self._wait_for_response("ok", ACK_TIMEOUT)
                if not response:
                    logger.error("No completion response")
                    return False

                code = response.get("code", -1)

                # Handle error codes
                if code == CODE_FRAGMENT_MISSING:
                    logger.warning("Fragment missing, will retry")
                    return False
                elif code in [CODE_BAD_FORMAT, CODE_INTERNAL_ERROR]:
                    logger.error(f"Fatal error code {code}, reconnecting")
                    self._handle_disconnect()
                    return False
                elif code == CODE_OK:
                    return True
                else:
                    logger.warning(f"Unknown code {code}")
                    return False

            except (BrokenPipeError, ConnectionResetError, OSError) as e:
                logger.error(f"Connection error during send: {e}")
                self._handle_disconnect()
                return False
            except Exception as e:
                logger.error(f"Send error: {e}")
                return False

    def set_screen_id(self, screen_id: str) -> None:
        """Set the current screen ID for tracking."""
        self.last_screen_id = screen_id

    def clear(self) -> None:
        """Clear the display (send black image)."""
        black_image = Image.new('RGB', (self.width, self.height), (0, 0, 0))
        self.display(black_image)

    def update(self) -> None:
        """Update method for compatibility - no-op for WiFi display."""
        pass

    def close(self) -> None:
        """Close connection and cleanup resources."""
        logger.info("Closing ESP32WiFiDisplay")
        self.reconnect_indefinitely = False  # Stop reconnection attempts
        self.running = False
        self._disconnect()

        if self.receiver_thread and self.receiver_thread.is_alive():
            self.receiver_thread.join(timeout=2.0)