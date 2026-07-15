import { useEffect, useRef } from 'react'
import * as echarts from 'echarts'

export interface KpNode {
  kp_id: number
  kp_name: string
  mastery: number // 0-1
  is_current_recommend?: boolean
  dependencies?: number[] // 前置知识点IDs
  difficulty_level?: string
  description?: string
}

interface LearningPathGraphProps {
  nodes: KpNode[]
  currentKpId?: number
  onNodeClick?: (kpId: number) => void
}

export function LearningPathGraph({ nodes, currentKpId, onNodeClick }: LearningPathGraphProps) {
  const chartRef = useRef<HTMLDivElement>(null)
  const chartInstance = useRef<echarts.ECharts | null>(null)

  useEffect(() => {
    if (!chartRef.current) return
    chartInstance.current = echarts.init(chartRef.current)
    return () => { chartInstance.current?.dispose() }
  }, [])

  useEffect(() => {
    const chart = chartInstance.current
    if (!chart || nodes.length === 0) return

    const masteryColor = (m: number) =>
      m >= 0.75 ? '#22c55e' : m >= 0.5 ? '#f97316' : '#ef4444'

    // 构建 graph 数据
    const graphNodes = nodes.map((node, i) => ({
      id: String(node.kp_id),
      name: node.kp_name,
      value: [i % 3, Math.floor(i / 3)],
      mastery: node.mastery,
      difficulty: node.difficulty_level,
      description: node.description,
      isCurrent: node.kp_id === currentKpId,
      symbolSize: node.kp_id === currentKpId ? 65 : 50,
      itemStyle: {
        color: node.kp_id === currentKpId ? '#3b82f6' : masteryColor(node.mastery),
        borderColor: node.kp_id === currentKpId ? '#1d4ed8' : undefined,
        borderWidth: node.kp_id === currentKpId ? 4 : 2,
      },
    }))

    const graphLinks = nodes.flatMap((node) =>
      (node.dependencies ?? []).map((depId) => ({
        source: String(depId),
        target: String(node.kp_id),
      }))
    )

    const option: echarts.EChartsOption = {
      tooltip: {
        trigger: 'item',
        triggerOn: 'mousemove',
        backgroundColor: 'rgba(255,255,255,0.98)',
        borderColor: '#e2e8f0',
        borderWidth: 1,
        padding: [12, 16],
        textStyle: { color: '#1e293b' },
        formatter: (params: unknown) => {
          const p = params as { data?: { name?: string; mastery?: number; description?: string } }
          if (p.data && p.data.name) {
            const pct = p.data.mastery !== undefined ? Math.round(p.data.mastery * 100) : 0
            const desc = (p.data as { description?: string }).description || '无描述'
            const color = pct >= 75 ? '#22c55e' : pct >= 50 ? '#f97316' : '#ef4444'
            return `<div style="font-weight:bold;margin-bottom:4px">${p.data.name}</div>
                    <div style="color:#64748b;font-size:12px">掌握度: <span style="color:${color};font-weight:bold">${pct}%</span></div>
                    <div style="color:#64748b;font-size:12px;margin-top:4px">${desc}</div>`
          }
          return ''
        },
      },
      series: [{
        type: 'graph',
        layout: 'force',
        symbol: 'circle',
        roam: true,
        draggable: true,
        label: {
          show: true,
          position: 'inside',
          formatter: (params: unknown) => {
            const name = (params as { name?: string }).name ?? ''
            return name.length > 5 ? name.slice(0, 4) + '…' : name
          },
          fontSize: 11,
          fontWeight: 'bold',
          color: '#fff',
        },
        lineStyle: { width: 1.5, color: '#94a3b8', curveness: 0.3 },
        emphasis: {
          focus: 'adjacency',
          lineStyle: { width: 4, color: '#3b82f6' },
          itemStyle: { shadowBlur: 12, shadowColor: 'rgba(59,130,246,0.4)' },
        },
        data: graphNodes,
        links: graphLinks,
        categories: [
          { name: '已掌握', itemStyle: { color: '#22c55e' } },
          { name: '待巩固', itemStyle: { color: '#f97316' } },
          { name: '薄弱', itemStyle: { color: '#ef4444' } },
          { name: '当前', itemStyle: { color: '#3b82f6' } },
        ],
        force: {
          repulsion: 120,
          gravity: 0.05,
          edgeLength: 80,
          layoutAnimation: true,
        },
        itemStyle: { borderWidth: 2, borderColor: '#fff' },
      }],
    }

    chart.off('click')
    chart.on('click', (params: unknown) => {
      const p = params as { data?: { id?: string } }
      if (p.data?.id && onNodeClick) {
        onNodeClick(Number(p.data.id))
      }
    })

    chart.setOption(option, true)
  }, [nodes, currentKpId, onNodeClick])

  if (nodes.length === 0) {
    return (
      <div className="flex items-center justify-center h-64 text-slate-400">
        暂无知识点数据
      </div>
    )
  }

  return (
    <div className="relative">
      <div ref={chartRef} className="w-full h-80" />
      <div className="flex items-center justify-center gap-6 mt-4">
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded-full bg-green-500" />
          <span className="text-xs text-slate-600">已掌握 (≥75%)</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded-full bg-orange-500" />
          <span className="text-xs text-slate-600">待巩固 (50-75%)</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded-full bg-red-500" />
          <span className="text-xs text-slate-600">薄弱 (&lt;50%)</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded-full bg-blue-500 border-2 border-blue-800" />
          <span className="text-xs text-slate-600">当前推荐</span>
        </div>
      </div>
    </div>
  )
}
