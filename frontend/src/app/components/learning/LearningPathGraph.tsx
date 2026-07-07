import React, { useEffect, useRef } from 'react'
import * as echarts from 'echarts'

export interface KpNode {
  kp_id: number
  kp_name: string
  mastery: number // 0-1
  is_current_recommend?: boolean
  dependencies?: number[] // 前置知识点IDs
  difficulty_level?: number
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

    // 初始化图表实例
    chartInstance.current = echarts.init(chartRef.current)
    chartInstance.current.on('click', (params) => {
      if (params.dataType === 'node' && params.data && onNodeClick) {
        const kpId = (params.data as { kp_id?: number }).kp_id
        if (kpId !== undefined) {
          onNodeClick(kpId)
        }
      }
    })

    return () => {
      chartInstance.current?.dispose()
    }
  }, [onNodeClick])

  useEffect(() => {
    if (!chartInstance.current || nodes.length === 0) return

    // 构建节点数据
    const graphNodes: echarts.EChartsOption['series'] = []
    const categoryCount = 3 // 将节点分成3个分类展示

    // 根据 mastery 分配分类
    const categorizedNodes = nodes.map((node, index) => ({
      ...node,
      category: Math.floor(node.mastery * categoryCount),
    }))

    // 布局：使用简单的层级布局
    // 按 mastery 分层
    const levels: KpNode[][] = [[], [], []]
    categorizedNodes.forEach((node) => {
      levels[node.category].push(node)
    })

    // 构建 ECharts 图形节点
    const echartsNodes = nodes.map((node, index) => {
      // 节点颜色
      let nodeColor = '#22c55e' // 绿色 - 已掌握
      if (node.mastery < 0.5) {
        nodeColor = '#ef4444' // 红色 - 薄弱点
      } else if (node.mastery < 0.75) {
        nodeColor = '#f97316' // 橙色 - 待巩固
      }

      // 当前推荐节点加蓝色描边
      const isCurrentRecommend = node.is_current_recommend || node.kp_id === currentKpId

      return {
        id: String(node.kp_id),
        kp_id: node.kp_id,
        name: node.kp_name,
        value: [index % 3, Math.floor(index / 3)],
        symbolSize: isCurrentRecommend ? 70 : 55,
        itemStyle: {
          color: nodeColor,
          borderColor: isCurrentRecommend ? '#3b82f6' : undefined,
          borderWidth: isCurrentRecommend ? 4 : 2,
        },
        label: {
          show: true,
          formatter: node.kp_name.length > 6 ? node.kp_name.slice(0, 5) + '...' : node.kp_name,
          fontSize: 11,
          fontWeight: 'bold',
          color: '#fff',
        },
        mastery: node.mastery,
        description: node.description,
      }
    })

    // 构建连线数据
    const edges: Array<{ source: string; target: string; lineStyle?: { color?: string; type?: string } }> = []
    nodes.forEach((node) => {
      if (node.dependencies && node.dependencies.length > 0) {
        node.dependencies.forEach((depId) => {
          edges.push({
            source: String(depId),
            target: String(node.kp_id),
            lineStyle: {
              color: '#94a3b8',
              type: 'solid',
            },
          })
        })
      }
    })

    const option: echarts.EChartsOption = {
      tooltip: {
        trigger: 'item',
        triggerOn: 'mousemove',
        backgroundColor: 'rgba(255, 255, 255, 0.95)',
        borderColor: '#e2e8f0',
        borderWidth: 1,
        padding: [12, 16],
        textStyle: {
          color: '#1e293b',
        },
        formatter: (params: unknown) => {
          const p = params as { data?: { name?: string; mastery?: number; description?: string } }
          if (p.data && p.data.name) {
            const masteryPercent = p.data.mastery !== undefined ? Math.round(p.data.mastery * 100) : 0
            const desc = p.data.description || '无描述'
            return `<div style="font-weight: bold; margin-bottom: 4px;">${p.data.name}</div>
                    <div style="color: #64748b; font-size: 12px;">掌握度: <span style="color: ${masteryPercent >= 75 ? '#22c55e' : masteryPercent >= 50 ? '#f97316' : '#ef4444'}; font-weight: bold;">${masteryPercent}%</span></div>
                    <div style="color: #64748b; font-size: 12px; margin-top: 4px;">${desc}</div>`
          }
          return ''
        },
      },
      series: [
        {
          type: 'graph',
          layout: 'none',
          symbol: 'circle',
          roam: false,
          label: {
            show: true,
            position: 'inside',
            formatter: '{b}',
          },
          lineStyle: {
            width: 2,
            curveness: 0.3,
            color: '#94a3b8',
          },
          emphasis: {
            focus: 'adjacency',
            lineStyle: {
              width: 4,
              color: '#3b82f6',
            },
          },
          data: echartsNodes,
          links: edges,
          itemStyle: {
            borderWidth: 2,
            borderColor: '#fff',
          },
        },
      ],
      xAxis: {
        show: false,
        min: -0.5,
        max: 2.5,
      },
      yAxis: {
        show: false,
        min: -0.5,
        max: Math.ceil(nodes.length / 3) + 0.5,
      },
    }

    chartInstance.current.setOption(option)

    // 响应窗口大小变化
    const handleResize = () => {
      chartInstance.current?.resize()
    }
    window.addEventListener('resize', handleResize)

    return () => {
      window.removeEventListener('resize', handleResize)
    }
  }, [nodes, currentKpId])

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
      {/* 图例 */}
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
          <span className="text-xs text-slate-600">薄弱点 (&lt;50%)</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded-full bg-white border-2 border-blue-500" />
          <span className="text-xs text-slate-600">当前推荐</span>
        </div>
      </div>
    </div>
  )
}
