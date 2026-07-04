"""Sony ADCP protocol client."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
import hashlib
import json
import logging
import socket
from struct import unpack
from typing import Any

from .const import DEFAULT_ADCP_PORT, DEFAULT_SDAP_PORT, DEFAULT_TIMEOUT

_LOGGER = logging.getLogger(__name__)


class ADCPError(Exception):
    """Base ADCP error."""


class ADCPAuthError(ADCPError):
    """Authentication failed."""


class ADCPCommandError(ADCPError):
    """Command rejected by the projector."""


class ADCPTimeoutError(ADCPError):
    """Communication timed out."""


@dataclass(slots=True)
class DiscoveredProjector:
    """Projector discovered via SDAP."""

    ip: str
    model: str
    serial: int


def _strip_quotes(value: str) -> str:
    if value.startswith('"') and value.endswith('"'):
        return value[1:-1]
    return value


class ADCPClient:
    """Async client for Sony ADCP over TCP."""

    def __init__(
        self,
        host: str,
        *,
        port: int = DEFAULT_ADCP_PORT,
        password: str = "",
        timeout: int = DEFAULT_TIMEOUT,
        sdap_port: int = DEFAULT_SDAP_PORT,
    ) -> None:
        self.host = host
        self.port = port
        self.password = password
        self.timeout = timeout
        self.sdap_port = sdap_port
        self._lock = asyncio.Lock()

    async def send_command(self, command: str) -> str | list[str] | bool:
        """Authenticate, send a command, and return the parsed response."""
        async with self._lock:
            return await self._send_command_unlocked(command)

    async def _send_command_unlocked(self, command: str) -> str | list[str] | bool:
        try:
            async with asyncio.timeout(self.timeout):
                reader, writer = await asyncio.open_connection(self.host, self.port)
        except TimeoutError as err:
            raise ADCPTimeoutError(
                f"Timed out connecting to {self.host}:{self.port}"
            ) from err
        except OSError as err:
            raise ADCPError(f"Unable to connect to {self.host}:{self.port}") from err

        try:
            challenge = (await reader.readline()).decode("ascii", errors="ignore").strip()
            if not challenge:
                raise ADCPError("Projector closed connection during authentication")

            if challenge != "NOKEY":
                digest = hashlib.sha256(f"{challenge}{self.password}".encode()).hexdigest()
                writer.write(f"{digest}\r\n".encode("ascii"))
                await writer.drain()
                auth_reply = (await reader.readline()).decode("ascii", errors="ignore").strip()
                if auth_reply == "err_auth":
                    raise ADCPAuthError("ADCP authentication failed")
                if "OK" not in auth_reply:
                    raise ADCPAuthError(f"Unexpected auth response: {auth_reply}")

            writer.write(f"{command}\r\n".encode("ascii"))
            await writer.drain()
            response = (await reader.readline()).decode("ascii", errors="ignore").strip()
        finally:
            writer.close()
            try:
                await writer.wait_closed()
            except Exception:  # noqa: BLE001
                pass

        if not response:
            raise ADCPError(f"No response for command: {command}")

        return self._parse_response(command, response)

    def _parse_response(self, command: str, response: str) -> str | list[str] | bool:
        if response == "ok":
            return True
        if response == "err_auth":
            raise ADCPAuthError("ADCP authentication failed")
        if response == "err_cmd":
            raise ADCPCommandError(f"Unsupported command: {command}")
        if response == "err_val":
            raise ADCPCommandError(f"Invalid value for command: {command}")
        if response == "err_option":
            raise ADCPCommandError(f"Invalid option for command: {command}")
        if response == "err_inactive":
            raise ADCPCommandError(f"Command inactive: {command}")
        if response in {"err_internal1", "err_internal2"}:
            raise ADCPError(f"Projector internal error for command: {command}")

        if command.endswith("? --range") and response.startswith("["):
            try:
                values = json.loads(response)
            except json.JSONDecodeError as err:
                raise ADCPError(f"Invalid range response: {response}") from err
            return [_strip_quotes(str(item)) for item in values]

        if response.startswith('"') and response.endswith('"'):
            return _strip_quotes(response)

        return response

    async def query(self, name: str) -> str:
        """Query a current value."""
        result = await self.send_command(f"{name} ?")
        if isinstance(result, str):
            return result
        raise ADCPError(f"Unexpected query response for {name}: {result}")

    async def query_range(self, name: str) -> list[str]:
        """Query allowed values for a select command."""
        result = await self.send_command(f"{name} ? --range")
        if isinstance(result, list):
            return result
        raise ADCPError(f"Unexpected range response for {name}: {result}")

    async def set_value(self, name: str, value: str) -> None:
        """Set a quoted ADCP value."""
        await self.send_command(f'{name} "{value}"')

    async def execute(self, name: str) -> None:
        """Execute a menu_exec style command."""
        await self.send_command(name)

    async def get_device_info(self) -> dict[str, Any]:
        """Return model and serial information."""
        model = await self.query("modelname")
        serial = await self.query("serialnum")
        return {"model": model, "serial": serial}

    @staticmethod
    async def discover(
        timeout: int = 12,
        sdap_port: int = DEFAULT_SDAP_PORT,
    ) -> list[DiscoveredProjector]:
        """Discover Sony projectors via SDAP UDP advertisements."""

        def receive_once(sock: socket.socket) -> tuple[bytes, tuple[str, int]]:
            return sock.recvfrom(1028)

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind(("", sdap_port))
            sock.setblocking(False)
        except OSError as err:
            sock.close()
            raise ADCPError(f"Unable to bind SDAP port {sdap_port}") from err

        devices: list[DiscoveredProjector] = []
        seen: set[tuple[int, str]] = set()
        loop = asyncio.get_running_loop()
        end = loop.time() + timeout

        try:
            while loop.time() < end:
                remaining = end - loop.time()
                if remaining <= 0:
                    break
                try:
                    data, addr = await asyncio.wait_for(
                        loop.run_in_executor(None, receive_once, sock),
                        timeout=remaining,
                    )
                except TimeoutError:
                    break

                if len(data) < 24:
                    continue

                serial = unpack(">I", data[20:24])[0]
                model = data[8:20].strip(b"\x00").decode("ascii", errors="ignore")
                ip = addr[0]
                key = (serial, ip)
                if not model or key in seen:
                    continue
                seen.add(key)
                devices.append(DiscoveredProjector(ip=ip, model=model, serial=serial))
        finally:
            sock.close()

        return devices
