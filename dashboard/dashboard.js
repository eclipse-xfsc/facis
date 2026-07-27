const HEALTH_LABEL = { green: 'Healthy', yellow: 'Needs Attention', red: 'Broken', unknown: 'Unknown' };
const HEALTH_EMOJI = { green: '\u{1F7E2}', yellow: '\u{1F7E1}', red: '\u{1F534}', unknown: '\u26AA' };
const GOV_LABEL = { license: 'License', contributing: 'Contributing', readme: 'README' };
const ICON_SVG = {
  root: `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-6">
  <path stroke-linecap="round" stroke-linejoin="round" d="M3.75 3v11.25A2.25 2.25 0 0 0 6 16.5h2.25M3.75 3h-1.5m1.5 0h16.5m0 0h1.5m-1.5 0v11.25A2.25 2.25 0 0 1 18 16.5h-2.25m-7.5 0h7.5m-7.5 0-1 3m8.5-3 1 3m0 0 .5 1.5m-.5-1.5h-9.5m0 0-.5 1.5M9 11.25v1.5M12 9v3.75m3-6v6" />
</svg>
`,
  dcs: `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 0 0-3.375-3.375h-1.5A1.125 1.125 0 0 1 13.5 7.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 0 0-9-9Z" /></svg>`,
  dcm: `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-6">
  <path stroke-linecap="round" stroke-linejoin="round" d="M20.25 6.375c0 2.278-3.694 4.125-8.25 4.125S3.75 8.653 3.75 6.375m16.5 0c0-2.278-3.694-4.125-8.25-4.125S3.75 4.097 3.75 6.375m16.5 0v11.25c0 2.278-3.694 4.125-8.25 4.125s-8.25-1.847-8.25-4.125V6.375m16.5 0v3.75m-16.5-3.75v3.75m16.5 0v3.75C20.25 16.153 16.556 18 12 18s-8.25-1.847-8.25-4.125v-3.75m16.5 0c0 2.278-3.694 4.125-8.25 4.125s-8.25-1.847-8.25-4.125" />
</svg>
`,
  'iot-ai': `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M8.25 3v1.5M4.5 8.25H3m18 0h-1.5M4.5 12H3m18 0h-1.5m-15 3.75H3m18 0h-1.5M8.25 19.5V21M12 3v1.5m0 15V21m3.75-18v1.5m0 15V21m-9-1.5h10.5a2.25 2.25 0 0 0 2.25-2.25V6.75a2.25 2.25 0 0 0-2.25-2.25H6.75A2.25 2.25 0 0 0 4.5 6.75v10.5a2.25 2.25 0 0 0 2.25 2.25Zm.75-12h9v9h-9v-9Z" /></svg>`,
  'partner-onboarding': `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M15 19.128a9.38 9.38 0 0 0 2.625.372 9.337 9.337 0 0 0 4.121-.952 4.125 4.125 0 0 0-7.533-2.493M15 19.128v-.003c0-1.113-.285-2.16-.786-3.07M15 19.128v.106A12.318 12.318 0 0 1 8.624 21c-2.331 0-4.512-.645-6.374-1.766l-.001-.109a6.375 6.375 0 0 1 11.964-3.07M12 6.375a3.375 3.375 0 1 1-6.75 0 3.375 3.375 0 0 1 6.75 0Zm8.25 2.25a2.625 2.625 0 1 1-5.25 0 2.625 2.625 0 0 1 5.25 0Z" /></svg>`,
  'aviation-poc': `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M6 12 3.269 3.125A59.769 59.769 0 0 1 21.485 12 59.768 59.768 0 0 1 3.27 20.875L5.999 12Zm0 0h7.5" /></svg>`,
  'credential-issuance': `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M15 9h3.75M15 12h3.75M15 15h3.75M4.5 19.5h15a2.25 2.25 0 0 0 2.25-2.25V6.75A2.25 2.25 0 0 0 19.5 4.5h-15a2.25 2.25 0 0 0-2.25 2.25v10.5A2.25 2.25 0 0 0 4.5 19.5Zm6-10.125a1.875 1.875 0 1 1-3.75 0 1.875 1.875 0 0 1 3.75 0Zm1.294 6.336a6.721 6.721 0 0 1-3.17.789 6.721 6.721 0 0 1-3.168-.789 3.376 3.376 0 0 1 6.338 0Z" /></svg>`,
  default: `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M20.25 7.5l-.625 10.632a2.25 2.25 0 0 1-2.247 2.118H6.622a2.25 2.25 0 0 1-2.247-2.118L3.75 7.5M10 11.25h4M3.375 7.5h17.25c.621 0 1.125-.504 1.125-1.125v-1.5c0-.621-.504-1.125-1.125-1.125H3.375c-.621 0-1.125.504-1.125 1.125v1.5c0 .621.504 1.125 1.125 1.125Z" /></svg>`,
};

function renderSummary(repos) {
  const counts = { green: 0, yellow: 0, red: 0, unknown: 0 };
  repos.forEach(r => counts[r.health || 'unknown']++);
  document.getElementById('summary').innerHTML = Object.entries(counts)
    .filter(([k, v]) => v > 0 || k === 'red')
    .map(([k, v]) => `<div class="stat ${k}"><b>${v}</b><span>${HEALTH_LABEL[k]}</span></div>`)
    .join('');
}

function timeAgo(iso) {
  if (!iso) return null;
  const ms = Date.now() - new Date(iso).getTime();
  const h = Math.floor(ms / 3600000);
  if (h < 1) return 'just now';
  if (h < 24) return `${h}h ago`;
  return `${Math.floor(h / 24)}d ago`;
}

function daysAgoText(days) {
  if (days == null) return 'unknown';
  if (days === 0) return 'today';
  if (days === 1) return '1 day ago';
  return `${days} days ago`;
}

function trendBadge(t) {
  if (!t || t.direction === 'stable') return '';
  const arrow = t.direction === 'up' ? '\u2191' : '\u2193';
  const sign = t.delta > 0 ? '+' : '';
  return ` <span class="trend ${t.sentiment}">${arrow} ${sign}${t.delta} this week</span>`;
}

function ciStatusText(r) {
  if (r.currentlyFailingWorkflows && r.currentlyFailingWorkflows.length) {
    return `\u274C Failed \u2014 ${r.currentlyFailingWorkflows.join(', ')}`;
  }
  if (r.ciLastRunStatus === 'success') return `\u2705 Passed ${r.ciLastRunAt ? `(${timeAgo(r.ciLastRunAt)})` : ''}`;
  if (r.ciLastRunStatus === 'failure') return `\u274C Failed ${r.ciLastRunAt ? `(${timeAgo(r.ciLastRunAt)})` : ''}`;
  if (r.ciLastRunStatus === 'pending') return '\u23F3 Pending';
  return 'No runs recorded';
}

function weekTrendText(counts) {
  if (!counts || counts.length < 6) return '<b>Not enough data</b>';
  const firstHalf = counts.slice(0, 3).reduce((a, b) => a + b, 0);
  const secondHalf = counts.slice(4, 7).reduce((a, b) => a + b, 0);
  if (secondHalf < firstHalf) return '<b><span class="trend good">\u2193 Improving</span></b>';
  if (secondHalf > firstHalf) return '<b><span class="trend bad">\u2191 Worsening</span></b>';
  return '<b><span class="trend neutral">\u2192 Stable</span></b>';
}

function failureColor(count, max) {
  if (count === 0) return '#9aa0a8';
  const t = count / max;
  const light = [241, 148, 138];
  const dark = [123, 36, 28];
  const rgb = light.map((c, i) => Math.round(c + (dark[i] - c) * t));
  return `rgb(${rgb[0]},${rgb[1]},${rgb[2]})`;
}

function renderTrendLine(counts, key) {
  if (!counts || counts.length < 2) return '';
  const max = Math.max(1, ...counts);
  const w = 100, h = 30, padTop = 3, padBottom = 3;
  const stepX = w / (counts.length - 1);
  const points = counts.map((c, i) => [i * stepX, h - padBottom - (c / max) * (h - padTop - padBottom)]);

  let lineD = `M ${points[0][0].toFixed(1)} ${points[0][1].toFixed(1)}`;
  for (let i = 0; i < points.length - 1; i++) {
    const p0 = points[i === 0 ? i : i - 1];
    const p1 = points[i];
    const p2 = points[i + 1];
    const p3 = points[i + 2 < points.length ? i + 2 : i + 1];
    const c1x = p1[0] + (p2[0] - p0[0]) / 6;
    const c1y = p1[1] + (p2[1] - p0[1]) / 6;
    const c2x = p2[0] - (p3[0] - p1[0]) / 6;
    const c2y = p2[1] - (p3[1] - p1[1]) / 6;
    lineD += ` C ${c1x.toFixed(1)} ${c1y.toFixed(1)} ${c2x.toFixed(1)} ${c2y.toFixed(1)} ${p2[0].toFixed(1)} ${p2[1].toFixed(1)}`;
  }
  const areaD = `${lineD} L ${points[points.length - 1][0].toFixed(1)} ${h} L ${points[0][0].toFixed(1)} ${h} Z`;

  const gradId = `lineGrad-${key}`;
  const areaGradId = `areaGrad-${key}`;
  const stops = points.map((p, i) => {
    const offsetPct = ((p[0] / w) * 100).toFixed(1);
    return `<stop offset="${offsetPct}%" stop-color="${failureColor(counts[i], max)}"></stop>`;
  }).join('');

  const peakColor = failureColor(max, max);
  const dots = points.map((p, i) =>
    `<circle cx="${p[0].toFixed(1)}" cy="${p[1].toFixed(1)}" r="1.8" fill="${failureColor(counts[i], max)}"></circle>`
  ).join('');

  return `
    <div class="sparkline">
      <div class="chart-caption">Failed CI runs per day</div>
      <svg viewBox="0 0 ${w} ${h}" class="spark-svg" preserveAspectRatio="none">
        <defs>
          <linearGradient id="${gradId}" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="${w}" y2="0">${stops}</linearGradient>
          <linearGradient id="${areaGradId}" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stop-color="${peakColor}" stop-opacity="0.3"></stop>
            <stop offset="100%" stop-color="${peakColor}" stop-opacity="0"></stop>
          </linearGradient>
        </defs>
        <path d="${areaD}" fill="url(#${areaGradId})" stroke="none"></path>
        <path d="${lineD}" fill="none" stroke="url(#${gradId})" stroke-width="1.8" stroke-linecap="round"></path>
        ${dots}
      </svg>
      <div class="chart-x-axis"><span>Day 1</span><span>Day 7</span></div>
    </div>
  `;
}

function renderCard(r) {
  if (r.error) {
    return `<div class="card unknown"><div class="card-header"><div class="card-header-left"><h2>${r.label}</h2></div></div><div class="card-body"><div class="row"><span>Fetch error</span></div><div class="row"><b>${r.error}</b></div></div></div>`;
  }

  const alerts = [];
  if (r.daysSinceLastCommit != null && r.daysSinceLastCommit > 90) {
    alerts.push(`Last commit: ${r.daysSinceLastCommit} days ago \u26A0\uFE0F (stale)`);
  }
  if (r.currentlyFailingWorkflows && r.currentlyFailingWorkflows.length) {
    alerts.push(`Currently failing: ${r.currentlyFailingWorkflows.join(', ')}`);
  }


  const govChips = Object.entries(r.governanceFiles || {}).map(([k, present]) => `
    <span class="chip ${present ? 'yes' : 'no'}">${present ? '\u2713' : '\u2717'} ${GOV_LABEL[k]}</span>
  `).join('');

  return `
    <div class="card ${r.health}">
      <div class="card-header">
        <div class="card-header-left">
          <span class="card-icon">${ICON_SVG[r.key] || ICON_SVG.default}</span>
          <h2><a href="${r.url}" target="_blank" rel="noopener">${r.label}</a></h2>
        </div>
        <div class="card-status">${HEALTH_EMOJI[r.health]} ${HEALTH_LABEL[r.health] || 'Unknown'}</div>
      </div>
      <div class="card-body">
        ${alerts.length ? `<div class="section">${alerts.map(a => `<div class="alert-box">${a}</div>`).join('')}</div>` : ''}

        <div class="section">
          <div class="section-title">Activity</div>
          <div class="row"><span>Last commit</span><b class="${r.daysSinceLastCommit > 90 ? 'stale' : ''}">${daysAgoText(r.daysSinceLastCommit)}</b></div>
          <div class="row"><span>Open PRs</span><b class="${r.openHumanPRCount > 0 ? 'value-bad' : ''}">${r.openHumanPRCount ?? '?'} PR${r.openHumanPRCount === 1 ? '' : 's'}</b></div>
        </div>

        <div class="section">
          <div class="section-title">Quality</div>
          <div class="row"><span>CI Status</span><b>${ciStatusText(r)}</b></div>
          <div class="row"><span>Historical</span><b class="${(r.ciRecentFailureCount ?? 0) > 0 ? 'value-bad' : ''}">${r.ciRecentFailureCount ?? 0} failures in 7d</b></div>
          <div class="row"><span>Trend</span>${weekTrendText(r.ciFailuresByDay)}</div>
          ${renderTrendLine(r.ciFailuresByDay, r.key)}
        </div>

        <div class="section">
          <div class="section-title">Community</div>
          <div class="row"><span>Contributors</span><b>${r.contributorCount ?? '?'}${trendBadge(r.trends?.contributorCount)}</b></div>
          <div class="row"><span>Open issues</span><b>${r.openIssueCount ?? '?'}${trendBadge(r.trends?.openIssueCount)}</b></div>
        </div>

        <div class="section">
          <div class="section-title">Governance (${r.governanceScore ?? 0}/${Object.keys(r.governanceFiles || {}).length})</div>
          <div class="chip-row">${govChips}</div>
        </div>
      </div>
    </div>
  `;
}

fetch('./status.json')
  .then(r => r.json())
  .then(data => {
    document.getElementById('meta').textContent = 'Last updated: ' + new Date(data.generatedAt).toLocaleString();
    renderSummary(data.repos);
    document.getElementById('grid').innerHTML = data.repos.map(renderCard).join('');
  })
  .catch(err => {
    document.getElementById('meta').textContent = 'Failed to load status.json: ' + err;
  });
