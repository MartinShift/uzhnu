import { useCallback, useEffect, useMemo, useState } from 'react'
import { DragDropContext, type DropResult } from '@hello-pangea/dnd'
import { useTranslation } from 'react-i18next'
import { useNavigate } from 'react-router-dom'
import { projectsApi } from '../api/projects'
import type { Project, Stage } from '../types'
import { STAGES } from '../types'
import { Column } from '../components/Column'
import { CreateProjectModal } from '../components/CreateProjectModal'

export function BoardPage() {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const [projects, setProjects] = useState<Project[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [creating, setCreating] = useState(false)

  const load = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const p = await projectsApi.list()
      setProjects(p)
    } catch (err) {
      console.error(err)
      setError(String(err))
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    void load()
  }, [load])

  const grouped = useMemo(() => {
    const map: Record<Stage, Project[]> = {
      Sketch: [],
      ClientApproval: [],
      Drawings: [],
      Done: [],
    }
    for (const p of projects) {
      map[p.stage].push(p)
    }
    for (const s of STAGES) {
      map[s].sort((a, b) => a.position - b.position)
    }
    return map
  }, [projects])

  const onDragEnd = useCallback(
    async (result: DropResult) => {
      const { source, destination, draggableId } = result
      if (!destination) return
      if (
        source.droppableId === destination.droppableId &&
        source.index === destination.index
      ) {
        return
      }

      const id = Number(draggableId)
      const fromStage = source.droppableId as Stage
      const toStage = destination.droppableId as Stage

      const snapshot = projects
      const next = projects.map(p => ({ ...p }))

      const moving = next.find(p => p.id === id)
      if (!moving) return

      const sourceList = next
        .filter(p => p.stage === fromStage && p.id !== id)
        .sort((a, b) => a.position - b.position)
      sourceList.forEach((p, i) => (p.position = i))

      const targetList = next
        .filter(p => p.stage === toStage && p.id !== id)
        .sort((a, b) => a.position - b.position)

      moving.stage = toStage
      const insertAt = Math.min(destination.index, targetList.length)
      targetList.splice(insertAt, 0, moving)
      targetList.forEach((p, i) => (p.position = i))

      setProjects(next)

      try {
        await projectsApi.move(id, toStage, insertAt)
      } catch (err) {
        console.error(err)
        setProjects(snapshot)
      }
    },
    [projects]
  )

  if (loading) {
    return (
      <div className="flex-1 flex items-center justify-center text-slate-500">
        {t('board.loading')}
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center gap-3 text-center p-6">
        <p className="text-sm text-red-700 max-w-md">
          {t('board.loadError', { url: import.meta.env.VITE_API_URL ?? 'http://localhost:5080' })}
        </p>
        <button
          onClick={load}
          className="px-4 py-2 text-sm font-semibold text-white bg-brand-600 hover:bg-brand-700 rounded-md"
        >
          {t('board.retry')}
        </button>
      </div>
    )
  }

  return (
    <div className="flex-1 flex flex-col min-h-0">
      <div className="px-6 py-4 flex items-center justify-between">
        <h1 className="text-xl font-semibold text-slate-800">{t('nav.board')}</h1>
        <button
          onClick={() => setCreating(true)}
          className="px-3 py-1.5 text-sm font-semibold text-white bg-brand-600 hover:bg-brand-700 rounded-md shadow-sm"
        >
          {t('board.newProject')}
        </button>
      </div>

      <div className="flex-1 min-h-0 px-6 pb-6">
        <DragDropContext onDragEnd={onDragEnd}>
          <div className="h-full grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4 min-h-0">
            {STAGES.map(stage => (
              <Column
                key={stage}
                stage={stage}
                projects={grouped[stage]}
                onCardClick={p => navigate(`/projects/${p.id}`)}
              />
            ))}
          </div>
        </DragDropContext>
      </div>

      {creating && <CreateProjectModal onClose={() => setCreating(false)} />}
    </div>
  )
}
