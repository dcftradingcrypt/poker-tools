const crypto = require('crypto');
const fs = require('fs');
const http = require('http');
const path = require('path');

function loadPlaywrightTest() {
  try {
    return require('@playwright/test');
  } catch (primaryErr) {
    try {
      return require('playwright/test');
    } catch (_secondaryErr) {
      const candidatePaths = [];
      let current = module;
      while (current) {
        const filename = current.filename || '';
        const playwrightMarker = `${path.sep}node_modules${path.sep}playwright${path.sep}`;
        const playwrightTestMarker = `${path.sep}node_modules${path.sep}@playwright${path.sep}test${path.sep}`;
        const playwrightIndex = filename.indexOf(playwrightMarker);
        if (playwrightIndex >= 0) {
          candidatePaths.push(path.join(filename.slice(0, playwrightIndex + playwrightMarker.length - 1), 'test.js'));
        }
        const playwrightTestIndex = filename.indexOf(playwrightTestMarker);
        if (playwrightTestIndex >= 0) {
          candidatePaths.push(path.join(filename.slice(0, playwrightTestIndex + playwrightTestMarker.length - 1), 'index.js'));
        }
        current = current.parent;
      }
      for (const candidatePath of candidatePaths) {
        if (fs.existsSync(candidatePath)) {
          return require(candidatePath);
        }
      }
      throw primaryErr;
    }
  }
}

const { test, expect } = loadPlaywrightTest();

const REPO_ROOT = path.resolve(__dirname, '..');
const INDEX_PATH = path.join(REPO_ROOT, 'index.html');
const BRIDGE_BASE = (process.env.PUSHFOLD_BRIDGE_BASE || 'http://127.0.0.1:8875').replace(/\/+$/, '');
const SERVED_PAGE_URL = process.env.PUSHFOLD_SERVED_PAGE_URL
  || `http://127.0.0.1:8876/?tab=pushfold-tab&pushfoldBridgeBase=${encodeURIComponent(BRIDGE_BASE)}`;
const TARGET_NONZERO_REGIME = process.env.PUSHFOLD_TEST_REGIME || 'antes10';
const TARGET_BBANTE_OPENJAM_REGIME = process.env.PUSHFOLD_TEST_BBANTE_REGIME || 'tool10max_bb100_openjam';
const TARGET_CALL_REGIME = process.env.PUSHFOLD_TEST_CALL_REGIME || 'tool10max_bb100_call';
const EXPECTED_ANTE0_SOURCE_EXPANDED_CATEGORIES = [
  '44', '55', '66', '77', '88', '99', 'TT', 'JJ', 'QQ', 'KK', 'AA',
  'A9s', 'ATs', 'AJs', 'AQs', 'AKs', 'A5s',
  'AJo', 'AQo', 'AKo',
  'KTs', 'KJs', 'KQs',
  'QTs', 'QJs',
  'JTs',
];
const EXPECTED_ANTES10_SOURCE_EXPANDED_CATEGORIES = [
  '22', '33', '44', '55', '66', '77', '88', '99', 'TT', 'JJ', 'QQ', 'KK', 'AA',
  'A7s', 'A8s', 'A9s', 'ATs', 'AJs', 'AQs', 'AKs',
  'A5s', 'A4s', 'A3s',
  'ATo', 'AJo', 'AQo', 'AKo',
  'K9s', 'KTs', 'KJs', 'KQs',
  'KJo', 'KQo',
  'Q9s', 'QTs', 'QJs', 'QJo',
  'J9s', 'JTs',
  'T9s',
  '98s',
];
const EXPECTED_BB100_OPENJAM_CATEGORIES = [
  '33', '44', '55', '66', '77', '88', '99', 'TT', 'JJ', 'QQ', 'KK', 'AA',
  'A7s', 'A8s', 'A9s', 'ATs', 'AJs', 'AQs', 'AKs',
  'A5s', 'A4s',
  'ATo', 'AJo', 'AQo', 'AKo',
  'K9s', 'KTs', 'KJs', 'KQs',
  'KJo', 'KQo',
  'Q9s', 'QTs', 'QJs',
  'J9s', 'JTs',
  'T9s',
];
const EXPECTED_BB100_CALL_CATEGORIES = [
  '77', '88', '99', 'TT', 'JJ', 'QQ', 'KK', 'AA',
  'AJs', 'AQs', 'AKs',
  'AQo', 'AKo',
];

function sha256(text) {
  return crypto.createHash('sha256').update(text).digest('hex');
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

function sortStrings(values) {
  return values.slice().sort((left, right) => left.localeCompare(right));
}

async function startStaticIndexServer(options = {}) {
  const mountPathRaw = typeof options.mountPath === 'string' && options.mountPath.trim()
    ? options.mountPath.trim()
    : '/';
  const normalizedMountPath = mountPathRaw === '/'
    ? '/'
    : `/${mountPathRaw.replace(/^\/+|\/+$/g, '')}/`;
  const server = http.createServer((request, response) => {
    const requestUrl = new URL(request.url || '/', 'http://127.0.0.1');
    let repoRelativePath = '';
    if (normalizedMountPath === '/') {
      repoRelativePath = requestUrl.pathname;
    } else if (requestUrl.pathname === normalizedMountPath.slice(0, -1)) {
      repoRelativePath = '/index.html';
    } else if (requestUrl.pathname === normalizedMountPath) {
      repoRelativePath = '/index.html';
    } else if (requestUrl.pathname.startsWith(normalizedMountPath)) {
      repoRelativePath = requestUrl.pathname.slice(normalizedMountPath.length - 1);
    }
    if (!repoRelativePath) {
      response.writeHead(404, { 'Content-Type': 'text/plain; charset=utf-8' });
      response.end('not found');
      return;
    }
    const relativePath = decodeURIComponent(repoRelativePath === '/' ? '/index.html' : repoRelativePath);
    const resolvedPath = path.resolve(REPO_ROOT, `.${relativePath}`);
    if (!(resolvedPath === INDEX_PATH || resolvedPath.startsWith(`${REPO_ROOT}${path.sep}`))) {
      response.writeHead(404, { 'Content-Type': 'text/plain; charset=utf-8' });
      response.end('not found');
      return;
    }
    if (!fs.existsSync(resolvedPath) || !fs.statSync(resolvedPath).isFile()) {
      response.writeHead(404, { 'Content-Type': 'text/plain; charset=utf-8' });
      response.end('not found');
      return;
    }
    const ext = path.extname(resolvedPath).toLowerCase();
    const contentType = ext === '.json'
      ? 'application/json; charset=utf-8'
      : 'text/html; charset=utf-8';
    response.writeHead(200, {
      'Content-Type': contentType,
      'Cache-Control': 'no-store',
      'Pragma': 'no-cache',
      'Expires': '0',
    });
    response.end(fs.readFileSync(resolvedPath));
  });
  await new Promise((resolve, reject) => {
    server.once('error', reject);
    server.listen(0, '127.0.0.1', resolve);
  });
  const address = server.address();
  if (!address || typeof address === 'string') {
    throw new Error('failed to resolve static server address');
  }
  const basePath = normalizedMountPath === '/' ? '' : normalizedMountPath.slice(0, -1);
  return {
    baseUrl: `http://127.0.0.1:${address.port}${basePath}`,
    mountPath: normalizedMountPath,
    close: () => new Promise((resolve, reject) => {
      server.close(err => (err ? reject(err) : resolve()));
    }),
  };
}

async function readState(page) {
  return page.evaluate(() => {
    const surfaceEl = document.getElementById('pushfold-surface');
    const statusEl = document.getElementById('pushfold-bridge-status');
    const noteEl = document.getElementById('pushfold-runtime-note');
    const refreshButton = document.getElementById('pushfold-refresh-btn');
    const loadButton = document.getElementById('pushfold-load-btn');
    const previewEl = document.getElementById('pushfold-range-preview');
    const previewSummaryEl = document.getElementById('pushfold-range-preview-summary');
    const previewEmptyEl = document.getElementById('pushfold-range-preview-empty');
    const previewLegendEl = document.getElementById('pushfold-range-legend');
    const previewCategoryListEl = document.getElementById('pushfold-range-category-list');
    const openPreflopButton = document.getElementById('pushfold-open-preflop-btn');
    const familySelectEl = document.getElementById('pushfold-family-select');
    const familyBadgeEl = document.getElementById('pushfold-family-badge');
    const regimeBadgeEl = document.getElementById('pushfold-regime-badge');
    const anteBadgeEl = document.getElementById('pushfold-ante-badge');
    const familySummaryEl = document.getElementById('pushfold-family-summary');
    const scenarioDetailsEl = document.getElementById('pushfold-scenario-details');
    const scenarioDetailsSummaryEl = scenarioDetailsEl ? scenarioDetailsEl.querySelector('summary') : null;
    const regimeSelectEl = document.getElementById('pushfold-regime-select');
    const runtimeMetaEl = document.getElementById('pushfold-runtime-meta');
    const selectedChipEl = document.getElementById('pushfold-runtime-selected-chip');
    const loadedChipEl = document.getElementById('pushfold-runtime-loaded-chip');
    const positionSelectEl = document.getElementById('pushfold-position-select');
    const secondaryPositionSelectEl = document.getElementById('pushfold-secondary-position-select');
    const positionWrapEl = positionSelectEl ? positionSelectEl.closest('label') : null;
    const secondaryPositionWrapEl = secondaryPositionSelectEl ? secondaryPositionSelectEl.closest('label') : null;
    const state = typeof pushfoldRuntimeState === 'undefined' ? null : pushfoldRuntimeState;
    const activeHands = Array.from(document.querySelectorAll('#pushfold-range-grid td.active-range')).map(cell => cell.dataset.hand || '');
    const activeCell = document.querySelector('#pushfold-range-grid td[data-hand="AA"]');
    const inactiveCell = document.querySelector('#pushfold-range-grid td[data-hand="72o"]');
    return {
      activeTabId: document.querySelector('.tab-content.active')?.id || '',
      runtimeMode: surfaceEl?.dataset.runtimeMode || '',
      sourceMode: surfaceEl?.dataset.sourceMode || '',
      statusText: statusEl ? statusEl.textContent : '',
      noteText: noteEl ? noteEl.textContent : '',
      hasRefreshButton: !!refreshButton,
      hasLoadButton: !!loadButton,
      refreshButtonDisabled: !!refreshButton?.disabled,
      loadButtonDisabled: !!loadButton?.disabled,
      hasOpenPreflopButton: !!openPreflopButton,
      openPreflopButtonDisabled: !!openPreflopButton?.disabled,
      familySelectValue: familySelectEl ? familySelectEl.value : '',
      familyOptionLabels: familySelectEl
        ? Array.from(familySelectEl.querySelectorAll('option')).map(option => option.textContent || '')
        : [],
      familyBadgeText: familyBadgeEl ? familyBadgeEl.textContent : '',
      regimeBadgeText: regimeBadgeEl ? regimeBadgeEl.textContent : '',
      anteBadgeText: anteBadgeEl ? anteBadgeEl.textContent : '',
      familySummaryText: familySummaryEl ? familySummaryEl.textContent : '',
      scenarioDetailsSummaryText: scenarioDetailsSummaryEl ? scenarioDetailsSummaryEl.textContent : '',
      scenarioDetailsText: scenarioDetailsEl ? scenarioDetailsEl.textContent : '',
      refreshAttemptCount: state ? state.refreshAttemptCount : null,
      refreshInFlight: state ? !!state.refreshInFlight : null,
      bridgeHttpOk: state ? !!state.bridgeHttpOk : null,
      fullRangeRenderEnabled: state ? !!state.fullRangeRenderEnabled : null,
      availablePositionCount: state && Array.isArray(state.availablePositions) ? state.availablePositions.length : null,
      previewState: previewEl?.dataset.previewState || '',
      previewLoadedLabel: previewEl?.dataset.loadedLabel || '',
      previewLoadedCategoryCount: Number(previewEl?.dataset.loadedCategoryCount || 0),
      previewLoadedCategoriesCsv: previewEl?.dataset.loadedCategories || '',
      previewSummaryText: previewSummaryEl ? previewSummaryEl.textContent : '',
      previewEmptyText: previewEmptyEl ? previewEmptyEl.textContent : '',
      previewLegendText: previewLegendEl ? previewLegendEl.textContent : '',
      previewCategoryTexts: previewCategoryListEl
        ? Array.from(previewCategoryListEl.querySelectorAll('.pushfold-range-category-chip')).map(chip => chip.textContent || '')
        : [],
      regimeSelectValue: regimeSelectEl ? regimeSelectEl.value : '',
      regimeOptionLabels: regimeSelectEl
        ? Array.from(regimeSelectEl.querySelectorAll('option')).map(option => option.textContent || '')
        : [],
      positionLabelText: positionWrapEl
        ? Array.from(positionWrapEl.childNodes).find(node => node.nodeType === Node.TEXT_NODE)?.textContent?.trim() || ''
        : '',
      secondaryPositionSelectValue: secondaryPositionSelectEl ? secondaryPositionSelectEl.value : '',
      secondaryPositionOptionLabels: secondaryPositionSelectEl
        ? Array.from(secondaryPositionSelectEl.querySelectorAll('option')).map(option => option.textContent || '')
        : [],
      secondaryPositionLabelText: secondaryPositionWrapEl
        ? Array.from(secondaryPositionWrapEl.childNodes).find(node => node.nodeType === Node.TEXT_NODE)?.textContent?.trim() || ''
        : '',
      runtimeMetaText: runtimeMetaEl ? runtimeMetaEl.textContent : '',
      runtimeMetaScenarioLabel: runtimeMetaEl?.dataset.scenarioLabel || '',
      runtimeSelectedText: selectedChipEl ? selectedChipEl.textContent : '',
      runtimeLoadedText: loadedChipEl ? loadedChipEl.textContent : '',
      previewActiveCount: activeHands.length,
      previewActiveHands: activeHands,
      sharedRangeActiveCount: document.querySelectorAll('#range-grid td.active-range').length,
      activeCellOpacity: activeCell ? window.getComputedStyle(activeCell).opacity : '',
      inactiveCellOpacity: inactiveCell ? window.getComputedStyle(inactiveCell).opacity : '',
    };
  });
}

test('served static AOF page under a project-pages-like subpath loads the repo-hosted AOF bundle', async ({ page }) => {
  test.setTimeout(60_000);

  const worktreeHtml = fs.readFileSync(INDEX_PATH, 'utf8');
  const worktreeSha = sha256(worktreeHtml);
  const staticServer = await startStaticIndexServer({ mountPath: '/poker-tools/' });
  const noBridgeUrl = `${staticServer.baseUrl}/?tab=pushfold-tab`;
  const attemptedBridgeRequests = [];
  const bundledAssetRequests = [];

  page.on('request', request => {
    if (request.url().startsWith(`${BRIDGE_BASE}/api/`)) {
      attemptedBridgeRequests.push({
        url: request.url(),
        method: request.method(),
      });
    }
    if (request.url().includes('/assets/pushfold/aof-bundle.v1.json')) {
      bundledAssetRequests.push({
        url: request.url(),
        method: request.method(),
      });
    }
  });

  try {
    const response = await page.goto(noBridgeUrl, { waitUntil: 'domcontentloaded' });
    expect(response).not.toBeNull();
    const servedHtml = await response.text();
    expect(sha256(servedHtml)).toBe(worktreeSha);

    await expect(page.locator('#pushfold-surface')).toHaveAttribute('data-runtime-mode', 'full');
    await expect(page.locator('#pushfold-surface')).toHaveAttribute('data-source-mode', 'bundle');
    await expect(page.locator('#pushfold-bridge-status')).toHaveText('bundled data ready');
    await expect(page.locator('#pushfold-runtime-note')).toContainText('load to show');
    await expect(page.locator('#pushfold-refresh-btn')).toHaveCount(0);
    await expect(page.locator('#pushfold-load-btn')).toBeVisible();
    await expect(page.locator('#pushfold-runtime-meta')).toBeVisible();
    await expect(page.locator('#pushfold-family-badge')).toHaveText('9max');
    await expect(page.locator('#pushfold-regime-badge')).toHaveText('jam');
    await expect(page.locator('#pushfold-ante-badge')).toHaveText('no ante');
    await expect(page.locator('#pushfold-family-summary')).toContainText('Jennifear first-in');
    await expect(page.locator('#pushfold-range-preview')).toHaveAttribute('data-preview-state', 'ready');
    await expect(page.locator('#pushfold-range-preview-empty')).toContainText('13x13 matrix');

    await page.selectOption('#pushfold-stack-select', '11');
    await page.selectOption('#pushfold-position-select', 'UTG+2');
    await expect(page.locator('#pushfold-load-btn')).toBeEnabled();
    await page.locator('#pushfold-load-btn').click();
    await expect(page.locator('#pushfold-range-preview')).toHaveAttribute('data-preview-state', 'loaded');
    await expect(page.locator('#pushfold-range-preview-summary')).toContainText('11bb / UTG+2');
    await expect(page.locator('#pushfold-range-preview-summary')).toContainText('26 active');
    await expect(page.locator('#pushfold-range-preview-summary')).toContainText('9max / jam / no ante');
    await expect(page.locator('#pushfold-range-grid td.active-range')).toHaveCount(26);
    const bundled9maxState = await readState(page);

    await page.selectOption('#pushfold-family-select', 'push72o_tool_10max_bbante');
    await expect(page.locator('#pushfold-family-badge')).toHaveText('10max');
    await expect(page.locator('#pushfold-regime-badge')).toHaveText('jam');
    await expect(page.locator('#pushfold-ante-badge')).toHaveText('BB ante');
    await expect(page.locator('#pushfold-runtime-note')).toContainText('10max / jam / BB ante selected / preview cleared');
    await expect(page.locator('#pushfold-regime-select')).toHaveValue(TARGET_BBANTE_OPENJAM_REGIME);

    await page.selectOption('#pushfold-regime-select', TARGET_CALL_REGIME);
    await expect(page.locator('#pushfold-regime-badge')).toHaveText('call');
    await expect(page.locator('#pushfold-secondary-position-select')).toBeVisible();
    await expect(page.locator('#pushfold-runtime-note')).toContainText('10max / call / BB ante selected');
    await page.selectOption('#pushfold-stack-select', '11');
    await page.selectOption('#pushfold-position-select', 'UTG+2');
    await page.selectOption('#pushfold-secondary-position-select', 'UTG+1');
    await page.locator('#pushfold-load-btn').click();
    await expect(page.locator('#pushfold-range-preview')).toHaveAttribute('data-preview-state', 'loaded');
    await expect(page.locator('#pushfold-range-preview-summary')).toContainText('11bb / jam UTG+2 / caller UTG+1');
    await expect(page.locator('#pushfold-range-preview-summary')).toContainText('13 active');
    await expect(page.locator('#pushfold-range-preview-summary')).toContainText('10max / call / BB ante');
    await expect(page.locator('#pushfold-range-grid td.active-range')).toHaveCount(13);
    const bundledCallState = await readState(page);

    expect(bundled9maxState.activeTabId).toBe('pushfold-tab');
    expect(bundled9maxState.runtimeMode).toBe('full');
    expect(bundled9maxState.sourceMode).toBe('bundle');
    expect(bundled9maxState.bridgeHttpOk).toBe(true);
    expect(bundled9maxState.fullRangeRenderEnabled).toBe(true);
    expect(bundled9maxState.hasRefreshButton).toBe(false);
    expect(bundled9maxState.hasLoadButton).toBe(true);
    expect(bundled9maxState.previewState).toBe('loaded');
    expect(sortStrings(bundled9maxState.previewActiveHands)).toEqual(sortStrings(EXPECTED_ANTE0_SOURCE_EXPANDED_CATEGORIES));
    expect(bundled9maxState.runtimeMetaScenarioLabel).toBe('9max / jam / no ante');
    expect(bundledCallState.sourceMode).toBe('bundle');
    expect(bundledCallState.familyBadgeText).toBe('10max');
    expect(bundledCallState.regimeBadgeText).toBe('call');
    expect(bundledCallState.anteBadgeText).toBe('BB ante');
    expect(bundledCallState.positionLabelText).toBe('Jam position');
    expect(bundledCallState.secondaryPositionLabelText).toBe('Caller position');
    expect(sortStrings(bundledCallState.previewActiveHands)).toEqual(sortStrings(EXPECTED_BB100_CALL_CATEGORIES));
    expect(bundledCallState.runtimeMetaScenarioLabel).toBe('10max / call / BB ante');
    expect(attemptedBridgeRequests).toHaveLength(0);
    expect(bundledAssetRequests.length).toBeGreaterThanOrEqual(1);
    expect(bundledAssetRequests.some(entry =>
      entry.url.includes('/poker-tools/assets/pushfold/aof-bundle.v1.json')
    )).toBe(true);
  } finally {
    await staticServer.close();
  }
});

test('served AOF page visibly retries and recovers with explicit ante selection', async ({ page, context }) => {
  test.setTimeout(90_000);

  const worktreeHtml = fs.readFileSync(INDEX_PATH, 'utf8');
  const worktreeSha = sha256(worktreeHtml);
  const stacksRequests = [];
  const stackLoadRequests = [];
  let stacksRouteMode = 'abort';

  await context.route(`${BRIDGE_BASE}/api/stacks*`, async route => {
    stacksRequests.push({
      index: stacksRequests.length + 1,
      mode: stacksRouteMode,
      url: route.request().url(),
      method: route.request().method(),
    });
    if (stacksRouteMode === 'delay_abort') {
      await sleep(600);
      await route.abort('failed');
      return;
    }
    if (stacksRouteMode === 'delay_allow') {
      await sleep(600);
      await route.continue();
      return;
    }
    await route.abort('failed');
  });
  page.on('request', request => {
    if (request.url().startsWith(`${BRIDGE_BASE}/api/stack?`)) {
      stackLoadRequests.push({
        url: request.url(),
        method: request.method(),
      });
    }
  });

  const response = await page.goto(SERVED_PAGE_URL, { waitUntil: 'domcontentloaded' });
  expect(response).not.toBeNull();
  const servedHtml = await response.text();
  expect(sha256(servedHtml)).toBe(worktreeSha);

  await expect(page.locator('#pushfold-refresh-btn')).toBeVisible();
  const hasRefreshFunction = await page.evaluate(() => typeof refreshPushfoldRuntimeBridge === 'function');
  expect(hasRefreshFunction).toBe(true);

  await expect(page.locator('#pushfold-bridge-status')).toHaveText(/bridge offline/);
  const initialOfflineState = await readState(page);

  stacksRouteMode = 'delay_abort';
  await page.locator('#pushfold-refresh-btn').click();
  const retryOneCheckingState = await readState(page);
  expect(/bridge checking \/ retry 1|bridge retry 1 failed/.test(retryOneCheckingState.statusText)).toBe(true);
  await expect(page.locator('#pushfold-bridge-status')).toHaveText(/bridge retry 1 failed/);
  await expect(page.locator('#pushfold-runtime-note')).toContainText('retry 1 failed');
  const retryOneFailedState = await readState(page);

  stacksRouteMode = 'delay_allow';
  await page.locator('#pushfold-refresh-btn').click();
  const retryTwoCheckingState = await readState(page);
  expect(/bridge checking \/ retry 2|bridge ready \/ retry 2 recovered/.test(retryTwoCheckingState.statusText)).toBe(true);
  await expect(page.locator('#pushfold-bridge-status')).toHaveText(/bridge ready \/ retry 2 recovered/);
  await expect(page.locator('#pushfold-load-btn')).toBeVisible();
  await expect(page.locator('#pushfold-range-preview')).toHaveAttribute('data-preview-state', 'ready');
  await expect(page.locator('#pushfold-family-select')).toBeVisible();
  await expect(page.locator('#pushfold-family-select')).toHaveValue('jennifear_9max_first_in');
  await expect(page.locator('#pushfold-family-badge')).toHaveText('9max');
  await expect(page.locator('#pushfold-regime-badge')).toHaveText('jam');
  await expect(page.locator('#pushfold-ante-badge')).toHaveText('no ante');
  await expect(page.locator('#pushfold-family-summary')).toContainText('Jennifear first-in');
  await expect(page.locator('#pushfold-range-preview-empty')).toContainText('13x13 matrix');
  await expect(page.locator('#pushfold-range-preview-empty')).toContainText('9max / jam / no ante');
  await expect(page.locator('#pushfold-regime-select')).toBeVisible();
  await expect(page.locator('#pushfold-regime-select')).toHaveValue('antes0');
  await expect(page.locator('#pushfold-scenario-details summary')).toHaveText('Details');
  const recoveredState = await readState(page);

  const regimeSwitchResponsePromise = page.waitForResponse(response =>
    response.url().startsWith(`${BRIDGE_BASE}/api/stacks?`)
    && response.url().includes(`regime=${encodeURIComponent(TARGET_NONZERO_REGIME)}`)
    && response.status() === 200
  );
  await page.selectOption('#pushfold-regime-select', TARGET_NONZERO_REGIME);
  const regimeSwitchPayload = await (await regimeSwitchResponsePromise).json();
  await expect(page.locator('#pushfold-regime-select')).toHaveValue(TARGET_NONZERO_REGIME);
  await expect(page.locator('#pushfold-family-select')).toHaveValue('jennifear_9max_first_in');
  await expect(page.locator('#pushfold-ante-badge')).toHaveText('10% ante');
  await expect(page.locator('#pushfold-range-preview-empty')).toContainText('9max / jam / 10% ante');
  const switchedRegimeState = await readState(page);

  await page.selectOption('#pushfold-stack-select', '11');
  await page.selectOption('#pushfold-position-select', 'UTG+2');
  await expect(page.locator('#pushfold-load-btn')).toBeEnabled();
  await expect(page.locator('#pushfold-runtime-note')).toContainText('load to show');
  const stackLoadResponsePromise = page.waitForResponse(response =>
    response.url().startsWith(`${BRIDGE_BASE}/api/stack?`) && response.status() === 200
  );
  await page.locator('#pushfold-load-btn').click();
  const stackLoadPayload = await (await stackLoadResponsePromise).json();
  await expect(page.locator('#pushfold-range-preview')).toHaveAttribute('data-preview-state', 'loaded');
  await expect(page.locator('#pushfold-range-preview-summary')).toContainText('11bb / UTG+2');
  await expect(page.locator('#pushfold-range-preview-summary')).toContainText('41 active');
  await expect(page.locator('#pushfold-range-preview-summary')).toContainText('9max / jam / 10% ante');
  await expect(page.locator('#pushfold-range-legend')).toContainText('active = jam included');
  await expect(page.locator('#pushfold-range-legend')).toContainText('mixed frequencies are not available');
  await expect(page.locator('#pushfold-open-preflop-btn')).toBeEnabled();
  await expect(page.locator('#pushfold-range-grid td.active-range')).toHaveCount(41);
  const loadedRangeState = await readState(page);

  await page.locator('#pushfold-open-preflop-btn').click();
  await expect(page.locator('#winrate-tab')).toHaveClass(/active/);
  await expect(page.locator('#range-grid td.active-range')).toHaveCount(41);
  const handedOffState = await readState(page);

  expect(stacksRequests.length).toBeGreaterThanOrEqual(5);
  expect(stacksRequests.some(entry => entry.mode === 'delay_abort')).toBe(true);
  expect(stacksRequests.some(entry => entry.mode === 'delay_allow')).toBe(true);
  expect(stackLoadRequests).toHaveLength(1);
  expect(regimeSwitchPayload.selectedRegime).toBe(TARGET_NONZERO_REGIME);
  expect(regimeSwitchPayload.semantics.ante).toBe('10%');
  expect(regimeSwitchPayload.semantics.sourceName).toBe('push72o_real_data_antes10');
  expect(recoveredState.familySelectValue).toBe('jennifear_9max_first_in');
  expect(recoveredState.familyOptionLabels).toEqual(expect.arrayContaining(['9max', '10max']));
  expect(recoveredState.familyBadgeText).toBe('9max');
  expect(recoveredState.regimeBadgeText).toBe('jam');
  expect(recoveredState.anteBadgeText).toBe('no ante');
  expect(recoveredState.familySummaryText).toContain('Jennifear first-in');
  expect(recoveredState.scenarioDetailsSummaryText).toBe('Details');
  expect(recoveredState.scenarioDetailsText).toContain('Jennifear');
  expect(switchedRegimeState.regimeSelectValue).toBe(TARGET_NONZERO_REGIME);
  expect(switchedRegimeState.regimeOptionLabels).toEqual(expect.arrayContaining([
    'jam · no ante',
    'jam · 10% ante',
    'jam · 12.5% ante',
    'jam · 20% ante',
  ]));
  expect(switchedRegimeState.regimeOptionLabels).not.toContain('jam · BB ante');
  expect(switchedRegimeState.regimeOptionLabels).not.toContain('call · BB ante');
  expect(switchedRegimeState.anteBadgeText).toBe('10% ante');
  expect(switchedRegimeState.noteText).toContain('9max / jam / 10% ante selected');
  expect(stackLoadPayload.selectedRegime).toBe(TARGET_NONZERO_REGIME);
  expect(stackLoadPayload.semantics.ante).toBe('10%');
  expect(stackLoadPayload.semantics.sourceName).toBe('push72o_real_data_antes10');
  expect(stackLoadPayload.categoryCount).toBe(41);
  expect(stackLoadPayload.categories).toEqual(EXPECTED_ANTES10_SOURCE_EXPANDED_CATEGORIES);
  expect(stackLoadPayload.categories).not.toEqual(EXPECTED_ANTE0_SOURCE_EXPANDED_CATEGORIES);
  expect(loadedRangeState.previewLoadedCategoryCount).toBe(41);
  expect(loadedRangeState.previewLoadedLabel).toBe('11bb / UTG+2');
  expect(sortStrings(loadedRangeState.previewCategoryTexts)).toEqual(sortStrings(EXPECTED_ANTES10_SOURCE_EXPANDED_CATEGORIES));
  expect(sortStrings(loadedRangeState.previewActiveHands)).toEqual(sortStrings(EXPECTED_ANTES10_SOURCE_EXPANDED_CATEGORIES));
  expect(loadedRangeState.familyBadgeText).toBe('9max');
  expect(loadedRangeState.regimeBadgeText).toBe('jam');
  expect(loadedRangeState.anteBadgeText).toBe('10% ante');
  expect(loadedRangeState.runtimeMetaScenarioLabel).toBe('9max / jam / 10% ante');
  expect(loadedRangeState.runtimeSelectedText).toContain('11bb / UTG+2');
  expect(loadedRangeState.runtimeLoadedText).toContain('11bb / UTG+2');
  expect(loadedRangeState.previewActiveCount).toBe(41);
  expect(loadedRangeState.sharedRangeActiveCount).toBe(41);
  expect(loadedRangeState.previewLegendText).toContain('inactive = excluded from this source range');
  expect(parseFloat(loadedRangeState.activeCellOpacity)).toBeGreaterThan(parseFloat(loadedRangeState.inactiveCellOpacity));
  expect(handedOffState.activeTabId).toBe('winrate-tab');
  expect(handedOffState.sharedRangeActiveCount).toBe(41);

  console.log(JSON.stringify({
    status: 'ok',
    servedPageUrl: SERVED_PAGE_URL,
    bridgeBase: BRIDGE_BASE,
    servedPageMatchesWorktree: true,
    hasRefreshFunction,
    stacksRequests,
    initialOfflineState,
    retryOneCheckingState,
    retryOneFailedState,
    retryTwoCheckingState,
    recoveredState,
    regimeSwitchPayload,
    switchedRegimeState,
    stackLoadRequests,
    stackLoadPayload,
    loadedRangeState,
    handedOffState,
  }, null, 2));
});

test('served AOF page supports BB ante shove and call regimes from the official tool source', async ({ page }) => {
  test.setTimeout(90_000);

  const response = await page.goto(SERVED_PAGE_URL, { waitUntil: 'domcontentloaded' });
  expect(response).not.toBeNull();

  await expect(page.locator('#pushfold-bridge-status')).toHaveText(/bridge ready/);
  await expect(page.locator('#pushfold-family-select')).toHaveValue('jennifear_9max_first_in');
  await expect(page.locator('#pushfold-regime-select')).toBeVisible();
  await expect(page.locator('#pushfold-family-badge')).toHaveText('9max');
  await expect(page.locator('#pushfold-regime-badge')).toHaveText('jam');
  await expect(page.locator('#pushfold-family-summary')).toContainText('Jennifear first-in');

  await page.selectOption('#pushfold-stack-select', '11');
  await page.selectOption('#pushfold-position-select', 'UTG+2');
  const initial9maxLoadResponsePromise = page.waitForResponse(candidate =>
    candidate.url().startsWith(`${BRIDGE_BASE}/api/stack?`)
    && candidate.url().includes(`regime=${encodeURIComponent('antes0')}`)
    && candidate.status() === 200
  );
  await page.locator('#pushfold-load-btn').click();
  const initial9maxLoadPayload = await (await initial9maxLoadResponsePromise).json();
  await expect(page.locator('#pushfold-range-preview')).toHaveAttribute('data-preview-state', 'loaded');
  await expect(page.locator('#pushfold-range-preview-summary')).toContainText('26 active');
  await expect(page.locator('#pushfold-range-preview-summary')).toContainText('9max / jam / no ante');
  const initial9maxState = await readState(page);

  const toolFamilySwitchResponsePromise = page.waitForResponse(candidate =>
    candidate.url().startsWith(`${BRIDGE_BASE}/api/stacks?`)
    && candidate.url().includes(`regime=${encodeURIComponent(TARGET_BBANTE_OPENJAM_REGIME)}`)
    && candidate.status() === 200
  );
  await page.selectOption('#pushfold-family-select', 'push72o_tool_10max_bbante');
  const toolRegimeSwitchPayload = await (await toolFamilySwitchResponsePromise).json();
  await expect(page.locator('#pushfold-family-select')).toHaveValue('push72o_tool_10max_bbante');
  await expect(page.locator('#pushfold-family-badge')).toHaveText('10max');
  await expect(page.locator('#pushfold-regime-badge')).toHaveText('jam');
  await expect(page.locator('#pushfold-ante-badge')).toHaveText('BB ante');
  await expect(page.locator('#pushfold-family-summary')).toContainText('Push72o BB-ante');
  await expect(page.locator('#pushfold-runtime-note')).toContainText('10max / jam / BB ante selected / preview cleared');
  await expect(page.locator('#pushfold-range-preview')).toHaveAttribute('data-preview-state', 'ready');
  await expect(page.locator('#pushfold-range-grid')).toHaveCount(0);
  await expect(page.locator('#pushfold-regime-select')).toHaveValue(TARGET_BBANTE_OPENJAM_REGIME);
  await expect(page.locator('#pushfold-regime-select')).not.toContainText('jam · 10% ante');
  await expect(page.locator('#pushfold-position-select')).toHaveValue('UTG');
  await expect(page.locator('#pushfold-secondary-position-select')).toHaveCount(0);

  await page.selectOption('#pushfold-stack-select', '11');
  await page.selectOption('#pushfold-position-select', 'UTG+2');
  const bbOpenJamResponsePromise = page.waitForResponse(candidate =>
    candidate.url().startsWith(`${BRIDGE_BASE}/api/stack?`)
    && candidate.url().includes(`regime=${encodeURIComponent(TARGET_BBANTE_OPENJAM_REGIME)}`)
    && candidate.status() === 200
  );
  await page.locator('#pushfold-load-btn').click();
  const bbOpenJamPayload = await (await bbOpenJamResponsePromise).json();
  await expect(page.locator('#pushfold-range-preview-summary')).toContainText('11bb / UTG+2');
  await expect(page.locator('#pushfold-range-preview-summary')).toContainText('37 active');
  await expect(page.locator('#pushfold-range-preview-summary')).toContainText('10max / jam / BB ante');
  await expect(page.locator('#pushfold-range-legend')).toContainText('active = jam included');
  await expect(page.locator('#pushfold-range-grid td.active-range')).toHaveCount(37);
  const bbOpenJamState = await readState(page);

  const callRegimeSwitchResponsePromise = page.waitForResponse(candidate =>
    candidate.url().startsWith(`${BRIDGE_BASE}/api/stacks?`)
    && candidate.url().includes(`regime=${encodeURIComponent(TARGET_CALL_REGIME)}`)
    && candidate.status() === 200
  );
  await page.selectOption('#pushfold-regime-select', TARGET_CALL_REGIME);
  const callRegimeSwitchPayload = await (await callRegimeSwitchResponsePromise).json();
  await expect(page.locator('#pushfold-regime-badge')).toHaveText('call');
  await expect(page.locator('#pushfold-runtime-note')).toContainText('10max / call / BB ante selected / preview cleared');
  await expect(page.locator('#pushfold-secondary-position-select')).toBeVisible();
  await expect(page.locator('#pushfold-secondary-position-select')).toHaveValue('UTG');

  await page.selectOption('#pushfold-stack-select', '11');
  await page.selectOption('#pushfold-position-select', 'UTG+2');
  await expect(page.locator('#pushfold-secondary-position-select')).toBeVisible();
  await page.selectOption('#pushfold-secondary-position-select', 'UTG+1');
  const callLoadResponsePromise = page.waitForResponse(candidate =>
    candidate.url().startsWith(`${BRIDGE_BASE}/api/stack?`)
    && candidate.url().includes(`regime=${encodeURIComponent(TARGET_CALL_REGIME)}`)
    && candidate.url().includes('secondaryPosition=UTG%2B1')
    && candidate.status() === 200
  );
  await page.locator('#pushfold-load-btn').click();
  const callLoadPayload = await (await callLoadResponsePromise).json();
  await expect(page.locator('#pushfold-range-preview-summary')).toContainText('11bb / jam UTG+2 / caller UTG+1');
  await expect(page.locator('#pushfold-range-preview-summary')).toContainText('13 active');
  await expect(page.locator('#pushfold-range-preview-summary')).toContainText('10max / call / BB ante');
  await expect(page.locator('#pushfold-range-legend')).toContainText('active = call included');
  await expect(page.locator('#pushfold-range-grid td.active-range')).toHaveCount(13);
  const bbCallState = await readState(page);

  await page.locator('#pushfold-open-preflop-btn').click();
  await expect(page.locator('#winrate-tab')).toHaveClass(/active/);
  await expect(page.locator('#range-grid td.active-range')).toHaveCount(13);

  expect(initial9maxLoadPayload.selectedRegime).toBe('antes0');
  expect(initial9maxLoadPayload.categories).toEqual(EXPECTED_ANTE0_SOURCE_EXPANDED_CATEGORIES);
  expect(initial9maxState.familyBadgeText).toBe('9max');
  expect(initial9maxState.regimeBadgeText).toBe('jam');
  expect(initial9maxState.anteBadgeText).toBe('no ante');
  expect(initial9maxState.previewActiveCount).toBe(26);
  expect(toolRegimeSwitchPayload.selectedRegime).toBe(TARGET_BBANTE_OPENJAM_REGIME);
  expect(toolRegimeSwitchPayload.semantics.familyId).toBe('push72o_tool_10max_bbante');
  expect(toolRegimeSwitchPayload.semantics.anteType).toBe('big_blind');
  expect(toolRegimeSwitchPayload.semantics.anteSize).toBe('100% BB');
  expect(toolRegimeSwitchPayload.semantics.sourceBucketAnte).toBe('10% antes');
  expect(bbOpenJamPayload.selectedRegime).toBe(TARGET_BBANTE_OPENJAM_REGIME);
  expect(bbOpenJamPayload.categoryCount).toBe(37);
  expect(bbOpenJamPayload.categories).toEqual(EXPECTED_BB100_OPENJAM_CATEGORIES);
  expect(sortStrings(bbOpenJamState.previewCategoryTexts)).toEqual(sortStrings(EXPECTED_BB100_OPENJAM_CATEGORIES));
  expect(sortStrings(bbOpenJamState.previewActiveHands)).toEqual(sortStrings(EXPECTED_BB100_OPENJAM_CATEGORIES));
  expect(bbOpenJamState.familyBadgeText).toBe('10max');
  expect(bbOpenJamState.regimeBadgeText).toBe('jam');
  expect(bbOpenJamState.anteBadgeText).toBe('BB ante');
  expect(bbOpenJamState.familyOptionLabels).toEqual(expect.arrayContaining(['9max', '10max']));
  expect(bbOpenJamState.regimeOptionLabels).toEqual(expect.arrayContaining(['jam · BB ante', 'call · BB ante']));
  expect(bbOpenJamState.positionLabelText).toBe('Position');
  expect(bbOpenJamState.runtimeMetaScenarioLabel).toBe('10max / jam / BB ante');
  expect(bbOpenJamState.previewActiveCount).toBe(37);
  expect(bbOpenJamState.sharedRangeActiveCount).toBe(37);

  expect(callRegimeSwitchPayload.selectedRegime).toBe(TARGET_CALL_REGIME);
  expect(callRegimeSwitchPayload.semantics.familyId).toBe('push72o_tool_10max_bbante');
  expect(callRegimeSwitchPayload.semantics.rangeMode).toBe('call_vs_jam');
  expect(callRegimeSwitchPayload.semantics.secondaryPositionRole).toBe('caller_position');
  expect(bbCallState.familyBadgeText).toBe('10max');
  expect(bbCallState.regimeBadgeText).toBe('call');
  expect(bbCallState.anteBadgeText).toBe('BB ante');
  expect(bbCallState.positionLabelText).toBe('Jam position');
  expect(bbCallState.secondaryPositionLabelText).toBe('Caller position');
  expect(bbCallState.secondaryPositionOptionLabels).toEqual(expect.arrayContaining(['UTG', 'UTG+1']));
  expect(callLoadPayload.selectedRegime).toBe(TARGET_CALL_REGIME);
  expect(callLoadPayload.secondaryPosition).toBe('UTG+1');
  expect(callLoadPayload.categoryCount).toBe(13);
  expect(callLoadPayload.categories).toEqual(EXPECTED_BB100_CALL_CATEGORIES);
  expect(sortStrings(bbCallState.previewCategoryTexts)).toEqual(sortStrings(EXPECTED_BB100_CALL_CATEGORIES));
  expect(sortStrings(bbCallState.previewActiveHands)).toEqual(sortStrings(EXPECTED_BB100_CALL_CATEGORIES));
  expect(bbCallState.previewActiveCount).toBe(13);
  expect(bbCallState.sharedRangeActiveCount).toBe(13);
  expect(bbCallState.runtimeMetaScenarioLabel).toBe('10max / call / BB ante');
  expect(bbCallState.previewLegendText).toContain('active = call included');
});
