import { useMemo } from 'react'
import { useDashboardContext } from '../App.jsx'
import Badge from '../components/Badge.jsx'
import ChartWrapper from '../components/ChartWrapper.jsx'
import { STRAND_COLORS } from '../lib/charts.js'

const CATEGORY_COLORS = {
    protagonist: '#26a8ff',
    ally: '#2ec27e',
    antagonist: '#d7263d',
    neutral: '#f5a524',
    faction: '#7f5af0',
    location: '#00b8d4',
}

function buildGraphOption(nodes, links, categories) {
    return {
        tooltip: {
            formatter: params => {
                if (params.dataType === 'node') {
                    return `${params.name}<br/>类型：${params.data.category}<br/>${params.data.desc || ''}`
                }
                return `${params.data.source} → ${params.data.target}<br/>${params.data.label || ''}`
            },
        },
        legend: {
            bottom: 0,
            data: categories.map(c => c.name),
        },
        series: [
            {
                type: 'graph',
                layout: 'force',
                roam: true,
                draggable: true,
                force: {
                    repulsion: 200,
                    edgeLength: [80, 200],
                    gravity: 0.1,
                },
                categories,
                data: nodes.map(n => ({
                    name: n.name,
                    category: n.category,
                    symbolSize: n.size || 20,
                    desc: n.desc || '',
                    itemStyle: {
                        color: CATEGORY_COLORS[n.category] || '#26a8ff',
                        borderColor: '#2a220f',
                        borderWidth: 2,
                    },
                    label: {
                        show: true,
                        fontSize: 12,
                        fontWeight: 600,
                        color: '#2a220f',
                    },
                })),
                links: links.map(l => ({
                    source: l.source,
                    target: l.target,
                    label: { show: true, formatter: l.label || '', fontSize: 10 },
                    lineStyle: {
                        color: '#8f7f5c',
                        width: l.width || 1.5,
                        curveness: 0.2,
                    },
                })),
            },
        ],
    }
}

function StatCard({ label, value, sub }) {
    return (
        <article className="card stat-card">
            <span className="stat-label">{label}</span>
            <span className="stat-value">{value}</span>
            <span className="stat-sub">{sub}</span>
        </article>
    )
}

export default function RelationGraphPage() {
    const { projectInfo } = useDashboardContext()

    const { nodes, links, categories } = useMemo(() => {
        const chars = projectInfo?.characters || []
        const relations = projectInfo?.relations || []

        const catSet = new Set(chars.map(c => c.category || 'neutral'))
        const categories = [...catSet].map(name => ({ name }))

        const nodes = chars.map(c => ({
            name: c.name || c.id || '?',
            category: c.category || 'neutral',
            size: (c.importance || 3) * 6 + 8,
            desc: c.title || c.desc || '',
        }))

        const links = relations.map(r => ({
            source: r.source,
            target: r.target,
            label: r.type || r.label || '',
            width: (r.strength || 1) * 1.5,
        }))

        return { nodes, links, categories }
    }, [projectInfo])

    return (
        <section className="dashboard-page">
            <header className="page-header">
                <h2>关系图谱</h2>
                <Badge tone="purple">{nodes.length} 节点 · {links.length} 关系</Badge>
            </header>

            <div className="stat-grid">
                <StatCard label="角色节点" value={String(nodes.filter(n => n.category !== 'faction').length)} sub="含势力/地点" />
                <StatCard label="关系连线" value={String(links.length)} sub="含标注类型" />
                <StatCard label="势力节点" value={String(nodes.filter(n => n.category === 'faction').length)} sub="组织/门派" />
                <StatCard label="节点类型" value={String(categories.length)} sub="按分类着色" />
            </div>

            <article className="card">
                <div className="card-header">
                    <div>
                        <div className="section-label">RELATIONSHIP GRAPH</div>
                        <div className="card-title">角色 / 势力关系网络</div>
                    </div>
                    <Badge tone="blue">拖拽可移动 · 滚轮缩放</Badge>
                </div>
                {nodes.length ? (
                    <ChartWrapper
                        height={520}
                        option={buildGraphOption(nodes, links, categories)}
                    />
                ) : (
                    <div className="empty-state">
                        <p>暂无角色关系数据</p>
                        <p>请在设定/角色/ 和 设定/关系.md 中完善角色和关系信息</p>
                    </div>
                )}
            </article>
        </section>
    )
}
