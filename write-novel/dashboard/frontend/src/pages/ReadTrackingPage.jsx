import { useEffect, useMemo, useState } from 'react'
import { useDashboardContext } from '../App.jsx'
import { fetchChapterTrend } from '../api.js'
import Badge from '../components/Badge.jsx'
import ChartWrapper from '../components/ChartWrapper.jsx'
import Pager from '../components/Pager.jsx'
import { STRAND_COLORS } from '../lib/charts.js'
import { average, formatChapterLabel, formatNumber, formatShortNumber } from '../lib/format.js'

const WINDOW_SIZE = 50

const HOOK_TYPE_COLORS = {
    crisis: '#d7263d',
    suspense: '#7f5af0',
    desire: '#f5a524',
    emotion: '#ff5c8a',
    choice: '#26a8ff',
    unknown: '#8f7f5c',
}

const HOOK_TYPE_LABELS = {
    crisis: '危机',
    suspense: '悬念',
    desire: '欲望',
    emotion: '情绪',
    choice: '选择',
    unknown: '未知',
}

function buildHookDistributionOption(stats) {
    const entries = Object.entries(stats.typeCounts)
        .filter(([, v]) => v > 0)
        .map(([key, value]) => ({
            name: HOOK_TYPE_LABELS[key] || key,
            value,
            itemStyle: {
                color: HOOK_TYPE_COLORS[key] || '#8f7f5c',
                borderColor: '#2a220f',
                borderWidth: 2,
            },
        }))

    return {
        tooltip: { trigger: 'item', formatter: '{b}: {c} 次 ({d}%)' },
        legend: { bottom: 0 },
        series: [
            {
                type: 'pie',
                radius: ['42%', '68%'],
                avoidLabelOverlap: false,
                label: {
                    show: true,
                    formatter: '{b}\n{d}%',
                    color: '#5d5035',
                    fontSize: 12,
                    fontWeight: 600,
                },
                data: entries,
            },
        ],
    }
}

function buildCoolPointTrend(items) {
    return {
        tooltip: { trigger: 'axis' },
        grid: { left: 52, right: 24, top: 36, bottom: 46 },
        xAxis: {
            type: 'category',
            data: items.map(item => item.chapter),
            axisLabel: { interval: 9, formatter: value => `${value}` },
        },
        yAxis: {
            type: 'value',
            min: 0,
        },
        series: [
            {
                type: 'line',
                name: '爽点密度',
                data: items.map(item => item.cool_points ?? null),
                symbol: 'rect',
                symbolSize: 8,
                lineStyle: { width: 3, color: '#2ec27e' },
                itemStyle: {
                    color: '#2ec27e',
                    borderColor: '#2a220f',
                    borderWidth: 2,
                },
                connectNulls: false,
            },
        ],
    }
}

function StatCard({ label, value, sub, tone = 'plain' }) {
    return (
        <article className="card stat-card">
            <span className="stat-label">{label}</span>
            <span className={`stat-value ${tone === 'plain' ? 'plain' : ''}`.trim()}>{value}</span>
            <span className="stat-sub">{sub}</span>
        </article>
    )
}

export default function ReadTrackingPage() {
    const { projectInfo, refreshToken } = useDashboardContext()
    const [windowPayload, setWindowPayload] = useState({ items: [], total: 0, latest_chapter: 0 })
    const [windowIndex, setWindowIndex] = useState(0)
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        setWindowIndex(0)
    }, [refreshToken])

    useEffect(() => {
        let cancelled = false
        setLoading(true)

        fetchChapterTrend({ limit: WINDOW_SIZE, offset: windowIndex * WINDOW_SIZE })
            .then(payload => {
                if (!cancelled) setWindowPayload(payload)
            })
            .catch(() => {
                if (!cancelled) setWindowPayload({ items: [], total: 0, latest_chapter: 0 })
            })
            .finally(() => {
                if (!cancelled) setLoading(false)
            })

        return () => { cancelled = true }
    }, [refreshToken, windowIndex])

    const items = windowPayload.items || []
    const totalPages = Math.max(1, Math.ceil((windowPayload.total || 0) / WINDOW_SIZE))
    const displayPage = Math.max(1, totalPages - windowIndex)
    const currentStart = items[0]?.chapter || 0
    const currentEnd = items[items.length - 1]?.chapter || 0

    const hookStats = useMemo(() => {
        const typeCounts = { crisis: 0, suspense: 0, desire: 0, emotion: 0, choice: 0, unknown: 0 }
        let total = 0
        items.forEach(item => {
            const t = item.hook_type || 'unknown'
            typeCounts[t] = (typeCounts[t] || 0) + 1
            total++
        })
        const dominant = Object.entries(typeCounts)
            .filter(([, v]) => v > 0)
            .sort(([, a], [, b]) => b - a)[0]
        return {
            typeCounts,
            total,
            dominant: dominant ? HOOK_TYPE_LABELS[dominant[0]] : '无数据',
            dominantPct: total > 0 ? Math.round((dominant?.[1] || 0) / total * 100) : 0,
        }
    }, [items])

    const coolAvg = useMemo(() => average(items.map(item => item.cool_points)), [items])
    const hookDensity = useMemo(() => {
        const totalWords = items.reduce((sum, item) => sum + Number(item.word_count || 0), 0)
        return totalWords > 0 ? (hookStats.total / (totalWords / 1000)) : 0
    }, [items, hookStats])

    const progress = projectInfo?.progress || {}

    return (
        <section className="dashboard-page">
            <header className="page-header">
                <h2>追读力仪表盘</h2>
                <Badge tone="green">{formatChapterLabel(progress.current_chapter)}</Badge>
            </header>

            <div className="stat-grid">
                <StatCard label="钩子总数" value={String(hookStats.total)} sub="当前窗口" tone="plain" />
                <StatCard label="主导类型" value={hookStats.dominant} sub={`占比 ${hookStats.dominantPct}%`} tone="plain" />
                <StatCard label="钓子密度" value={formatShortNumber(hookDensity)} sub="每千字钩子数" tone="plain" />
                <StatCard label="爽点均分" value={coolAvg ? formatShortNumber(coolAvg) : '—'} sub="当前窗口" tone="plain" />
            </div>

            <div className="content-grid two-columns">
                <article className="card">
                    <div className="card-header">
                        <div>
                            <div className="section-label">HOOK DISTRIBUTION</div>
                            <div className="card-title">钩子类型分布</div>
                        </div>
                        <Badge tone="purple">危机·悬念·欲望·情绪·选择</Badge>
                    </div>
                    {hookStats.total > 0 ? (
                        <ChartWrapper option={buildHookDistributionOption(hookStats)} height={300} />
                    ) : (
                        <div className="empty-state">
                            <p>暂无钩子类型数据</p>
                        </div>
                    )}
                </article>

                <article className="card">
                    <div className="card-header">
                        <div>
                            <div className="section-label">TYPE LEGEND</div>
                            <div className="card-title">钩子类型说明</div>
                        </div>
                    </div>
                    <div style={{ padding: '12px 16px' }}>
                        {Object.entries(HOOK_TYPE_LABELS).map(([key, label]) => (
                            <div key={key} style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
                                <span style={{
                                    display: 'inline-block', width: 14, height: 14,
                                    background: HOOK_TYPE_COLORS[key], border: '2px solid #2a220f',
                                }} />
                                <span style={{ fontWeight: 600, fontSize: 13, color: '#2a220f', minWidth: 32 }}>{label}</span>
                                <span style={{ fontSize: 13, color: '#5d5035' }}>
                                    {key === 'crisis' && '紧急危机——读者担心角色安危'}
                                    {key === 'suspense' && '信息悬念——读者想知道答案'}
                                    {key === 'desire' && '欲望驱动——读者想看主角得到'}
                                    {key === 'emotion' && '情绪牵动——读者被情感感染'}
                                    {key === 'choice' && '两难选择——读者纠结角色会怎么选'}
                                    {key === 'unknown' && '未分类——建议补充钩子类型标注'}
                                </span>
                            </div>
                        ))}
                    </div>
                </article>
            </div>

            <article className="card">
                <div className="card-header">
                    <div>
                        <div className="section-label">COOL POINT TREND</div>
                        <div className="card-title">爽点密度趋势</div>
                    </div>
                    <Badge tone="green">
                        {currentStart && currentEnd ? `${formatChapterLabel(currentStart)} - ${formatChapterLabel(currentEnd)}` : '最近窗口'}
                    </Badge>
                </div>
                {items.length ? (
                    <>
                        <ChartWrapper option={buildCoolPointTrend(items)} loading={loading} />
                        <Pager
                            page={displayPage}
                            totalPages={totalPages}
                            currentStart={currentStart}
                            currentEnd={currentEnd}
                            totalItems={windowPayload.total || 0}
                            onPrevious={() => setWindowIndex(current => Math.min(totalPages - 1, current + 1))}
                            onNext={() => setWindowIndex(current => Math.max(0, current - 1))}
                            onLatest={() => setWindowIndex(0)}
                            stepLabel={String(WINDOW_SIZE)}
                        />
                    </>
                ) : (
                    <div className="empty-state">
                        <p>暂无爽点趋势数据</p>
                    </div>
                )}
            </article>
        </section>
    )
}
