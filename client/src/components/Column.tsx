import { Droppable, Draggable } from '@hello-pangea/dnd'
import { useTranslation } from 'react-i18next'
import type { Project, Stage } from '../types'
import { ProjectCard } from './ProjectCard'

const stageAccent: Record<Stage, string> = {
  Sketch:         'bg-sky-500',
  ClientApproval: 'bg-amber-500',
  Drawings:       'bg-violet-500',
  Done:           'bg-emerald-500',
}

interface Props {
  stage: Stage
  projects: Project[]
  onCardClick: (project: Project) => void
}

export function Column({ stage, projects, onCardClick }: Props) {
  const { t } = useTranslation()

  return (
    <div className="flex flex-col bg-slate-100/70 rounded-xl border border-slate-200 min-h-0">
      <div className="flex items-center justify-between px-4 py-3 border-b border-slate-200">
        <div className="flex items-center gap-2">
          <span className={`w-2 h-2 rounded-full ${stageAccent[stage]}`} />
          <h2 className="font-semibold text-sm text-slate-700">
            {t(`stage.${stage}`)}
          </h2>
        </div>
        <span className="text-xs text-slate-400 font-medium">
          {projects.length}
        </span>
      </div>

      <Droppable droppableId={stage}>
        {(provided, snapshot) => (
          <div
            ref={provided.innerRef}
            {...provided.droppableProps}
            className={`kanban-col flex-1 min-h-[140px] overflow-y-auto px-3 py-3 space-y-2 transition-colors rounded-b-xl border-2 border-dashed ${
              snapshot.isDraggingOver
                ? 'bg-brand-50 border-brand-400'
                : 'border-transparent'
            }`}
          >
            {projects.length === 0 && (
              <div
                className={`text-xs text-center py-8 select-none transition-colors ${
                  snapshot.isDraggingOver ? 'text-brand-600 font-medium' : 'text-slate-400'
                }`}
              >
                {t('board.empty')}
              </div>
            )}

            {projects.map((p, index) => (
              <Draggable key={p.id} draggableId={String(p.id)} index={index}>
                {(prov, snap) => (
                  <div
                    ref={prov.innerRef}
                    {...prov.draggableProps}
                    {...prov.dragHandleProps}
                    style={prov.draggableProps.style}
                    className={`transition-shadow ${
                      snap.isDragging
                        ? 'rotate-2 scale-[1.02] shadow-2xl ring-2 ring-brand-400'
                        : ''
                    } rounded-lg`}
                  >
                    <ProjectCard
                      project={p}
                      onClick={() => onCardClick(p)}
                      isDragging={snap.isDragging}
                    />
                  </div>
                )}
              </Draggable>
            ))}
            {provided.placeholder}
          </div>
        )}
      </Droppable>
    </div>
  )
}
