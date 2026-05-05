import React, { useEffect, useMemo, useState } from 'react';

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const navItems = [
  ['Overview', 'overview'],
  ['Seasonality', 'seasonality'],
  ['Periodicity', 'periodicity'],
  ['Correlations', 'correlations'],
  ['Clusters', 'clusters'],
  ['Forecasting', 'forecasting'],
];

function formatNumber(value, options = {}) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return '0';
  return new Intl.NumberFormat('en-US', options).format(Number(value));
}

function compactNumber(value) {
  return formatNumber(value, { notation: 'compact', maximumFractionDigits: 1 });
}

function toPercent(value) {
  return `${formatNumber((value || 0) * 100, { maximumFractionDigits: 0 })}%`;
}

function average(items, key) {
  const values = items.map((item) => Number(item[key])).filter(Number.isFinite);
  return values.length ? values.reduce((sum, value) => sum + value, 0) / values.length : 0;
}

function maxItem(items, key) {
  return items.reduce((best, item) => (Number(item[key]) > Number(best?.[key] || -Infinity) ? item : best), null);
}

function monthShort(value) {
  return String(value || '').slice(0, 3);
}

const FEATURE_UNITS = {
  hour: 'hour',
  temperature: 'deg C',
  humidity: '%',
  wind_speed: 'm/s',
  visibility: 'm',
  dew_point_temperature: 'deg C',
  solar_radiation: 'MJ/m2',
  rainfall: 'mm',
  snowfall: 'cm',
};

const YEAR_COLORS = {
  2017: '#0f766e',
  2018: '#4f46e5',
  2019: '#f43f5e',
};

function yearColor(year, fallback = '#4f46e5') {
  return YEAR_COLORS[year] || fallback;
}

function yearsIn(data, key = 'year') {
  return [...new Set((data || []).map((item) => item[key]).filter(Boolean))];
}

async function fetchJson(path) {
  const response = await fetch(`${API_BASE}${path}`);
  if (!response.ok) throw new Error(`Request failed: ${path}`);
  return response.json();
}

function useApi(path, initialValue) {
  const [data, setData] = useState(initialValue);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    let active = true;
    setLoading(true);
    fetchJson(path)
      .then((payload) => {
        if (active) {
          setData(payload);
          setError('');
        }
      })
      .catch((err) => {
        if (active) setError(err.message);
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
    };
  }, [path]);

  return { data, loading, error };
}

function Card({ children, className = '', style = {} }) {
  return <section className={`card ${className}`} style={{ background: '#ffffff', borderRadius: '16px', padding: '1.5rem', boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -2px rgba(0, 0, 0, 0.05)', border: '1px solid #e2e8f0', overflow: 'hidden', ...style }}>{children}</section>;
}

function EmptyState({ message = 'No data available yet.' }) {
  return <div className="empty-state" style={{ padding: '3rem', textAlign: 'center', color: '#64748b', background: '#f8fafc', borderRadius: '12px', border: '2px dashed #cbd5e1' }}>{message}</div>;
}

function MetricCard({ label, value, detail, tone = 'blue' }) {
  const toneColors = {
    blue: { bg: '#eff6ff', text: '#1e40af', detail: '#3b82f6', border: '#bfdbfe' },
    teal: { bg: '#f0fdfa', text: '#115e59', detail: '#14b8a6', border: '#ccfbf1' },
    rose: { bg: '#fff1f2', text: '#9f1239', detail: '#f43f5e', border: '#fecdd3' },
    violet: { bg: '#f5f3ff', text: '#5b21b6', detail: '#8b5cf6', border: '#ede9fe' },
  };
  const colors = toneColors[tone] || toneColors.blue;

  return (
    <Card className={`metric metric-${tone}`} style={{ backgroundColor: colors.bg, borderColor: colors.border, display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
      <div className="metric-label" style={{ color: colors.text, fontSize: '0.875rem', fontWeight: '700', textTransform: 'uppercase', letterSpacing: '0.05em', opacity: 0.8 }}>{label}</div>
      <div className="metric-value" style={{ color: colors.text, fontSize: '2.25rem', fontWeight: '700', margin: '0.75rem 0', lineHeight: 1 }}>{value}</div>
      <div className="metric-detail" style={{ color: colors.detail, fontSize: '0.875rem', fontWeight: '600' }}>{detail}</div>
    </Card>
  );
}

function ChartFrame({ title, action, children }) {
  return (
    <Card className="chart-frame" style={{ display: 'flex', flexDirection: 'column' }}>
      <div className="card-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem', borderBottom: '1px solid #f1f5f9', paddingBottom: '1rem' }}>
        <h3 style={{ margin: 0, fontSize: '1.125rem', fontWeight: '600', color: '#0f172a' }}>{title}</h3>
        {action && <div style={{ fontSize: '0.875rem' }}>{action}</div>}
      </div>
      <div style={{ flex: 1, minHeight: 0 }}>
        {children}
      </div>
    </Card>
  );
}

function InsightCard({ label, value, detail }) {
  return (
    <div className="insight-card" style={{ display: 'flex', flexDirection: 'column', padding: '1rem', background: '#f8fafc', borderRadius: '8px', border: '1px solid #e2e8f0', flex: 1 }}>
      <span style={{ fontSize: '0.75rem', color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.05em', fontWeight: '700', marginBottom: '0.25rem' }}>{label}</span>
      <strong style={{ fontSize: '1.25rem', color: '#0f172a', lineHeight: '1.2' }}>{value}</strong>
      <small style={{ fontSize: '0.875rem', color: '#475569', marginTop: '0.25rem' }}>{detail}</small>
    </div>
  );
}

function PageStory({ eyebrow, title, children, meta }) {
  return (
    <section className="page-story" style={{ display: 'flex', flexWrap: 'wrap', gap: '2rem', alignItems: 'flex-start', background: '#ffffff', padding: '2rem', borderRadius: '16px', border: '1px solid #e2e8f0', borderLeft: '6px solid #3b82f6', marginBottom: '1.5rem', boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.05)' }}>
      <div style={{ flex: '1 1 500px' }}>
        <span style={{ fontSize: '0.875rem', fontWeight: '700', color: '#3b82f6', textTransform: 'uppercase', letterSpacing: '0.05em' }}>{eyebrow}</span>
        <h2 style={{ fontSize: '1.75rem', fontWeight: '700', color: '#0f172a', margin: '0.5rem 0 1rem 0', lineHeight: '1.3' }}>{title}</h2>
        <p style={{ color: '#475569', fontSize: '1.05rem', lineHeight: '1.6', margin: 0 }}>{children}</p>
      </div>
      {meta && <div className="story-meta" style={{ flex: '0 1 auto', display: 'flex', gap: '1rem', minWidth: '300px' }}>{meta}</div>}
    </section>
  );
}

function DateControls({ startDate, endDate, setStartDate, setEndDate }) {
  return (
    <div className="date-controls" style={{ display: 'flex', gap: '0.75rem', marginBottom: '2rem', alignItems: 'center' }}>
      <input type="date" min="2017-12-01" max={endDate} value={startDate} onChange={(event) => setStartDate(event.target.value)} style={{ padding: '0.5rem 0.75rem', border: '1px solid #cbd5e1', borderRadius: '8px', color: '#0f172a', background: '#ffffff', cursor: 'pointer', fontSize: '0.875rem', fontWeight: '500', boxShadow: '0 1px 2px rgba(0,0,0,0.05)' }} />
      <span style={{ color: '#94a3b8', fontWeight: '500' }}>&rarr;</span>
      <input type="date" min={startDate} max="2018-11-30" value={endDate} onChange={(event) => setEndDate(event.target.value)} style={{ padding: '0.5rem 0.75rem', border: '1px solid #cbd5e1', borderRadius: '8px', color: '#0f172a', background: '#ffffff', cursor: 'pointer', fontSize: '0.875rem', fontWeight: '500', boxShadow: '0 1px 2px rgba(0,0,0,0.05)' }} />
    </div>
  );
}

function Legend({ items }) {
  return (
    <div className="legend" style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
      {items.map((item) => (
        <span key={item.label} style={{ display: 'flex', alignItems: 'center', gap: '0.375rem', fontSize: '0.875rem', color: '#475569', fontWeight: '500' }}>
          <i style={{ background: item.color, width: '10px', height: '10px', borderRadius: '50%', display: 'inline-block' }} />
          {item.label}
        </span>
      ))}
    </div>
  );
}

function SvgChart({ children, height = 250 }) {
  return (
    <svg className="chart-svg" viewBox={`0 0 720 ${height}`} role="img" aria-hidden="true" style={{ width: '100%', height: 'auto', display: 'block', overflow: 'visible' }}>
      {children}
    </svg>
  );
}

function LineChart({ data, xKey, lines, height = 260 }) {
  if (!data?.length) return <EmptyState />;
  const width = 720;
  const pad = { top: 20, right: 28, bottom: 34, left: 48 };
  const plotWidth = width - pad.left - pad.right;
  const plotHeight = height - pad.top - pad.bottom;
  const values = data.flatMap((item) => lines.map((line) => Number(item[line.key])).filter(Number.isFinite));
  const min = Math.min(...values, 0);
  const max = Math.max(...values, 1);
  const scaleX = (index) => pad.left + (index / Math.max(data.length - 1, 1)) * plotWidth;
  const scaleY = (value) => pad.top + (1 - (value - min) / Math.max(max - min, 1)) * plotHeight;
  const grid = [0, 0.25, 0.5, 0.75, 1];

  return (
    <SvgChart height={height}>
      {grid.map((tick) => {
        const y = pad.top + tick * plotHeight;
        const label = max - tick * (max - min);
        return (
          <g key={tick}>
            <line x1={pad.left} x2={width - pad.right} y1={y} y2={y} className="grid-line" style={{ stroke: '#e2e8f0', strokeDasharray: '4 4' }} />
            <text x={pad.left - 10} y={y + 4} textAnchor="end" className="axis-label" style={{ fontSize: '12px', fill: '#64748b' }}>
              {compactNumber(label)}
            </text>
          </g>
        );
      })}
      {lines.map((line) => {
        const points = data
          .map((item, index) => {
            const value = Number(item[line.key]);
            return Number.isFinite(value) ? `${scaleX(index)},${scaleY(value)}` : null;
          })
          .filter(Boolean)
          .join(' ');
        return (
          <g key={line.key}>
            <polyline points={points} fill="none" stroke={line.color} strokeWidth={line.width || 3} strokeDasharray={line.dash || ''} strokeLinecap="round" strokeLinejoin="round" />
            {data.map((item, index) => {
              const value = Number(item[line.key]);
              if (!Number.isFinite(value)) return null;
              return (
                <circle key={index} cx={scaleX(index)} cy={scaleY(value)} r="6" fill="transparent" stroke="transparent" style={{ color: line.color }} className="chart-hover-dot">
                  <title>{`${String(item[xKey])}: ${formatNumber(value)}`}</title>
                </circle>
              );
            })}
          </g>
        );
      })}
      {[0, Math.floor(data.length / 2), data.length - 1].map((index) => (
        <text key={index} x={scaleX(index)} y={height - 10} textAnchor="middle" className="axis-label" style={{ fontSize: '12px', fill: '#64748b' }}>
          {String(data[index]?.[xKey] || '').slice(5)}
        </text>
      ))}
    </SvgChart>
  );
}

function BarChart({ data, xKey, yKey, color = '#4f46e5', height = 250, highlight }) {
  if (!data?.length) return <EmptyState />;
  const width = 720;
  const pad = { top: 20, right: 22, bottom: 42, left: 48 };
  const plotWidth = width - pad.left - pad.right;
  const plotHeight = height - pad.top - pad.bottom;
  const max = Math.max(...data.map((item) => Number(item[yKey]) || 0), 1);
  const gap = 8;
  const barWidth = Math.max((plotWidth - gap * (data.length - 1)) / data.length, 3);

  return (
    <SvgChart height={height}>
      {[0, 0.5, 1].map((tick) => {
        const y = pad.top + tick * plotHeight;
        return <line key={tick} x1={pad.left} x2={width - pad.right} y1={y} y2={y} className="grid-line" style={{ stroke: '#e2e8f0', strokeDasharray: '4 4' }} />;
      })}
      {data.map((item, index) => {
        const value = Number(item[yKey]) || 0;
        const heightValue = (value / max) * plotHeight;
        const x = pad.left + index * (barWidth + gap);
        const y = pad.top + plotHeight - heightValue;
        const fill = highlight?.(item) || color;
        return (
          <g key={`${item[xKey]}-${index}`}>
            <rect x={x} y={y} width={barWidth} height={heightValue} rx="5" fill={fill} className="chart-bar">
              <title>{`${item[xKey]}: ${formatNumber(value)}`}</title>
            </rect>
            <text x={x + barWidth / 2} y={height - 14} textAnchor="middle" className="axis-label" style={{ fontSize: '12px', fill: '#64748b' }}>
              {String(item[xKey]).slice(0, 3)}
            </text>
          </g>
        );
      })}
    </SvgChart>
  );
}

function GroupedYearBarChart({ data, xKey, yKey, height = 250 }) {
  if (!data?.length) return <EmptyState />;
  const years = yearsIn(data);
  if (years.length <= 1) return <BarChart data={data} xKey={xKey} yKey={yKey} color={yearColor(years[0])} height={height} />;

  const groups = [...new Set(data.map((item) => item[xKey]))];
  const byGroupYear = new Map(data.map((item) => [`${item[xKey]}-${item.year}`, item]));
  const width = 720;
  const pad = { top: 20, right: 22, bottom: 42, left: 48 };
  const plotWidth = width - pad.left - pad.right;
  const plotHeight = height - pad.top - pad.bottom;
  const max = Math.max(...data.map((item) => Number(item[yKey]) || 0), 1);
  const groupGap = 12;
  const groupWidth = (plotWidth - groupGap * (groups.length - 1)) / groups.length;
  const barWidth = Math.max((groupWidth - 5 * (years.length - 1)) / years.length, 3);

  return (
    <SvgChart height={height}>
      {[0, 0.5, 1].map((tick) => {
        const y = pad.top + tick * plotHeight;
        return <line key={tick} x1={pad.left} x2={width - pad.right} y1={y} y2={y} className="grid-line" style={{ stroke: '#e2e8f0', strokeDasharray: '4 4' }} />;
      })}
      {groups.map((group, groupIndex) => {
        const groupX = pad.left + groupIndex * (groupWidth + groupGap);
        return (
          <g key={group}>
            {years.map((year, yearIndex) => {
              const item = byGroupYear.get(`${group}-${year}`);
              const value = Number(item?.[yKey]) || 0;
              const heightValue = (value / max) * plotHeight;
              const x = groupX + yearIndex * (barWidth + 5);
              const y = pad.top + plotHeight - heightValue;
              return (
                <rect key={year} x={x} y={y} width={barWidth} height={heightValue} rx="4" fill={yearColor(year)} className="chart-bar">
                  <title>{`${group} ${year}: ${formatNumber(value)}`}</title>
                </rect>
              );
            })}
            <text x={groupX + groupWidth / 2} y={height - 14} textAnchor="middle" className="axis-label" style={{ fontSize: '12px', fill: '#64748b' }}>{monthShort(group)}</text>
          </g>
        );
      })}
    </SvgChart>
  );
}

function quantile(values, q) {
  if (!values.length) return 0;
  const sorted = [...values].sort((a, b) => a - b);
  const position = (sorted.length - 1) * q;
  const base = Math.floor(position);
  const rest = position - base;
  return sorted[base + 1] !== undefined ? sorted[base] + rest * (sorted[base + 1] - sorted[base]) : sorted[base];
}

function BoxPlotChart({ data, groupKey, valueKey, height = 280 }) {
  if (!data?.length) return <EmptyState />;
  const groups = [...new Set(data.map((item) => item[groupKey]).filter(Boolean))];
  const summaries = groups.map((group) => {
    const values = data
      .filter((item) => item[groupKey] === group)
      .map((item) => Number(item[valueKey]))
      .filter(Number.isFinite);
    return {
      group,
      min: Math.min(...values),
      q1: quantile(values, 0.25),
      median: quantile(values, 0.5),
      q3: quantile(values, 0.75),
      max: Math.max(...values),
    };
  });
  const width = 720;
  const pad = { top: 22, right: 30, bottom: 42, left: 56 };
  const plotWidth = width - pad.left - pad.right;
  const plotHeight = height - pad.top - pad.bottom;
  const min = Math.min(...summaries.map((item) => item.min), 0);
  const max = Math.max(...summaries.map((item) => item.max), 1);
  const scaleY = (value) => pad.top + (1 - (value - min) / Math.max(max - min, 1)) * plotHeight;
  const slot = plotWidth / summaries.length;
  const colors = ['#38bdf8', '#22c55e', '#f59e0b', '#f43f5e'];

  return (
    <SvgChart height={height}>
      {[0, 0.5, 1].map((tick) => {
        const y = pad.top + tick * plotHeight;
        return <line key={tick} x1={pad.left} x2={width - pad.right} y1={y} y2={y} className="grid-line" style={{ stroke: '#e2e8f0', strokeDasharray: '4 4' }} />;
      })}
      {summaries.map((item, index) => {
        const center = pad.left + index * slot + slot / 2;
        const boxWidth = Math.min(slot * 0.5, 58);
        return (
          <g key={item.group}>
            <line x1={center} x2={center} y1={scaleY(item.min)} y2={scaleY(item.max)} stroke="#64748b" strokeWidth="2" />
            <line x1={center - boxWidth / 3} x2={center + boxWidth / 3} y1={scaleY(item.min)} y2={scaleY(item.min)} stroke="#64748b" strokeWidth="2" />
            <line x1={center - boxWidth / 3} x2={center + boxWidth / 3} y1={scaleY(item.max)} y2={scaleY(item.max)} stroke="#64748b" strokeWidth="2" />
            <rect x={center - boxWidth / 2} y={scaleY(item.q3)} width={boxWidth} height={Math.max(scaleY(item.q1) - scaleY(item.q3), 2)} rx="5" fill={colors[index % colors.length]} opacity="0.82" className="chart-bar">
              <title>{`${item.group}\nMax: ${formatNumber(item.max)}\nQ3: ${formatNumber(item.q3)}\nMedian: ${formatNumber(item.median)}\nQ1: ${formatNumber(item.q1)}\nMin: ${formatNumber(item.min)}`}</title>
            </rect>
            <line x1={center - boxWidth / 2} x2={center + boxWidth / 2} y1={scaleY(item.median)} y2={scaleY(item.median)} stroke="#111827" strokeWidth="3" />
            <text x={center} y={height - 14} textAnchor="middle" className="axis-label" style={{ fontSize: '12px', fill: '#64748b' }}>{item.group.slice(0, 3)}</text>
          </g>
        );
      })}
      <text x={pad.left - 10} y={pad.top + 4} textAnchor="end" className="axis-label" style={{ fontSize: '12px', fill: '#64748b' }}>{compactNumber(max)}</text>
      <text x={pad.left - 10} y={height - pad.bottom} textAnchor="end" className="axis-label" style={{ fontSize: '12px', fill: '#64748b' }}>{compactNumber(min)}</text>
    </SvgChart>
  );
}

function HorizontalBarChart({ data, xKey, yKey, color = '#4f46e5', height = 250 }) {
  if (!data?.length) return <EmptyState />;
  const width = 720;
  const pad = { top: 18, right: 34, bottom: 18, left: 130 };
  const rowHeight = (height - pad.top - pad.bottom) / data.length;
  const max = Math.max(...data.map((item) => Number(item[yKey]) || 0), 1);

  return (
    <SvgChart height={height}>
      {data.map((item, index) => {
        const value = Number(item[yKey]) || 0;
        const y = pad.top + index * rowHeight + 6;
        const barWidth = ((width - pad.left - pad.right) * value) / max;
        return (
          <g key={`${item[xKey]}-${index}`}>
            <text x={pad.left - 12} y={y + rowHeight / 2 + 4} textAnchor="end" className="axis-label" style={{ fontSize: '12px', fill: '#64748b' }}>{item[xKey]}</text>
            <rect x={pad.left} y={y} width={width - pad.left - pad.right} height={Math.max(rowHeight - 12, 10)} rx="5" fill="#edf2f7" />
            <rect x={pad.left} y={y} width={barWidth} height={Math.max(rowHeight - 12, 10)} rx="5" fill={color} className="chart-bar">
              <title>{`${item[xKey]}: ${formatNumber(value)}`}</title>
            </rect>
            <text x={pad.left + barWidth + 8} y={y + rowHeight / 2 + 4} className="axis-label" style={{ fontSize: '12px', fill: '#64748b' }}>{compactNumber(value)}</text>
          </g>
        );
      })}
    </SvgChart>
  );
}

function ScatterPlot({ data, xKey, yKey, colorKey, height = 280, xUnit = '', xLabel = '' }) {
  if (!data?.length) return <EmptyState />;
  const width = 720;
  const pad = { top: 20, right: 32, bottom: 42, left: 58 };
  const plotWidth = width - pad.left - pad.right;
  const plotHeight = height - pad.top - pad.bottom;
  const xValues = data.map((item) => Number(item[xKey])).filter(Number.isFinite);
  const yValues = data.map((item) => Number(item[yKey])).filter(Number.isFinite);
  const minX = Math.min(...xValues);
  const maxX = Math.max(...xValues);
  const minY = Math.min(...yValues, 0);
  const maxY = Math.max(...yValues, 1);
  const colors = { Winter: '#38bdf8', Spring: '#22c55e', Summer: '#f59e0b', Autumn: '#f43f5e', Fall: '#f43f5e' };
  const scaleX = (value) => pad.left + ((value - minX) / Math.max(maxX - minX, 1)) * plotWidth;
  const scaleY = (value) => pad.top + (1 - (value - minY) / Math.max(maxY - minY, 1)) * plotHeight;

  return (
    <SvgChart height={height}>
      {[0, 0.5, 1].map((tick) => {
        const y = pad.top + tick * plotHeight;
        return <line key={tick} x1={pad.left} x2={width - pad.right} y1={y} y2={y} className="grid-line" style={{ stroke: '#e2e8f0', strokeDasharray: '4 4' }} />;
      })}
      {data.map((item) => (
        <circle
          key={item.date}
          cx={scaleX(Number(item[xKey]))}
          cy={scaleY(Number(item[yKey]))}
          r={Number(item.rainfall) > 0 ? 4.6 : 3.4}
          fill={colors[item[colorKey]] || '#4f46e5'}
          opacity="0.72"
          className="chart-dot"
        >
          <title>{`${item.date}\n${xLabel ? xLabel + ': ' : ''}${formatNumber(item[xKey])}${xUnit ? ' ' + xUnit : ''}\nTotal: ${formatNumber(item[yKey])}`}</title>
        </circle>
      ))}
      <text x={pad.left} y={height - 10} className="axis-label" style={{ fontSize: '12px', fill: '#64748b' }}>{formatNumber(minX, { maximumFractionDigits: 0 })}{xUnit ? ` ${xUnit}` : ''}</text>
      <text x={width / 2} y={height - 10} textAnchor="middle" className="axis-label" style={{ fontSize: '12px', fill: '#64748b', fontWeight: '500' }}>{xLabel}</text>
      <text x={width - pad.right} y={height - 10} textAnchor="end" className="axis-label" style={{ fontSize: '12px', fill: '#64748b' }}>{formatNumber(maxX, { maximumFractionDigits: 0 })}{xUnit ? ` ${xUnit}` : ''}</text>
      <text x={pad.left - 10} y={pad.top + 4} textAnchor="end" className="axis-label" style={{ fontSize: '12px', fill: '#64748b' }}>{compactNumber(maxY)}</text>
      <text x={pad.left - 10} y={height - pad.bottom} textAnchor="end" className="axis-label" style={{ fontSize: '12px', fill: '#64748b' }}>{compactNumber(minY)}</text>
    </SvgChart>
  );
}

function HeatmapChart({ data }) {
  if (!data?.length) return <EmptyState />;
  const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
  const width = 720;
  const height = 300;
  const pad = { top: 18, right: 16, bottom: 30, left: 76 };
  const cellWidth = (width - pad.left - pad.right) / 24;
  const cellHeight = (height - pad.top - pad.bottom) / days.length;
  const max = Math.max(...data.map((item) => Number(item.avg_bikes) || 0), 1);
  const byKey = new Map(data.map((item) => [`${item.day_name}-${item.hour}`, Number(item.avg_bikes) || 0]));

  function fill(value) {
    const ratio = value / max;
    if (ratio > 0.78) return '#4338ca';
    if (ratio > 0.58) return '#6366f1';
    if (ratio > 0.38) return '#14b8a6';
    if (ratio > 0.18) return '#93c5fd';
    return '#e8eef7';
  }

  return (
    <SvgChart height={height}>
      {days.map((day, dayIndex) => (
        <g key={day}>
          <text x={pad.left - 10} y={pad.top + dayIndex * cellHeight + cellHeight / 2 + 4} textAnchor="end" className="axis-label" style={{ fontSize: '12px', fill: '#64748b' }}>{day.slice(0, 3)}</text>
          {Array.from({ length: 24 }, (_, hour) => {
            const value = byKey.get(`${day}-${hour}`) || 0;
            return (
              <rect
                key={`${day}-${hour}`}
                x={pad.left + hour * cellWidth}
                y={pad.top + dayIndex * cellHeight}
                width={cellWidth - 2}
                height={cellHeight - 2}
                rx="3"
                fill={fill(value)}
                className="chart-bar"
              >
                <title>{`${day} @ ${hour}:00\n${formatNumber(value)} bikes`}</title>
              </rect>
            );
          })}
        </g>
      ))}
      {[0, 6, 12, 18, 23].map((hour) => (
        <text key={hour} x={pad.left + hour * cellWidth} y={height - 8} className="axis-label" style={{ fontSize: '12px', fill: '#64748b' }}>{hour}:00</text>
      ))}
    </SvgChart>
  );
}

function CorrelationChart({ data }) {
  if (!data?.length) return <EmptyState />;
  const width = 720;
  const height = 330;
  const pad = { top: 18, right: 48, bottom: 22, left: 150 };
  const rowHeight = (height - pad.top - pad.bottom) / data.length;
  const center = pad.left + (width - pad.left - pad.right) / 2;
  const halfWidth = (width - pad.left - pad.right) / 2;

  return (
    <SvgChart height={height}>
      <line x1={center} x2={center} y1={pad.top} y2={height - pad.bottom} className="zero-line" style={{ stroke: '#94a3b8', strokeWidth: 2 }} />
      {data.map((item, index) => {
        const value = Number(item.correlation) || 0;
        const barWidth = Math.abs(value) * halfWidth;
        const x = value >= 0 ? center : center - barWidth;
        const y = pad.top + index * rowHeight + 6;
        return (
          <g key={item.feature}>
            <text x={pad.left - 12} y={y + rowHeight / 2 + 4} textAnchor="end" className="axis-label" style={{ fontSize: '12px', fill: '#64748b' }}>{item.label}</text>
            <rect x={x} y={y} width={barWidth} height={Math.max(rowHeight - 12, 10)} rx="5" fill={value >= 0 ? '#14b8a6' : '#f43f5e'} className="chart-bar">
              <title>{`${item.label}\nCorrelation: ${formatNumber(value, { maximumFractionDigits: 3 })}`}</title>
            </rect>
            <text x={value >= 0 ? x + barWidth + 8 : x - 8} y={y + rowHeight / 2 + 4} textAnchor={value >= 0 ? 'start' : 'end'} className="axis-label" style={{ fontSize: '12px', fill: '#64748b' }}>
              {formatNumber(value, { maximumFractionDigits: 2 })}
            </text>
          </g>
        );
      })}
      <text x={pad.left} y={height - 4} className="axis-label" style={{ fontSize: '12px', fill: '#64748b' }}>Negative</text>
      <text x={width - pad.right} y={height - 4} textAnchor="end" className="axis-label" style={{ fontSize: '12px', fill: '#64748b' }}>Positive</text>
    </SvgChart>
  );
}

function SensitivityScatter({ data }) {
  if (!data?.length) return <EmptyState />;
  const width = 720;
  const height = 330;
  const pad = { top: 26, right: 36, bottom: 42, left: 60 };
  const plotWidth = width - pad.left - pad.right;
  const plotHeight = height - pad.top - pad.bottom;
  const maxAbsSensitivity = Math.max(...data.map((item) => Math.abs(Number(item.sensitivity) || 0)), 1);
  const scaleX = (value) => pad.left + ((value + 1) / 2) * plotWidth;
  const scaleY = (value) => pad.top + (1 - ((value + maxAbsSensitivity) / (2 * maxAbsSensitivity))) * plotHeight;

  return (
    <SvgChart height={height}>
      <line x1={scaleX(0)} x2={scaleX(0)} y1={pad.top} y2={height - pad.bottom} className="zero-line" style={{ stroke: '#94a3b8', strokeWidth: 1, strokeDasharray: '4 4' }} />
      <line x1={pad.left} x2={width - pad.right} y1={scaleY(0)} y2={scaleY(0)} className="zero-line" style={{ stroke: '#94a3b8', strokeWidth: 1, strokeDasharray: '4 4' }} />
      {[0.25, 0.5, 0.75].map((tick) => (
        <line key={tick} x1={pad.left} x2={width - pad.right} y1={pad.top + tick * plotHeight} y2={pad.top + tick * plotHeight} className="grid-line" style={{ stroke: '#e2e8f0', strokeDasharray: '4 4' }} />
      ))}
      {data.map((item) => {
        const x = scaleX(Number(item.correlation) || 0);
        const y = scaleY(Number(item.sensitivity) || 0);
        return (
          <g key={item.feature}>
            <circle cx={x} cy={y} r={7} fill={item.sensitivity >= 0 ? '#14b8a6' : '#f43f5e'} opacity="0.88" className="chart-dot">
              <title>{`${item.label}\nCorrelation: ${formatNumber(item.correlation, { maximumFractionDigits: 3 })}\nSensitivity: ${formatNumber(item.sensitivity, { maximumFractionDigits: 3 })}`}</title>
            </circle>
            <text x={x + 10} y={y + 4} className="axis-label" style={{ fontSize: '12px', fill: '#475569' }}>{item.label}</text>
          </g>
        );
      })}
      <text x={pad.left} y={height - 10} className="axis-label" style={{ fontSize: '12px', fill: '#64748b' }}>-1 corr</text>
      <text x={scaleX(0)} y={height - 10} textAnchor="middle" className="axis-label" style={{ fontSize: '12px', fill: '#64748b' }}>0</text>
      <text x={width - pad.right} y={height - 10} textAnchor="end" className="axis-label" style={{ fontSize: '12px', fill: '#64748b' }}>+1 corr</text>
      <text x={pad.left - 10} y={pad.top + 4} textAnchor="end" className="axis-label" style={{ fontSize: '12px', fill: '#64748b' }}>+{compactNumber(maxAbsSensitivity)}</text>
      <text x={pad.left - 10} y={height - pad.bottom} textAnchor="end" className="axis-label" style={{ fontSize: '12px', fill: '#64748b' }}>-{compactNumber(maxAbsSensitivity)}</text>
    </SvgChart>
  );
}

function FeatureSensitivityScatter({ data, feature }) {
  if (!data?.length || !feature) return <EmptyState />;
  return (
    <ScatterPlot
      data={data.map((item, index) => ({
        date: `${index}`,
        total: item.rented_bike_count,
        value: item[feature.feature],
        season: item.season,
        rainfall: item.rainfall,
      }))}
      xKey="value"
      yKey="total"
      colorKey="season"
      height={330}
      xLabel={feature.label}
      xUnit={FEATURE_UNITS[feature.feature] || ''}
    />
  );
}

function ClusterOverlayChart({ profiles }) {
  const flat = profiles.flatMap((profile) => profile.hourly_profile.map((item) => ({ ...item, [profile.cluster_name]: item.avg_bikes })));
  const hours = Array.from({ length: 24 }, (_, hour) => {
    const row = { hour };
    profiles.forEach((profile) => {
      row[profile.cluster_name] = profile.hourly_profile.find((item) => item.hour === hour)?.avg_bikes || 0;
    });
    return row;
  });
  if (!flat.length) return <EmptyState />;
  return (
    <LineChart
      data={hours}
      xKey="hour"
      height={280}
      lines={profiles.map((profile, index) => ({
        key: profile.cluster_name,
        color: ['#38bdf8', '#4f46e5', '#f43f5e'][index] || '#14b8a6',
        width: 3,
      }))}
    />
  );
}

function Correlations({ data, dateControls }) {
  const correlations = data.correlations || [];
  const strongest = correlations[0];
  const positives = correlations.filter((item) => item.correlation > 0).slice(0, 3);
  const negatives = correlations.filter((item) => item.correlation < 0).slice(0, 3);
  const [activeFeature, setActiveFeature] = useState(strongest?.feature || 'temperature');
  const selectedFeature = correlations.find((item) => item.feature === activeFeature) || strongest;

  useEffect(() => {
    if (strongest && !correlations.some((item) => item.feature === activeFeature)) {
      setActiveFeature(strongest.feature);
    }
  }, [strongest, correlations, activeFeature]);

  return (
    <div className="section-grid" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      <PageStory
        eyebrow="Correlation & Feature Relationships"
        title={strongest ? `${strongest.label} is the strongest linear signal for rental demand in the selected period.` : 'Feature relationships will appear when data is available.'}
        meta={
          <div className="diagnostic-grid" style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap', flex: 1 }}>
            <InsightCard label="Rows analyzed" value={formatNumber(data.rows || 0)} detail="hourly records in range" />
            <InsightCard label="Top correlation" value={formatNumber(strongest?.correlation, { maximumFractionDigits: 2 })} detail={strongest?.label || 'Unavailable'} />
          </div>
        }
      >
        Weather and time features explain different parts of rental demand. Correlation shows how strongly a feature moves with rentals, while the sensitivity view shows the observed rental distribution across feature values.
      </PageStory>
      {dateControls}
      <div className="chart-grid two" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(450px, 1fr))', gap: '1.5rem' }}>
        <ChartFrame
          title="Pearson correlation with rented bike count"
          action={<Legend items={[{ label: 'Positive', color: '#14b8a6' }, { label: 'Negative', color: '#f43f5e' }]} />}
        >
          <CorrelationChart data={correlations} />
        </ChartFrame>
        <ChartFrame
          title="Sensitivity by feature"
          action={<Legend items={[{ label: 'Positive bikes/unit', color: '#14b8a6' }, { label: 'Negative bikes/unit', color: '#f43f5e' }]} />}
        >
          <SensitivityScatter data={[...positives, ...negatives]} />
        </ChartFrame>
      </div>
      <div className="chart-grid" style={{ display: 'grid', gap: '1.5rem' }}>
        <ChartFrame
          title={`${selectedFeature?.label || 'Feature'} sensitivity`}
          action={<Legend items={[{ label: 'Winter', color: '#38bdf8' }, { label: 'Spring', color: '#22c55e' }, { label: 'Summer', color: '#f59e0b' }, { label: 'Autumn', color: '#f43f5e' }]} />}
        >
          <div className="feature-pills" style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem', marginBottom: '1.5rem' }}>
            {correlations.slice(0, 6).map((item) => (
              <button key={item.feature} className={item.feature === activeFeature ? 'selected' : ''} onClick={() => setActiveFeature(item.feature)} style={{ padding: '0.5rem 1rem', borderRadius: '9999px', fontSize: '0.875rem', fontWeight: '600', cursor: 'pointer', border: item.feature === activeFeature ? 'none' : '1px solid #cbd5e1', background: item.feature === activeFeature ? '#3b82f6' : '#ffffff', color: item.feature === activeFeature ? '#ffffff' : '#475569', transition: 'all 0.2s' }}>
                {item.label}
              </button>
            ))}
          </div>
          <FeatureSensitivityScatter data={data.samples || []} feature={selectedFeature} />
        </ChartFrame>
      </div>
    </div>
  );
}

function MultiForecastChart({ historical, prediction24h, prediction3d, actualFuture = [] }) {
  const byTime = new Map();
  const addValue = (items, key) => {
    items.forEach((item) => {
      const current = byTime.get(item.datetime) || { datetime: item.datetime };
      current[key] = item.bikes;
      byTime.set(item.datetime, current);
    });
  };
  addValue(historical, 'historical');
  addValue(actualFuture, 'actualFuture');
  addValue(prediction3d, 'prediction3d');
  addValue(prediction24h, 'prediction24h');
  const combined = [...byTime.values()].sort((a, b) => String(a.datetime).localeCompare(String(b.datetime)));
  return (
    <LineChart
      data={combined}
      xKey="datetime"
      height={320}
      lines={[
        { key: 'historical', color: '#14b8a6', width: 3 },
        { key: 'actualFuture', color: '#0f766e', width: 3 },
        { key: 'prediction3d', color: '#818cf8', width: 3, dash: '7 7' },
        { key: 'prediction24h', color: '#f43f5e', width: 3, dash: '2 6' },
      ]}
    />
  );
}

function Sidebar({ active, setActive }) {
  const icons = {
    overview: <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2" /><line x1="3" y1="9" x2="21" y2="9" /><line x1="9" y1="21" x2="9" y2="9" /></svg>,
    seasonality: <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="5" /><line x1="12" y1="1" x2="12" y2="3" /><line x1="12" y1="21" x2="12" y2="23" /><line x1="4.22" y1="4.22" x2="5.64" y2="5.64" /><line x1="18.36" y1="18.36" x2="19.78" y2="19.78" /><line x1="1" y1="12" x2="3" y2="12" /><line x1="21" y1="12" x2="23" y2="12" /><line x1="4.22" y1="19.78" x2="5.64" y2="18.36" /><line x1="18.36" y1="5.64" x2="19.78" y2="4.22" /></svg>,
    periodicity: <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10" /><polyline points="12 6 12 12 16 14" /></svg>,
    correlations: <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="18" cy="5" r="3" /><circle cx="6" cy="12" r="3" /><circle cx="18" cy="19" r="3" /><line x1="8.59" y1="13.51" x2="15.42" y2="17.49" /><line x1="15.41" y1="6.51" x2="8.59" y2="10.49" /></svg>,
    clusters: <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" /><circle cx="9" cy="7" r="4" /><path d="M23 21v-2a4 4 0 0 0-3-3.87" /><path d="M16 3.13a4 4 0 0 1 0 7.75" /></svg>,
    forecasting: <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12" /></svg>,
  };

  return (
    <aside className="sidebar" style={{ width: '260px', borderRight: '1px solid #e2e8f0', background: '#ffffff', display: 'flex', flexDirection: 'column', height: '100vh', position: 'sticky', top: 0 }}>
      <div className="brand" style={{ padding: '2rem 1.5rem', display: 'flex', alignItems: 'center', gap: '1rem', borderBottom: '1px solid #f1f5f9' }}>
        <div className="brand-mark" style={{ background: '#0f172a', color: '#fff', width: '40px', height: '40px', borderRadius: '10px', display: 'flex', alignItems: 'center', justifyContent: 'center', boxShadow: '0 2px 4px rgba(15, 23, 42, 0.3)' }}>
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="5.5" cy="17.5" r="3.5"/><circle cx="18.5" cy="17.5" r="3.5"/><path d="M15 6a1 1 0 1 0 0-2 1 1 0 0 0 0 2zm-3 11.5V14l-3-3 4-3 2 3h2"/></svg>
        </div>
        <div style={{ display: 'flex', flexDirection: 'column' }}>
          <strong style={{ fontSize: '1.125rem', color: '#06122e', lineHeight: '1.2' }}>Seoul Bike</strong>
          <span style={{ fontSize: '0.875rem', color: '#163b6c', fontWeight: '500' }}>Analytics</span>
        </div>
      </div>
      <nav style={{ padding: '1.5rem 1rem', display: 'flex', flexDirection: 'column', gap: '0.5rem', flex: 1 }}>
        {navItems.map(([label, id]) => (
          <button key={id} className={`nav-item ${active === id ? 'active' : ''}`} onClick={() => setActive(id)} style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', padding: '0.75rem 1rem', borderRadius: '8px', border: 'none', outline: 'none', background: active === id ? '#f1f5f9' : 'transparent', color: active === id ? '#0f172a' : '#475569', fontWeight: active === id ? '600' : '500', cursor: 'pointer', textAlign: 'left', transition: 'all 0.2s ease', width: '100%' }}>
            <span style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', opacity: active === id ? 1 : 0.5 }}>{icons[id]}</span>
            <span>{label}</span>
          </button>
        ))}
      </nav>
      <div className="sidebar-footer" style={{ padding: '1.5rem', borderTop: '1px solid #f1f5f9', display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
        <span style={{ fontSize: '0.75rem', color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.05em', fontWeight: '600' }}>Dataset</span>
        <strong style={{ fontSize: '0.875rem', color: '#0f172a' }}>2017-2018 Historical</strong>
      </div>
    </aside>
  );
}

function Overview({ overview, trends, dateControls }) {
  const summary = overview.summary || {};
  const daily = trends.daily || [];
  const monthly = trends.monthly || [];
  const recent = daily.slice(-120);
  const peakMonth = maxItem(monthly, 'total');
  const quietMonth = monthly.reduce((best, item) => (Number(item.total) < Number(best?.total || Infinity) ? item : best), null);
  const peakLift = (peakMonth?.total || 0) / Math.max(quietMonth?.total || 1, 1);
  const distribution = [
    { band: '< 10k', days: daily.filter((item) => item.total < 10000).length },
    { band: '10-20k', days: daily.filter((item) => item.total >= 10000 && item.total < 20000).length },
    { band: '20-30k', days: daily.filter((item) => item.total >= 20000 && item.total < 30000).length },
    { band: '30k+', days: daily.filter((item) => item.total >= 30000).length },
  ];
  const weekly = (trends.weekly || []).slice(-18);
  return (
    <div className="section-grid" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      <PageStory
        eyebrow="Executive summary · Demand story"
        title="Bike demand rises into early summer, then settles into a commuter-led autumn rhythm."
        meta={
          <div className="diagnostic-grid" style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap', flex: 1 }}>
            <InsightCard label="Selected total" value={formatNumber(summary.total_rentals)} detail={`${summary.total_days || 0} days analyzed`} />
            <InsightCard
              label="Peak month lift"
              value={`${formatNumber(peakLift, { maximumFractionDigits: 1 })}x`}
              detail={`${peakMonth?.month_name || 'Peak'} vs ${quietMonth?.month_name || 'quiet'} demand`}
            />
            <InsightCard label="Recent avg" value={formatNumber(average(recent, 'total'), { maximumFractionDigits: 0 })} detail="last 120 days" />
          </div>
        }
      >
        Across the selected period, demand is seasonal and commute-shaped: usage climbs with warmer conditions, peaks in early summer, then compresses into steadier weekday patterns. The charts below summarize trend, volume distribution, and monthly shifts.
      </PageStory>
      {dateControls}
      <div className="metric-grid" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1.5rem', marginBottom: '0.5rem' }}>
        <MetricCard label="Total rentals" value={formatNumber(summary.total_rentals)} detail={`${summary.total_days || 0} operating days`} tone="teal" />
        <MetricCard label="Daily average" value={formatNumber(summary.daily_average, { maximumFractionDigits: 0 })} detail="bikes per day" />
        <MetricCard label="Peak day" value={formatNumber(overview.peak_day?.total_bike_count)} detail={overview.peak_day?.date || 'Unavailable'} tone="rose" />
        <MetricCard label="Peak month" value={overview.peak_month ? `${overview.peak_month.month_name} ${overview.peak_month.year}` : 'Unavailable'} detail={formatNumber(overview.peak_month?.total_bike_count)} tone="violet" />
      </div>
      <div className="chart-grid two" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(450px, 1fr))', gap: '1.5rem' }}>
        <ChartFrame title="Daily rentals and 7-day trend">
          <LineChart
            data={recent}
            xKey="date"
            lines={[
              { key: 'total', color: '#c7d2fe', width: 2 },
              { key: 'moving_average_7d', color: '#4f46e5', width: 4 },
            ]}
          />
        </ChartFrame>
        <ChartFrame
          title="Monthly demand"
          action={yearsIn(monthly).length > 1 ? <Legend items={yearsIn(monthly).map((year) => ({ label: String(year), color: yearColor(year) }))} /> : null}
        >
          <GroupedYearBarChart data={monthly} xKey="month_name" yKey="total" />
        </ChartFrame>
      </div>
      <div className="chart-grid two" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(450px, 1fr))', gap: '1.5rem' }}>
        <ChartFrame title="Weekly volume in the closing period">
          <LineChart data={weekly} xKey="end_date" height={230} lines={[{ key: 'total', color: '#0f766e', width: 4 }]} />
        </ChartFrame>
        <ChartFrame title="Daily demand distribution">
          <HorizontalBarChart data={distribution} xKey="band" yKey="days" color="#8b5cf6" height={230} />
        </ChartFrame>
      </div>
    </div>
  );
}

function Seasonality({ data, dateControls }) {
  const monthly = data.monthly || [];
  const warmest = maxItem(data.daily_weather || [], 'avg_temperature');
  const wettest = maxItem(data.daily_weather || [], 'rainfall');
  return (
    <div className="section-grid" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      <PageStory
        eyebrow="Seasonality"
        title="Temperature and season shape the demand envelope."
        meta={<InsightCard label="Monthly rows" value={formatNumber(monthly.length)} detail="months in selected range" />}
      >
        Box plots show how daily rentals vary inside each season, while weather scatter plots reveal how demand changes with warmer conditions.
      </PageStory>
      {dateControls}
      <div className="chart-grid two" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(450px, 1fr))', gap: '1.5rem' }}>
        <ChartFrame title="Average rentals by month">
          <GroupedYearBarChart data={monthly} xKey="month_name" yKey="average" />
        </ChartFrame>
        <ChartFrame title="Season summary">
          <BoxPlotChart data={data.daily_weather || []} groupKey="season" valueKey="total" />
        </ChartFrame>
      </div>
      <ChartFrame title="Weather and demand by source season">
        <div className="weather-grid" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '1.5rem' }}>
          {(data.weather || []).map((item) => (
            <div className="weather-card" key={item.season} style={{ padding: '1.5rem', background: '#f8fafc', borderRadius: '12px', border: '1px solid #e2e8f0', display: 'flex', flexDirection: 'column', alignItems: 'center', textAlign: 'center', gap: '0.5rem' }}>
              <span style={{ fontSize: '0.875rem', fontWeight: '700', color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.05em' }}>{item.season}</span>
              <strong style={{ fontSize: '1.75rem', color: '#0f172a', lineHeight: '1.2' }}>{formatNumber(item.avg_hourly_rentals, { maximumFractionDigits: 0 })}</strong>
              <small style={{ fontSize: '0.875rem', color: '#475569' }}>{formatNumber(item.avg_temperature, { maximumFractionDigits: 1 })} °C avg</small>
            </div>
          ))}
        </div>
      </ChartFrame>
      <div className="chart-grid two wide-left" style={{ display: 'grid', gridTemplateColumns: 'minmax(400px, 2fr) minmax(300px, 1fr)', gap: '1.5rem' }}>
        <ChartFrame
          title="Temperature sensitivity"
          action={<Legend items={[{ label: 'Winter', color: '#38bdf8' }, { label: 'Spring', color: '#22c55e' }, { label: 'Summer', color: '#f59e0b' }, { label: 'Autumn', color: '#f43f5e' }]} />}
        >
          <ScatterPlot data={data.daily_weather || []} xKey="avg_temperature" yKey="total" colorKey="season" xLabel="Average temperature" xUnit="deg C" />
        </ChartFrame>
        <ChartFrame title="Demand by temperature band">
          <HorizontalBarChart data={data.temperature_bins || []} xKey="bin" yKey="avg_daily_total" color="#0ea5e9" height={280} />
        </ChartFrame>
      </div>
      <div className="insight-grid" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1.5rem' }}>
        <InsightCard label="Warmest day" value={warmest?.date || 'Unavailable'} detail={`${formatNumber(warmest?.avg_temperature, { maximumFractionDigits: 1 })} deg C avg`} />
        <InsightCard label="Wettest day" value={wettest?.date || 'Unavailable'} detail={`${formatNumber(wettest?.rainfall, { maximumFractionDigits: 1 })} mm rainfall`} />
        <InsightCard label="Summer average" value={formatNumber((data.seasonal || []).find((item) => item.season === 'Summer')?.average, { maximumFractionDigits: 0 })} detail="average hourly rentals" />
      </div>
    </div>
  );
}

function Periodicity({ data, dateControls }) {
  const peakHours = new Set([7, 8, 9, 17, 18, 19]);
  const peakHour = maxItem(data.hourly || [], 'avg_bikes');
  const bestDay = maxItem(data.weekday || [], 'avg_total');
  return (
    <div className="section-grid" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      <PageStory
        eyebrow="Periodicity"
        title="The strongest pattern is daily rhythm: commute peaks dominate repeatable demand."
        meta={<InsightCard label="Peak hour" value={`${String(peakHour?.hour ?? 18).padStart(2, '0')}:00`} detail={`${formatNumber(peakHour?.avg_bikes, { maximumFractionDigits: 0 })} avg bikes`} />}
      >
        Hourly bars and the weekday-hour heatmap show where demand concentrates during the week and throughout each day.
      </PageStory>
      {dateControls}
      <div className="chart-grid two" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(450px, 1fr))', gap: '1.5rem' }}>
        <ChartFrame title="Hourly rental pattern">
          <BarChart data={data.hourly || []} xKey="hour" yKey="avg_bikes" highlight={(item) => (peakHours.has(Number(item.hour)) ? '#f43f5e' : '#22c55e')} />
        </ChartFrame>
        <ChartFrame title="Weekday pattern">
          <BarChart data={data.weekday || []} xKey="day_name" yKey="avg_total" color="#6366f1" />
        </ChartFrame>
      </div>
      <div className="chart-grid two wide-left" style={{ display: 'grid', gridTemplateColumns: 'minmax(400px, 2fr) minmax(300px, 1fr)', gap: '1.5rem' }}>
        <ChartFrame title="Weekday-hour demand heatmap">
          <HeatmapChart data={data.heatmap || []} />
        </ChartFrame>
        <ChartFrame title="Daypart intensity">
          <HorizontalBarChart data={data.dayparts || []} xKey="daypart" yKey="avg_bikes" color="#14b8a6" height={300} />
        </ChartFrame>
      </div>
      <div className="insight-strip" style={{ background: '#ffffff', padding: '1.5rem 2rem', borderRadius: '12px', border: '1px solid #e2e8f0', borderLeft: '4px solid #8b5cf6', display: 'flex', gap: '1.5rem', alignItems: 'center', boxShadow: '0 2px 4px rgba(0,0,0,0.02)' }}>
        <strong style={{ fontSize: '1.125rem', color: '#0f172a', whiteSpace: 'nowrap' }}>Demand Rhythm</strong>
        <span style={{ color: '#475569', fontSize: '1.05rem', lineHeight: '1.5' }}>{String(peakHour?.hour ?? 18).padStart(2, '0')}:00 is the strongest recurring hour, and {bestDay?.day_name || 'weekdays'} carries the highest average daily volume.</span>
      </div>
    </div>
  );
}

function Clusters({ data, dateControls }) {
  const profiles = data.profiles || [];
  const selected = profiles[0];
  const [activeCluster, setActiveCluster] = useState(0);
  const active = profiles.find((profile) => profile.cluster_id === activeCluster) || selected;
  const seasonMix = (data.season_mix || []).filter((item) => item.cluster_id === activeCluster);
  const weekdayMix = (data.weekday_mix || []).filter((item) => item.cluster_id === activeCluster);

  useEffect(() => {
    if (profiles.length && !profiles.some((profile) => profile.cluster_id === activeCluster)) {
      setActiveCluster(profiles[0].cluster_id);
    }
  }, [profiles, activeCluster]);

  if (!profiles.length) return <EmptyState message="Run backend/generate_analysis.py to populate clustering tables." />;

  return (
    <div className="section-grid" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      <PageStory
        eyebrow="Customer clustering"
        title="Time-series clusters separate low-use, commuter, and leisure-shaped days."
        meta={<InsightCard label="Clusters" value={formatNumber(profiles.length)} detail="DTW TimeSeriesKMeans groups" />}
      >
        Each cluster is built from the 24-hour rental profile, so the grouping emphasizes demand shape rather than only total volume.
      </PageStory>
      {dateControls}
      <div className="cluster-cards" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1.5rem', marginBottom: '0.5rem' }}>
        {profiles.map((profile) => (
          <button className={`cluster-card ${activeCluster === profile.cluster_id ? 'selected' : ''}`} key={profile.cluster_id} onClick={() => setActiveCluster(profile.cluster_id)} style={{ padding: '1.5rem', borderRadius: '16px', border: activeCluster === profile.cluster_id ? '2px solid #3b82f6' : '1px solid #e2e8f0', background: activeCluster === profile.cluster_id ? '#eff6ff' : '#ffffff', display: 'flex', flexDirection: 'column', gap: '0.5rem', textAlign: 'left', cursor: 'pointer', transition: 'all 0.2s', boxShadow: activeCluster === profile.cluster_id ? '0 4px 12px -2px rgba(59, 130, 246, 0.15)' : '0 2px 4px rgba(0,0,0,0.02)' }}>
            <span style={{ fontSize: '1.25rem', fontWeight: '700', color: activeCluster === profile.cluster_id ? '#1e40af' : '#0f172a' }}>{profile.cluster_name}</span>
            <strong style={{ fontSize: '1rem', color: '#475569' }}>{profile.day_count} days</strong>
            <small style={{ fontSize: '0.875rem', color: '#64748b', lineHeight: '1.5', marginTop: '0.25rem' }}>{profile.description}</small>
          </button>
        ))}
      </div>
      <div className="chart-grid two" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(450px, 1fr))', gap: '1.5rem' }}>
        <ChartFrame title={active?.cluster_name || 'Cluster profile'}>
          <LineChart data={active?.hourly_profile || []} xKey="hour" lines={[{ key: 'avg_bikes', color: '#4f46e5', width: 4 }]} />
        </ChartFrame>
        <ChartFrame title="Cluster details">
          <div className="detail-list" style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', paddingBottom: '0.75rem', borderBottom: '1px solid #f1f5f9' }}><span style={{ color: '#64748b', fontWeight: '500' }}>Average daily total</span><strong style={{ color: '#0f172a', fontSize: '1.125rem' }}>{formatNumber(active?.avg_daily_total, { maximumFractionDigits: 0 })}</strong></div>
            <div style={{ display: 'flex', justifyContent: 'space-between', paddingBottom: '0.75rem', borderBottom: '1px solid #f1f5f9' }}><span style={{ color: '#64748b', fontWeight: '500' }}>Weekend share</span><strong style={{ color: '#0f172a', fontSize: '1.125rem' }}>{toPercent(active?.weekend_share)}</strong></div>
            <div style={{ display: 'flex', justifyContent: 'space-between', paddingBottom: '0.75rem', borderBottom: '1px solid #f1f5f9' }}><span style={{ color: '#64748b', fontWeight: '500' }}>Holiday share</span><strong style={{ color: '#0f172a', fontSize: '1.125rem' }}>{toPercent(active?.holiday_share)}</strong></div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}><span style={{ color: '#64748b', fontWeight: '500' }}>Peak hour</span><strong style={{ color: '#0f172a', fontSize: '1.125rem' }}>{String(active?.peak_hour).padStart(2, '0')}:00</strong></div>
          </div>
        </ChartFrame>
      </div>
      <div className="chart-grid two wide-left" style={{ display: 'grid', gridTemplateColumns: 'minmax(400px, 2fr) minmax(300px, 1fr)', gap: '1.5rem' }}>
        <ChartFrame
          title="Cluster profiles compared"
          action={<Legend items={profiles.map((profile, index) => ({ label: profile.cluster_name, color: ['#38bdf8', '#4f46e5', '#f43f5e'][index] || '#14b8a6' }))} />}
        >
          <ClusterOverlayChart profiles={profiles} />
        </ChartFrame>
        <ChartFrame title="Selected cluster composition">
          <div className="mini-chart-stack" style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
            <div style={{ flex: 1 }}><h4 style={{ margin: '0 0 1rem 0', fontSize: '0.875rem', color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Season</h4><HorizontalBarChart data={seasonMix} xKey="season" yKey="days" color="#f59e0b" height={150} /></div>
            <div style={{ flex: 1 }}><h4 style={{ margin: '0 0 1rem 0', fontSize: '0.875rem', color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Weekday</h4><HorizontalBarChart data={weekdayMix} xKey="weekday" yKey="days" color="#14b8a6" height={190} /></div>
          </div>
        </ChartFrame>
      </div>
    </div>
  );
}

function Forecasting({ options, dateControls }) {
  const defaultDate = options.default?.date || options.dates?.[0] || '2018-11-22';
  const defaultHour = options.default?.hour ?? 8;
  const [date, setDate] = useState(defaultDate);
  const [hour, setHour] = useState(defaultHour);

  useEffect(() => {
    setDate(defaultDate);
    setHour(defaultHour);
  }, [defaultDate, defaultHour]);

  const { data } = useApi(`/api/forecast?date=${date}&hour=${hour}`, {
    historical: [],
    prediction_24h: [],
    prediction_3d: [],
    metrics: {},
  });
  const metrics = data.metrics || {};
  const prediction24h = data.prediction_24h || [];
  const prediction3d = data.prediction_3d || [];
  const historical = data.historical || [];
  const actualFuture = data.actual_future || [];
  const comparison = (data.comparison || []).slice(0, 72);
  const actualByTime = new Map(actualFuture.map((item) => [item.datetime, item.bikes]));
  const errorsByTime = new Map(comparison.map((item) => [item.datetime, item]));
  const peak = maxItem(prediction3d, 'bikes');
  const next24Total = metrics.predicted_24h_total || 0;
  const last24Total = metrics.historical_24h_total || 0;
  const change24h = last24Total ? ((next24Total - last24Total) / last24Total) * 100 : 0;
  const peakHour = peak ? String(peak.datetime).slice(11, 16) : '--:--';
  const peakDate = peak ? String(peak.datetime).slice(0, 10) : 'Unavailable';
  const forecastStart = prediction3d[0]?.datetime || prediction24h[0]?.datetime || 'Unavailable';
  const forecastEnd = prediction3d[prediction3d.length - 1]?.datetime || prediction24h[prediction24h.length - 1]?.datetime || 'Unavailable';
  const forecastValues = prediction3d.map((item) => Number(item.bikes) || 0);
  const highThreshold = quantile(forecastValues, 0.75);
  const mediumThreshold = quantile(forecastValues, 0.5);
  const forecastDayparts = ['Overnight', 'Morning', 'Midday', 'Evening', 'Late night'].map((daypart) => {
    const hours = prediction3d.filter((item) => {
      const hourValue = Number(String(item.datetime).slice(11, 13));
      if (daypart === 'Overnight') return hourValue <= 5;
      if (daypart === 'Morning') return hourValue >= 6 && hourValue <= 10;
      if (daypart === 'Midday') return hourValue >= 11 && hourValue <= 15;
      if (daypart === 'Evening') return hourValue >= 16 && hourValue <= 20;
      return hourValue >= 21;
    });
    const total = hours.reduce((sum, item) => sum + (Number(item.bikes) || 0), 0);
    return { daypart, predicted: total, average: hours.length ? total / hours.length : 0 };
  });
  const cumulativeForecast = prediction3d.reduce((items, item) => {
    const previous = items[items.length - 1]?.cumulative || 0;
    items.push({ datetime: item.datetime, cumulative: previous + (Number(item.bikes) || 0) });
    return items;
  }, []);
  const forecastTable = prediction3d.slice(0, 24).map((item) => {
    const bikes = Number(item.bikes) || 0;
    let action = 'Light demand';
    if (bikes >= highThreshold) action = 'High availability';
    else if (bikes >= mediumThreshold) action = 'Normal watch';
    return {
      ...item,
      actual: actualByTime.get(item.datetime),
      error: errorsByTime.get(item.datetime)?.error,
      action,
    };
  });
  const modelStatus = metrics.overlap_hours
    ? `${metrics.overlap_hours} overlap hours are available for validation.`
    : 'No future actuals are available for this origin yet.';

  return (
    <div className="section-grid">
      <PageStory
        eyebrow="Forecast planning"
        title="Use the forecast as an operating plan, not just a predicted line."
        meta={<InsightCard label="Forecast window" value={String(forecastEnd).slice(0, 10)} detail={`starts ${String(forecastStart).slice(0, 16)}`} />}
      >
        The view compares the forecast origin with recent observed demand, highlights when demand is expected to peak, and checks the forecast against any actual overlap.
      </PageStory>
      <Card className="forecast-planner">
        <div>
          <span>Forecast origin</span>
          <strong>{date} {String(hour).padStart(2, '0')}:00</strong>
          <small>Predictions are generated forward from this timestamp.</small>
        </div>
        <div className="forecast-controls">
          <label>
            Start date
            <select value={date} onChange={(event) => setDate(event.target.value)}>
              {(options.dates || []).map((item) => <option key={item}>{item}</option>)}
            </select>
          </label>
          <label>
            Start hour
            <select value={hour} onChange={(event) => setHour(Number(event.target.value))}>
              {(options.hours || Array.from({ length: 24 }, (_, index) => index)).map((item) => (
                <option key={item} value={item}>{String(item).padStart(2, '0')}:00</option>
              ))}
            </select>
          </label>
        </div>
      </Card>
      <div className="metric-grid">
        <MetricCard label="Next 24h" value={formatNumber(next24Total, { maximumFractionDigits: 0 })} detail={`${change24h >= 0 ? '+' : ''}${formatNumber(change24h, { maximumFractionDigits: 1 })}% vs previous 24h`} />
        <MetricCard label="Next 3d" value={formatNumber(metrics.predicted_3d_total, { maximumFractionDigits: 0 })} detail="total predicted rentals" tone="violet" />
        <MetricCard label="Peak hour" value={peakHour} detail={`${peakDate}, ${formatNumber(peak?.bikes, { maximumFractionDigits: 0 })} bikes`} tone="rose" />
        <MetricCard label="Validation MAE" value={formatNumber(metrics.mae_3d_overlap, { maximumFractionDigits: 0 })} detail={modelStatus} tone="teal" />
      </div>
      <div className="insight-strip">
        <strong>Planning readout</strong>
        <span>
          Demand is expected to {change24h >= 0 ? 'rise' : 'fall'} by {formatNumber(Math.abs(change24h), { maximumFractionDigits: 1 })}% against the prior 24 hours, with the largest hourly load around {peakHour} on {peakDate}.
        </span>
      </div>
      <div className="chart-grid two wide-left">
        <ChartFrame
          title="Observed demand and forecast horizon"
          action={<Legend items={[{ label: 'Observed history', color: '#14b8a6' }, { label: 'Actual overlap', color: '#0f766e' }, { label: '3d forecast', color: '#818cf8' }, { label: '24h forecast', color: '#f43f5e' }]} />}
        >
          <MultiForecastChart historical={historical} actualFuture={actualFuture} prediction24h={prediction24h} prediction3d={prediction3d} />
        </ChartFrame>
        <ChartFrame title="3-day demand by daypart">
          <HorizontalBarChart data={forecastDayparts} xKey="daypart" yKey="predicted" color="#6366f1" height={320} />
        </ChartFrame>
      </div>
      <div className="chart-grid two">
        <ChartFrame title="Cumulative 3-day forecast">
          <LineChart data={cumulativeForecast} xKey="datetime" height={260} lines={[{ key: 'cumulative', color: '#4f46e5', width: 4 }]} />
        </ChartFrame>
        <ChartFrame
          title="Forecast accuracy where actuals exist"
          action={<Legend items={[{ label: 'Observed', color: '#14b8a6' }, { label: 'Predicted', color: '#f43f5e' }]} />}
        >
          <LineChart
            data={comparison}
            xKey="datetime"
            height={260}
            lines={[
              { key: 'actual', color: '#14b8a6', width: 3 },
              { key: 'predicted', color: '#f43f5e', width: 3, dash: '5 5' },
            ]}
          />
        </ChartFrame>
      </div>
      <Card>
        <div className="card-header">
          <div>
            <h3>First 24 hours operating schedule</h3>
          </div>
        </div>
        <div className="table-wrap" style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
            <thead>
              <tr><th>Date and time</th><th>Forecast</th><th>Actual</th><th>Error</th><th>Operating cue</th></tr>
            </thead>
            <tbody>
              {forecastTable.map((row) => (
                <tr key={row.datetime}>
                  <td>{row.datetime}</td>
                  <td>{formatNumber(row.bikes, { maximumFractionDigits: 0 })}</td>
                  <td>{row.actual === undefined ? '-' : formatNumber(row.actual, { maximumFractionDigits: 0 })}</td>
                  <td>{row.error === undefined ? '-' : formatNumber(row.error, { maximumFractionDigits: 0 })}</td>
                  <td><span className={`forecast-cue ${row.action === 'High availability' ? 'high' : row.action === 'Normal watch' ? 'normal' : 'low'}`}>{row.action}</span></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
}

function ModelSummary({ data }) {
  return (
    <Card style={{ marginTop: '2.5rem' }}>
      <div className="card-header" style={{ marginBottom: '1.5rem', borderBottom: '1px solid #f1f5f9', paddingBottom: '1rem' }}><h3 style={{ margin: 0, fontSize: '1.25rem', color: '#0f172a' }}>Forecast model summary</h3></div>
      <div className="model-grid" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1.5rem' }}>
        {(data.metrics || []).map((metric) => (
          <div className="model-card" key={metric.model_name} style={{ padding: '1.5rem', background: '#f8fafc', borderRadius: '12px', border: '1px solid #e2e8f0', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            <span style={{ fontSize: '0.875rem', fontWeight: '700', color: '#64748b', textTransform: 'uppercase' }}>{metric.model_name}</span>
            <strong style={{ fontSize: '1.75rem', color: '#0f172a' }}>R² {formatNumber(metric.r_squared, { maximumFractionDigits: 3 })}</strong>
            <small style={{ fontSize: '0.875rem', color: '#475569' }}>RMSE {formatNumber(metric.rmse, { maximumFractionDigits: 1 })} &bull; RMSLE {formatNumber(metric.rmsle, { maximumFractionDigits: 2 })}</small>
          </div>
        ))}
      </div>
    </Card>
  );
}

export default function App() {
  const [active, setActive] = useState('overview');
  const [startDate, setStartDate] = useState('2017-12-01');
  const [endDate, setEndDate] = useState('2018-11-30');
  const selectedRange = `start_date=${startDate}&end_date=${endDate}`;
  const overview = useApi(`/api/overview?${selectedRange}`, {});
  const trends = useApi(`/api/trends?${selectedRange}`, {});
  const seasonality = useApi(`/api/seasonality?${selectedRange}`, {});
  const periodicity = useApi(`/api/periodicity?${selectedRange}`, {});
  const correlations = useApi(`/api/correlations?${selectedRange}`, {});
  const clusters = useApi(`/api/clusters?${selectedRange}`, {});
  const forecastOptions = useApi('/api/forecast/options', {});
  const modelSummary = useApi('/api/model-summary', {});
  const anyError = [overview, trends, seasonality, periodicity, correlations, clusters, forecastOptions, modelSummary].find((item) => item.error);
  const dateControls = <DateControls startDate={startDate} endDate={endDate} setStartDate={setStartDate} setEndDate={setEndDate} />;

  const page = useMemo(() => {
    if (active === 'seasonality') return <Seasonality data={seasonality.data} dateControls={dateControls} />;
    if (active === 'periodicity') return <Periodicity data={periodicity.data} dateControls={dateControls} />;
    if (active === 'correlations') return <Correlations data={correlations.data} dateControls={dateControls} />;
    if (active === 'clusters') return <Clusters data={clusters.data} dateControls={dateControls} />;
    if (active === 'forecasting') return <Forecasting options={forecastOptions.data} dateControls={dateControls} />;
    return <Overview overview={overview.data} trends={trends.data} dateControls={dateControls} />;
  }, [active, overview.data, trends.data, seasonality.data, periodicity.data, correlations.data, clusters.data, forecastOptions.data, startDate, endDate]);

  return (
    <div className="app-shell" style={{ display: 'flex', minHeight: '100vh', background: '#f8fafc', fontFamily: 'system-ui, -apple-system, sans-serif' }}>
      <style>{`
        .chart-bar { transition: opacity 0.2s ease; cursor: pointer; }
        .chart-bar:hover { opacity: 0.75 !important; }
        .chart-dot { transition: all 0.2s ease; cursor: crosshair; }
        .chart-dot:hover { opacity: 1 !important; stroke: #0f172a; stroke-width: 2px; }
        .chart-hover-dot { transition: all 0.2s ease; cursor: crosshair; }
        .chart-hover-dot:hover { fill: currentColor; stroke: #0f172a; stroke-width: 2px; opacity: 1 !important; }
        .nav-item:hover { background-color: #f8fafc !important; color: #0f172a !important; }
        .nav-item:hover span { opacity: 1 !important; }
        .nav-item.active:hover { background-color: #e2e8f0 !important; }
      `}</style>
      <Sidebar active={active} setActive={setActive} />
      <main style={{ flex: 1, padding: '2.5rem 3rem', maxWidth: '1600px', width: '100%', boxSizing: 'border-box' }}>
        {anyError && <div className="api-error" style={{ background: '#fef2f2', color: '#9f1239', padding: '1rem 1.5rem', borderRadius: '8px', marginBottom: '2rem', border: '1px solid #fecdd3', fontWeight: '500' }}>API connection issue: {anyError.error}</div>}
        {page}
        {active === 'forecasting' && <ModelSummary data={modelSummary.data} />}
      </main>
    </div>
  );
}
