"""Tests for Sony ADCP client."""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, patch

import pytest

from custom_components.sony_adcp.adcp_client import (
    ADCPAuthError,
    ADCPClient,
    ADCPCommandError,
)


class MockStreamReader(asyncio.StreamReader):
  """Stream reader with predefined responses."""

  def __init__(self, lines: list[bytes]) -> None:
    super().__init__()
    for line in lines:
      self.feed_data(line)


class MockStreamWriter:
  """Capture writes from the ADCP client."""

  def __init__(self) -> None:
    self.writes: list[bytes] = []
    self.closed = False

  def write(self, data: bytes) -> None:
    self.writes.append(data)

  async def drain(self) -> None:
    return None

  def close(self) -> None:
    self.closed = True

  async def wait_closed(self) -> None:
    return None


@pytest.mark.asyncio
async def test_nokey_command_success() -> None:
  reader = MockStreamReader([b"NOKEY\r\n", b'ok\r\n'])
  writer = MockStreamWriter()
  client = ADCPClient("192.168.1.10")

  with patch(
    "custom_components.sony_adcp.adcp_client.asyncio.open_connection",
    AsyncMock(return_value=(reader, writer)),
  ):
    result = await client.send_command('power "on"')

  assert result is True
  assert writer.writes[-1] == b'power "on"\r\n'


@pytest.mark.asyncio
async def test_authenticated_command_success() -> None:
  reader = MockStreamReader([b"abc123\r\n", b"OK\r\n", b'"on"\r\n'])
  writer = MockStreamWriter()
  client = ADCPClient("192.168.1.10", password="secret")

  with patch(
    "custom_components.sony_adcp.adcp_client.asyncio.open_connection",
    AsyncMock(return_value=(reader, writer)),
  ):
    result = await client.query("power_status")

  assert result == "on"
  assert b"abc123secret" not in writer.writes[0]
  assert len(writer.writes[0].decode().strip()) == 64


@pytest.mark.asyncio
async def test_auth_failure_raises() -> None:
  reader = MockStreamReader([b"abc123\r\n", b"err_auth\r\n"])
  writer = MockStreamWriter()
  client = ADCPClient("192.168.1.10", password="wrong")

  with patch(
    "custom_components.sony_adcp.adcp_client.asyncio.open_connection",
    AsyncMock(return_value=(reader, writer)),
  ), pytest.raises(ADCPAuthError):
    await client.send_command('power "on"')


@pytest.mark.asyncio
async def test_unsupported_command_raises() -> None:
  reader = MockStreamReader([b"NOKEY\r\n", b"err_cmd\r\n"])
  writer = MockStreamWriter()
  client = ADCPClient("192.168.1.10")

  with patch(
    "custom_components.sony_adcp.adcp_client.asyncio.open_connection",
    AsyncMock(return_value=(reader, writer)),
  ), pytest.raises(ADCPCommandError):
    await client.send_command("unknown_command")


@pytest.mark.asyncio
async def test_query_range_parses_json() -> None:
  reader = MockStreamReader(
    [b"NOKEY\r\n", b'["cinema_film1","reference"]\r\n']
  )
  writer = MockStreamWriter()
  client = ADCPClient("192.168.1.10")

  with patch(
    "custom_components.sony_adcp.adcp_client.asyncio.open_connection",
    AsyncMock(return_value=(reader, writer)),
  ):
    result = await client.query_range("picture_mode")

  assert result == ["cinema_film1", "reference"]
