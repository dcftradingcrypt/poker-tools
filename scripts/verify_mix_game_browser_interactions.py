#!/usr/bin/env python3
"""Headless Chrome interaction checks for the mix-game UI.

This complements verify_mix_game_runtime_static.py. It uses Chrome DevTools
Protocol directly through the standard library, so it does not require
Playwright or npm installs.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import socket
import struct
import subprocess
import tempfile
import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

from verify_mix_game_runtime_static import CheckResult, add_check, repo_root, serve_repo


INTERACTION_CHECK_VERSION = "1.3"
EXPECTED_GAME_IDS = [
    "plo_high",
    "o8",
    "plo8",
    "badugi",
    "a5_triple_draw",
    "deuce_to_seven_triple_draw",
    "razz",
    "stud_high",
    "stud8",
    "basil_826",
]


class DevToolsWebSocket:
    def __init__(self, url: str, timeout: float = 15.0) -> None:
        parsed = urllib.parse.urlparse(url)
        if parsed.scheme != "ws" or not parsed.hostname or not parsed.port:
            raise ValueError(f"unsupported websocket url: {url}")
        self.host = parsed.hostname
        self.port = parsed.port
        self.path = parsed.path
        self.timeout = timeout
        self.sock = socket.create_connection((self.host, self.port), timeout=timeout)
        self.sock.settimeout(timeout)
        self.next_id = 1
        self.events: list[dict[str, Any]] = []
        self._handshake()

    def close(self) -> None:
        try:
            self.sock.close()
        except OSError:
            pass

    def _handshake(self) -> None:
        key = base64.b64encode(os.urandom(16)).decode("ascii")
        request = (
            f"GET {self.path} HTTP/1.1\r\n"
            f"Host: {self.host}:{self.port}\r\n"
            "Upgrade: websocket\r\n"
            "Connection: Upgrade\r\n"
            f"Sec-WebSocket-Key: {key}\r\n"
            "Sec-WebSocket-Version: 13\r\n"
            "\r\n"
        ).encode("ascii")
        self.sock.sendall(request)
        response = b""
        while b"\r\n\r\n" not in response:
            chunk = self.sock.recv(4096)
            if not chunk:
                break
            response += chunk
        if b" 101 " not in response.split(b"\r\n", 1)[0]:
            raise RuntimeError(f"websocket handshake failed: {response[:200]!r}")
        accept_src = (key + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11").encode("ascii")
        expected_accept = base64.b64encode(hashlib.sha1(accept_src).digest())
        if expected_accept not in response:
            raise RuntimeError("websocket handshake accept header mismatch")

    def send_json(self, payload: dict[str, Any]) -> None:
        data = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        header = bytearray([0x81])
        length = len(data)
        if length < 126:
            header.append(0x80 | length)
        elif length < 65536:
            header.append(0x80 | 126)
            header.extend(struct.pack("!H", length))
        else:
            header.append(0x80 | 127)
            header.extend(struct.pack("!Q", length))
        mask = os.urandom(4)
        masked = bytes(byte ^ mask[index % 4] for index, byte in enumerate(data))
        self.sock.sendall(bytes(header) + mask + masked)

    def recv_json(self) -> dict[str, Any]:
        while True:
            first = self._recv_exact(2)
            opcode = first[0] & 0x0F
            masked = bool(first[1] & 0x80)
            length = first[1] & 0x7F
            if length == 126:
                length = struct.unpack("!H", self._recv_exact(2))[0]
            elif length == 127:
                length = struct.unpack("!Q", self._recv_exact(8))[0]
            mask = self._recv_exact(4) if masked else b""
            payload = self._recv_exact(length) if length else b""
            if masked:
                payload = bytes(byte ^ mask[index % 4] for index, byte in enumerate(payload))
            if opcode == 8:
                raise RuntimeError("websocket closed by remote")
            if opcode == 9:
                self._send_pong(payload)
                continue
            if opcode != 1:
                continue
            return json.loads(payload.decode("utf-8"))

    def _send_pong(self, payload: bytes) -> None:
        header = bytearray([0x8A])
        header.append(0x80 | len(payload))
        mask = os.urandom(4)
        masked = bytes(byte ^ mask[index % 4] for index, byte in enumerate(payload))
        self.sock.sendall(bytes(header) + mask + masked)

    def _recv_exact(self, length: int) -> bytes:
        data = b""
        while len(data) < length:
            chunk = self.sock.recv(length - len(data))
            if not chunk:
                raise RuntimeError("socket closed")
            data += chunk
        return data

    def command(self, method: str, params: dict[str, Any] | None = None, timeout: float = 15.0) -> dict[str, Any]:
        command_id = self.next_id
        self.next_id += 1
        self.send_json({"id": command_id, "method": method, "params": params or {}})
        deadline = time.time() + timeout
        while time.time() < deadline:
            message = self.recv_json()
            if message.get("id") == command_id:
                if "error" in message:
                    raise RuntimeError(f"{method} failed: {message['error']}")
                return message.get("result", {})
            if "method" in message:
                self.events.append(message)
        raise TimeoutError(f"timed out waiting for {method}")


def wait_for_devtools_port(user_data_dir: Path, timeout: float = 15.0) -> int:
    port_file = user_data_dir / "DevToolsActivePort"
    deadline = time.time() + timeout
    while time.time() < deadline:
        if port_file.is_file():
            lines = port_file.read_text(encoding="utf-8", errors="replace").splitlines()
            if lines and lines[0].isdigit():
                return int(lines[0])
        time.sleep(0.1)
    raise TimeoutError("Chrome did not publish DevToolsActivePort")


def create_target(port: int, url: str) -> str:
    encoded_url = urllib.parse.quote(url, safe=":/?&=%")
    request = urllib.request.Request(f"http://127.0.0.1:{port}/json/new?{encoded_url}", method="PUT")
    with urllib.request.urlopen(request, timeout=10) as response:
        payload = json.loads(response.read().decode("utf-8"))
    ws_url = payload.get("webSocketDebuggerUrl")
    if not isinstance(ws_url, str) or not ws_url:
        raise RuntimeError(f"missing webSocketDebuggerUrl in {payload}")
    return ws_url


def evaluate(ws: DevToolsWebSocket, expression: str, timeout: float = 20.0) -> Any:
    result = ws.command(
        "Runtime.evaluate",
        {
            "expression": expression,
            "awaitPromise": True,
            "returnByValue": True,
            "timeout": int(timeout * 1000),
        },
        timeout=timeout + 5,
    )
    if result.get("exceptionDetails"):
        raise RuntimeError(json.dumps(result["exceptionDetails"], sort_keys=True)[:1000])
    remote = result.get("result", {})
    return remote.get("value")


def interaction_expression() -> str:
    return r"""
(async () => {
  const wait = (ms = 80) => new Promise(resolve => setTimeout(resolve, ms));
  const expectedGameIds = [
    'plo_high',
    'o8',
    'plo8',
    'badugi',
    'a5_triple_draw',
    'deuce_to_seven_triple_draw',
    'razz',
    'stud_high',
    'stud8',
    'basil_826',
  ];
  const expectedControls = {
    plo_high: ['#mix-plo-view-select'],
    o8: ['#mix-o8-family-select', '#mix-o8-position-select'],
    plo8: ['[data-mix-plo8-position-tab]'],
    badugi: ['[data-mix-badugi-position-tab]'],
    a5_triple_draw: ['[data-mix-a5-position-tab]'],
    stud8: ['[data-mix-stud8-position-tab]'],
    basil_826: ['#mix-826-variant-select', '#mix-826-view-select', '#mix-826-position-select'],
  };
  const selectStateKeys = {
    '#mix-plo-view-select': 'selectedPloView',
    '#mix-o8-family-select': 'selectedO8Family',
    '#mix-o8-position-select': 'selectedO8Position',
    '#mix-826-variant-select': 'selected826Variant',
    '#mix-826-view-select': 'selected826View',
    '#mix-826-position-select': 'selected826Position',
  };
  const tabStateKeys = {
    '[data-mix-plo8-position-tab]': ['selectedPlo8Position', 'mixPlo8PositionTab'],
    '[data-mix-badugi-position-tab]': ['selectedBadugiPosition', 'mixBadugiPositionTab'],
    '[data-mix-a5-position-tab]': ['selectedA5Position', 'mixA5PositionTab'],
    '[data-mix-stud8-position-tab]': ['selectedStud8Position', 'mixStud8PositionTab'],
  };
  const expectedPublicRangeGlobals = {
    __PLO_HIGH_PREFLOP_PUBLIC_RANGES_V1: 'plo_high_preflop_position_ranges_v3',
    __PLO8_PREFLOP_PUBLIC_RANGES_V1: 'plo8_preflop_position_ranges_v1',
    __BADUGI_PRE_DRAW_PUBLIC_RANGES_V1: 'badugi_pre_draw_position_ranges_v3',
    __A5_TRIPLE_DRAW_PUBLIC_RANGES_V1: 'a5_triple_draw_pre_draw_public_ranges_v1',
    __DEUCE_TO_SEVEN_TRIPLE_DRAW_PUBLIC_RANGES_V1: 'deuce_to_seven_triple_draw_pre_draw_public_ranges_v1',
    __RAZZ_THIRD_STREET_PUBLIC_RANGES_V1: 'razz_third_street_position_ranges_v1',
    __STUD_HIGH_THIRD_STREET_PUBLIC_RANGES_V1: 'stud_high_third_street_position_ranges_v1',
    __STUD8_THIRD_STREET_PUBLIC_RANGES_V1: 'stud8_third_street_position_ranges_v1',
    __BASIL_826_PUBLIC_RANGES_V1: 'basil_826_public_archetypes_v2',
  };
  const errors = [];
  const normalizeText = (value) => String(value || '').replace(/\s+/g, ' ').trim();
  const includesNormalized = (haystack, needle) => normalizeText(haystack).includes(normalizeText(needle));
  const validateBasil826Surface = (stage, variantValue = '', viewValue = '') => {
    const surface = document.getElementById('mix-display-surface');
    const surfaceText = surface ? surface.innerText : '';
    const activeVariant = variantValue || (typeof mixDisplayState === 'undefined' ? '' : mixDisplayState.selected826Variant);
    const activeView = viewValue || (typeof mixDisplayState === 'undefined' ? '' : mixDisplayState.selected826View);
    const viewLabels = {
      archetypes: '資料確認済みアーキタイプ',
      risk_overlays: 'Pot-share / risk',
    };
    const required826Text = [
      '公開資料で確認できる役・構造・リスクだけを表示します',
      'position 別の open range や BB defense matrix は、現時点の資料からは確定できません',
      '公開資料で確認できる範囲',
      '資料確認済み項目',
    ];
    const missing826Text = required826Text.filter(needle => !surfaceText.includes(needle));
    if (missing826Text.length) errors.push(`basil_826_${stage}_missing_boundary_text:${missing826Text.join('|')}`);
    if (surfaceText.includes('Open / Raise') || surfaceText.includes('BB Call')) {
      errors.push(`basil_826_${stage}_forbidden_old_view_label`);
    }
    if (!surface || surfaceText.length < 700) {
      errors.push(`basil_826_${stage}_surface_too_small:${surfaceText.length}`);
    }
    if (activeVariant && !surfaceText.includes(activeVariant)) {
      errors.push(`basil_826_${stage}_missing_active_variant:${activeVariant}`);
    }
    if (activeView && viewLabels[activeView] && !surfaceText.includes(viewLabels[activeView])) {
      errors.push(`basil_826_${stage}_missing_active_view_label:${activeView}`);
    }
    const dataset = window.__BASIL_826_PUBLIC_RANGES_V1;
    const expectedRows = dataset
      && dataset.hand_ranges
      && dataset.hand_ranges[activeVariant]
      && dataset.hand_ranges[activeVariant][activeView]
      && dataset.hand_ranges[activeVariant][activeView].SOURCE_CONFIRMED;
    if (!Array.isArray(expectedRows) || !expectedRows.length) {
      errors.push(`basil_826_${stage}_missing_dataset_rows:${activeVariant}:${activeView}`);
    } else {
      const missingRows = expectedRows.filter(row => !includesNormalized(surfaceText, row));
      if (missingRows.length) {
        errors.push(`basil_826_${stage}_missing_dataset_rows_in_surface:${activeVariant}:${activeView}:${missingRows.length}`);
      }
    }
  };
  const validateBadugiSurface = (stage, positionValue = '') => {
    const surface = document.getElementById('mix-display-surface');
    const surfaceText = surface ? surface.innerText : '';
    const dataset = window.__BADUGI_PRE_DRAW_PUBLIC_RANGES_V1;
    const activePosition = positionValue || (typeof mixDisplayState === 'undefined' ? '' : mixDisplayState.selectedBadugiPosition);
    const position = dataset && dataset.positions && dataset.positions[activePosition];
    const firstInOpen = position && position.first_in_open;
    if (!surface || surfaceText.length < 900) errors.push(`badugi_${stage}_surface_too_small:${surfaceText.length}`);
    if (!position || !firstInOpen) {
      errors.push(`badugi_${stage}_missing_dataset_position:${activePosition}`);
      return;
    }
    const requiredText = [
      'Source evidence folded into this position',
      'リンク先の記事と PDF',
      `${position.label || activePosition} Sources`,
    ];
    const missingRequired = requiredText.filter(needle => !includesNormalized(surfaceText, needle));
    if (missingRequired.length) errors.push(`badugi_${stage}_missing_required_text:${missingRequired.join('|')}`);
    const openRows = Array.isArray(firstInOpen.open_table_rows) ? firstInOpen.open_table_rows : [];
    const missingOpenRows = openRows.flat().filter(value => value && !includesNormalized(surfaceText, value));
    if (missingOpenRows.length) errors.push(`badugi_${stage}_missing_open_rows:${activePosition}:${missingOpenRows.join('|')}`);
    const collectedRows = Array.isArray(firstInOpen.collected_rows) ? firstInOpen.collected_rows : [];
    if (!collectedRows.length) {
      errors.push(`badugi_${stage}_missing_collected_rows:${activePosition}`);
    } else {
      const rangeFieldMissing = collectedRows
        .flatMap(row => [row && row.open_pct, row && row.pat, row && row.tri, row && row.two_card])
        .filter(value => value && !includesNormalized(surfaceText, value));
      if (rangeFieldMissing.length) errors.push(`badugi_${stage}_missing_collected_fields:${activePosition}:${rangeFieldMissing.slice(0, 4).join('|')}`);
    }
    const sourceIndex = dataset && dataset.source_index ? dataset.source_index : {};
    const sourceRefs = Array.isArray(position.source_refs) ? position.source_refs : [];
    const missingTitles = sourceRefs
      .map(sourceRef => sourceIndex[sourceRef] && sourceIndex[sourceRef].title)
      .filter(title => title && !includesNormalized(surfaceText, title));
    if (missingTitles.length) errors.push(`badugi_${stage}_missing_source_titles:${activePosition}:${missingTitles.join('|')}`);
  };
  const validateA5Surface = (stage, positionValue = '') => {
    const surface = document.getElementById('mix-display-surface');
    const surfaceText = surface ? surface.innerText : '';
    const dataset = window.__A5_TRIPLE_DRAW_PUBLIC_RANGES_V1;
    const activePosition = positionValue || (typeof mixDisplayState === 'undefined' ? '' : mixDisplayState.selectedA5Position);
    const position = dataset && dataset.positions && dataset.positions[activePosition];
    if (!surface || surfaceText.length < 800) errors.push(`a5_${stage}_surface_too_small:${surfaceText.length}`);
    if (!position) {
      errors.push(`a5_${stage}_missing_dataset_position:${activePosition}`);
      return;
    }
    const requiredText = [
      `${position.label || activePosition} Range`,
      `${position.label || activePosition} Sources`,
      'CountingOuts',
    ];
    const missingRequired = requiredText.filter(needle => !includesNormalized(surfaceText, needle));
    if (missingRequired.length) errors.push(`a5_${stage}_missing_required_text:${missingRequired.join('|')}`);
    const openRows = position.first_in_open && Array.isArray(position.first_in_open.open_table_rows)
      ? position.first_in_open.open_table_rows
      : [];
    const continueRows = position.versus_open && Array.isArray(position.versus_open.continue_table_rows)
      ? position.versus_open.continue_table_rows
      : [];
    const missingRows = [...openRows, ...continueRows].flat().filter(value => value && !includesNormalized(surfaceText, value));
    if (missingRows.length) errors.push(`a5_${stage}_missing_rows:${activePosition}:${missingRows.slice(0, 6).join('|')}`);
    const sourceIndex = dataset && dataset.source_index ? dataset.source_index : {};
    const sourceRefs = Array.isArray(position.source_refs) ? position.source_refs : [];
    const missingTitles = sourceRefs
      .map(sourceRef => sourceIndex[sourceRef] && sourceIndex[sourceRef].title)
      .filter(title => title && !includesNormalized(surfaceText, title));
    if (missingTitles.length) errors.push(`a5_${stage}_missing_source_titles:${activePosition}:${missingTitles.join('|')}`);
  };
  let select = document.getElementById('mix-game-select');
  const gameIds = select
    ? Array.from(select.options).map(option => option.value || '').filter(Boolean)
    : [];
  if (!select) errors.push('missing_mix_game_select');
  const buttons = Array.from(document.querySelectorAll('button[data-mix-game-id]'));
  for (const [globalName, datasetId] of Object.entries(expectedPublicRangeGlobals)) {
    const payload = window[globalName];
    if (!payload || typeof payload !== 'object') {
      errors.push(`public_range_global_missing:${globalName}`);
      continue;
    }
    if (payload.dataset_id !== datasetId) {
      errors.push(`public_range_global_dataset_mismatch:${globalName}:${payload.dataset_id}:${datasetId}`);
    }
    if (!payload.source_index || typeof payload.source_index !== 'object' || !Object.keys(payload.source_index).length) {
      errors.push(`public_range_global_missing_source_index:${globalName}`);
    }
    const hasRows = Boolean(
      (payload.positions && typeof payload.positions === 'object' && Object.keys(payload.positions).length)
      || (payload.hand_ranges && typeof payload.hand_ranges === 'object' && Object.keys(payload.hand_ranges).length)
    );
    if (!hasRows) errors.push(`public_range_global_missing_rows:${globalName}`);
  }
  for (const gameId of expectedGameIds) {
    select = document.getElementById('mix-game-select');
    const option = select ? Array.from(select.options).find(entry => entry.value === gameId) : null;
    const label = option ? (option.textContent || '').trim() : '';
    const button = document.querySelector(`button[data-mix-game-id="${gameId}"]`);
    if (button) {
      button.click();
    } else if (select) {
      select.value = gameId;
      select.dispatchEvent(new Event('change', { bubbles: true }));
    } else {
      errors.push(`missing_switch_control:${gameId}`);
      continue;
    }
    await wait();
    const nextSelect = document.getElementById('mix-game-select');
    const surface = document.getElementById('mix-display-surface');
    const active = document.querySelector('button.mix-game-card.active');
    const text = document.body.innerText || '';
    if (!surface) errors.push(`missing_surface:${gameId}`);
    if ((nextSelect && nextSelect.value) !== gameId) errors.push(`select_not_synced:${gameId}:${nextSelect && nextSelect.value}`);
    if (typeof mixDisplayState === 'undefined' || mixDisplayState.selectedGameId !== gameId) {
      errors.push(`state_not_synced:${gameId}:${typeof mixDisplayState === 'undefined' ? 'missing_state' : mixDisplayState.selectedGameId}`);
    }
    if (buttons.length && (!active || active.dataset.mixGameId !== gameId)) errors.push(`active_button_not_synced:${gameId}`);
    if (label && !text.includes(label)) errors.push(`missing_label:${gameId}:${label}`);
    const missingControls = (expectedControls[gameId] || []).filter(selector => !document.querySelector(selector));
    if (missingControls.length) errors.push(`missing_controls:${gameId}:${missingControls.join('|')}`);
    if (surface && surface.innerText.length < 300) errors.push(`surface_too_small:${gameId}:${surface.innerText.length}`);
    if (gameId === 'basil_826') {
      const variantSelect = document.querySelector('#mix-826-variant-select');
      const viewSelect = document.querySelector('#mix-826-view-select');
      const positionSelect = document.querySelector('#mix-826-position-select');
      const viewOptions = viewSelect ? Array.from(viewSelect.options).map(option => option.value) : [];
      const positionOptions = positionSelect ? Array.from(positionSelect.options).map(option => option.value) : [];
      const variantOptions = variantSelect ? Array.from(variantSelect.options).map(option => option.value) : [];
      if (!variantOptions.includes('FL826TD') || !variantOptions.includes('NL826SD')) {
        errors.push(`basil_826_variant_options:${variantOptions.join('|')}`);
      }
      if (viewOptions.join('|') !== 'archetypes|risk_overlays') {
        errors.push(`basil_826_view_options:${viewOptions.join('|')}`);
      }
      if (positionOptions.join('|') !== 'SOURCE_CONFIRMED') {
        errors.push(`basil_826_position_options:${positionOptions.join('|')}`);
      }
      validateBasil826Surface('default');
      for (const variantValue of variantOptions) {
        let nextVariantSelect = document.querySelector('#mix-826-variant-select');
        if (nextVariantSelect) {
          nextVariantSelect.value = variantValue;
          nextVariantSelect.dispatchEvent(new Event('change', { bubbles: true }));
          await wait();
        }
        for (const viewValue of viewOptions) {
          const nextViewSelect = document.querySelector('#mix-826-view-select');
          if (nextViewSelect) {
            nextViewSelect.value = viewValue;
            nextViewSelect.dispatchEvent(new Event('change', { bubbles: true }));
            await wait();
          }
          const nextPositionSelect = document.querySelector('#mix-826-position-select');
          if (!nextPositionSelect || nextPositionSelect.value !== 'SOURCE_CONFIRMED') {
            errors.push(`basil_826_combo_position_not_source_confirmed:${variantValue}:${viewValue}:${nextPositionSelect ? nextPositionSelect.value : 'missing'}`);
          }
          if (
            typeof mixDisplayState === 'undefined'
            || mixDisplayState.selected826Variant !== variantValue
            || mixDisplayState.selected826View !== viewValue
            || mixDisplayState.selected826Position !== 'SOURCE_CONFIRMED'
          ) {
            errors.push(`basil_826_combo_state_not_synced:${variantValue}:${viewValue}:${typeof mixDisplayState === 'undefined' ? 'missing_state' : `${mixDisplayState.selected826Variant}/${mixDisplayState.selected826View}/${mixDisplayState.selected826Position}`}`);
          }
          validateBasil826Surface(`${variantValue}_${viewValue}`, variantValue, viewValue);
        }
      }
    }
    if (gameId === 'badugi') {
      const positionValues = Array.from(document.querySelectorAll('[data-mix-badugi-position-tab]'))
        .map(tab => tab.dataset ? tab.dataset.mixBadugiPositionTab : '')
        .filter(Boolean);
      for (const positionValue of positionValues) {
        const tab = document.querySelector(`[data-mix-badugi-position-tab="${positionValue}"]`);
        if (!tab) {
          errors.push(`badugi_position_tab_missing_after_render:${positionValue}`);
          continue;
        }
        tab.click();
        await wait();
        if (typeof mixDisplayState === 'undefined' || mixDisplayState.selectedBadugiPosition !== positionValue) {
          errors.push(`badugi_position_state_not_synced:${positionValue}:${typeof mixDisplayState === 'undefined' ? 'missing_state' : mixDisplayState.selectedBadugiPosition}`);
        }
        validateBadugiSurface(positionValue || 'unknown', positionValue);
      }
    }
    if (gameId === 'a5_triple_draw') {
      const positionValues = Array.from(document.querySelectorAll('[data-mix-a5-position-tab]'))
        .map(tab => tab.dataset ? tab.dataset.mixA5PositionTab : '')
        .filter(Boolean);
      for (const positionValue of positionValues) {
        const tab = document.querySelector(`[data-mix-a5-position-tab="${positionValue}"]`);
        if (!tab) {
          errors.push(`a5_position_tab_missing_after_render:${positionValue}`);
          continue;
        }
        tab.click();
        await wait();
        if (typeof mixDisplayState === 'undefined' || mixDisplayState.selectedA5Position !== positionValue) {
          errors.push(`a5_position_state_not_synced:${positionValue}:${typeof mixDisplayState === 'undefined' ? 'missing_state' : mixDisplayState.selectedA5Position}`);
        }
        validateA5Surface(positionValue || 'unknown', positionValue);
      }
    }
    for (const selector of (expectedControls[gameId] || [])) {
      const stateKey = selectStateKeys[selector];
      if (stateKey) {
        const control = document.querySelector(selector);
        const options = control ? Array.from(control.options || []) : [];
        if (control && options.length > 1) {
          const nextOption = options.find(option => option.value !== control.value) || options[1];
          const nextValue = nextOption.value;
          control.value = nextValue;
          control.dispatchEvent(new Event('change', { bubbles: true }));
          await wait();
          const nextControl = document.querySelector(selector);
          if (typeof mixDisplayState === 'undefined' || mixDisplayState[stateKey] !== nextValue) {
            errors.push(`subcontrol_state_not_synced:${gameId}:${selector}:${stateKey}:${typeof mixDisplayState === 'undefined' ? 'missing_state' : mixDisplayState[stateKey]}:${nextValue}`);
          }
          if (nextControl && nextControl.value !== nextValue) {
            errors.push(`subcontrol_value_not_synced:${gameId}:${selector}:${nextControl.value}:${nextValue}`);
          }
        }
      }
      const tabConfig = tabStateKeys[selector];
      if (tabConfig) {
        const [stateKey, datasetKey] = tabConfig;
        const tabs = Array.from(document.querySelectorAll(selector));
        if (tabs.length > 1) {
          const nextTab = tabs.find(tab => tab.dataset && tab.dataset[datasetKey] !== (typeof mixDisplayState === 'undefined' ? '' : mixDisplayState[stateKey])) || tabs[1];
          const nextValue = nextTab.dataset ? nextTab.dataset[datasetKey] : '';
          nextTab.click();
          await wait();
          if (nextValue && (typeof mixDisplayState === 'undefined' || mixDisplayState[stateKey] !== nextValue)) {
            errors.push(`subtab_state_not_synced:${gameId}:${selector}:${stateKey}:${typeof mixDisplayState === 'undefined' ? 'missing_state' : mixDisplayState[stateKey]}:${nextValue}`);
          }
        }
      }
      const afterSurface = document.getElementById('mix-display-surface');
      if (!afterSurface || afterSurface.innerText.length < 300) {
        errors.push(`subcontrol_surface_too_small:${gameId}:${selector}:${afterSurface ? afterSurface.innerText.length : 0}`);
      }
    }
  }
  return {
    gameIds,
    expectedGameIds,
    errors,
    selectedGameId: typeof mixDisplayState === 'undefined' ? null : mixDisplayState.selectedGameId,
    surfaceTextLength: (document.getElementById('mix-display-surface')?.innerText || '').length,
    visibleCardCount: buttons.length,
    optionCount: document.getElementById('mix-game-select') ? document.getElementById('mix-game-select').options.length : 0,
  };
})()
"""


def verify_interactions(checks: list[CheckResult], root: Path, browser_exe: str) -> None:
    browser_path = Path(browser_exe)
    add_check(checks, "browser.executable_exists", browser_path.is_file(), str(browser_path))
    if not browser_path.is_file():
        return
    server, base_url = serve_repo(root)
    process: subprocess.Popen[str] | None = None
    try:
        with tempfile.TemporaryDirectory(prefix="popker_mix_interactions_", ignore_cleanup_errors=True) as temp_dir_raw:
            temp_dir = Path(temp_dir_raw)
            user_data_dir = temp_dir / "profile"
            process = subprocess.Popen(
                [
                    str(browser_path),
                    "--headless=new",
                    "--disable-gpu",
                    "--disable-dev-shm-usage",
                    "--disable-background-networking",
                    "--no-first-run",
                    "--no-default-browser-check",
                    "--remote-debugging-port=0",
                    f"--user-data-dir={user_data_dir}",
                    "about:blank",
                ],
                cwd=root,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                text=True,
            )
            target_url = f"{base_url}/?tab=mix-tab"
            port = wait_for_devtools_port(user_data_dir)
            ws_url = create_target(port, "about:blank")
            ws = DevToolsWebSocket(ws_url)
            try:
                ws.command("Runtime.enable")
                ws.command("Log.enable")
                ws.command("Page.enable")
                ws.command("Page.navigate", {"url": target_url})
                ready = False
                last_state: Any = None
                for _ in range(80):
                    state = evaluate(
                        ws,
                        "({readyState: document.readyState, hasMix: !!document.getElementById('mix-game-select'), optionCount: document.getElementById('mix-game-select') ? document.getElementById('mix-game-select').options.length : 0, buttonCount: document.querySelectorAll('button[data-mix-game-id]').length})",
                        timeout=5,
                    )
                    last_state = state
                    if (
                        isinstance(state, dict)
                        and state.get("readyState") == "complete"
                        and state.get("hasMix")
                        and int(state.get("optionCount") or 0) >= len(EXPECTED_GAME_IDS)
                    ):
                        ready = True
                        break
                    time.sleep(0.2)
                add_check(checks, "browser.interaction.ready", ready, f"mix controls became available; lastState={last_state}")
                if ready:
                    result = evaluate(ws, interaction_expression(), timeout=30)
                    errors = result.get("errors", []) if isinstance(result, dict) else ["invalid_result"]
                    observed_ids = result.get("gameIds", []) if isinstance(result, dict) else []
                    expected_set = set(EXPECTED_GAME_IDS)
                    add_check(
                        checks,
                        "browser.interaction.game_switching",
                        not errors and set(observed_ids) == expected_set,
                        f"observed={observed_ids} errors={errors} result={result}",
                    )
                event_errors = []
                for event in ws.events:
                    method = event.get("method")
                    params = event.get("params", {})
                    if method == "Runtime.exceptionThrown":
                        event_errors.append(json.dumps(params, sort_keys=True)[:500])
                    if method == "Runtime.consoleAPICalled" and params.get("type") == "error":
                        event_errors.append(json.dumps(params, sort_keys=True)[:500])
                    if method == "Log.entryAdded":
                        entry = params.get("entry", {})
                        if isinstance(entry, dict) and entry.get("level") in {"error", "warning"}:
                            text = str(entry.get("text", ""))
                            url = str(entry.get("url", ""))
                            if "favicon" not in text.lower() and "favicon" not in url.lower():
                                event_errors.append(json.dumps(entry, sort_keys=True)[:500])
                add_check(
                    checks,
                    "browser.interaction.no_runtime_errors",
                    not event_errors,
                    f"runtime/console/log errors={event_errors}",
                )
            finally:
                ws.close()
    finally:
        if process and process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
        server.shutdown()
        server.server_close()


def build_payload(args: argparse.Namespace) -> dict[str, Any]:
    root = repo_root()
    checks: list[CheckResult] = []
    try:
        verify_interactions(checks, root, args.browser_exe)
    except Exception as exc:  # noqa: BLE001
        add_check(checks, "browser.interaction.execution", False, f"{type(exc).__name__}: {exc}")
    failed = [check for check in checks if check.status != "passed"]
    return {
        "interactionCheckVersion": INTERACTION_CHECK_VERSION,
        "repoRoot": ".",
        "status": "passed" if not failed else "failed",
        "summary": {
            "checksTotal": len(checks),
            "checksPassed": len(checks) - len(failed),
            "checksFailed": len(failed),
            "failedCheckIds": [check.check_id for check in failed],
        },
        "checks": [check.as_dict() for check in checks] if args.verbose or failed else [],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--browser-exe", required=True, help="Chromium-family browser executable.")
    parser.add_argument("--verbose", action="store_true", help="Include all checks in output.")
    return parser.parse_args()


def main() -> int:
    payload = build_payload(parse_args())
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
