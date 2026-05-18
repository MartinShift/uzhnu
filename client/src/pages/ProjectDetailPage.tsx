import { useCallback, useEffect, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { membersApi } from '../api/members'
import { projectsApi } from '../api/projects'
import type { Member, Priority, Project, Role, Stage } from '../types'
import { PRIORITIES, STAGES } from '../types'
import { priorityDot } from '../components/priority'
import { AssigneeDropdown } from '../components/AssigneeDropdown'
import { useAuth } from '../auth/AuthContext'

const roleStyles: Record<Role, string> = {
  Architect:   'bg-brand-50 text-brand-700 border-brand-200',
  Designer:    'bg-amber-50 text-amber-700 border-amber-200',
  Constructor: 'bg-slate-100 text-slate-700 border-slate-200',
}

export function ProjectDetailPage() {
  const { id } = useParams<{ id: string }>()
  const projectId = Number(id)
  const navigate = useNavigate()
  const { t, i18n } = useTranslation()
  const { user } = useAuth()
  const isGuest = !user

  const [project, setProject] = useState<Project | null>(null)
  const [members, setMembers] = useState<Member[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // form draft
  const [title, setTitle] = useState('')
  const [clientName, setClientName] = useState('')
  const [description, setDescription] = useState('')
  const [stage, setStage] = useState<Stage>('Sketch')
  const [priority, setPriority] = useState<Priority>('Medium')
  const [dueDate, setDueDate] = useState('')

  const [saving, setSaving] = useState(false)
  const [savedAt, setSavedAt] = useState<number | null>(null)

  // attachment draft
  const [newAttLabel, setNewAttLabel] = useState('')
  const [newAttUrl, setNewAttUrl] = useState('')

  // comment draft
  const [commentText, setCommentText] = useState('')
  const [postingComment, setPostingComment] = useState(false)

  const load = useCallback(async () => {
    if (!projectId || Number.isNaN(projectId)) {
      setError('invalid')
      setLoading(false)
      return
    }
    setLoading(true)
    setError(null)
    try {
      const [p, m] = await Promise.all([
        projectsApi.get(projectId),
        membersApi.list(),
      ])
      setProject(p)
      setMembers(m)
      setTitle(p.title)
      setClientName(p.clientName)
      setDescription(p.description ?? '')
      setStage(p.stage)
      setPriority(p.priority)
      setDueDate(p.dueDate ? p.dueDate.slice(0, 10) : '')
    } catch (err) {
      console.error(err)
      setError(String(err))
    } finally {
      setLoading(false)
    }
  }, [projectId])

  useEffect(() => {
    void load()
  }, [load])

  async function handleSave() {
    if (!project) return
    if (!title.trim()) return
    setSaving(true)
    try {
      const updated = await projectsApi.update(project.id, {
        title: title.trim(),
        clientName: clientName.trim(),
        description: description.trim() || null,
        priority,
        dueDate: dueDate ? new Date(dueDate).toISOString() : null,
      })
      if (updated.stage !== stage) {
        await projectsApi.move(updated.id, stage, 0)
      }
      await load()
      setSavedAt(Date.now())
    } catch (err) {
      console.error(err)
    } finally {
      setSaving(false)
    }
  }

  async function handleDelete() {
    if (!project) return
    if (!confirm(t('detail.deleteConfirm'))) return
    await projectsApi.remove(project.id)
    navigate('/')
  }

  async function assignMember(memberId: number) {
    if (!project) return
    await projectsApi.assignMember(project.id, memberId)
    await load()
  }

  async function unassignMember(memberId: number) {
    if (!project) return
    await projectsApi.unassignMember(project.id, memberId)
    await load()
  }

  async function addAttachment() {
    if (!project) return
    if (!newAttLabel.trim() || !newAttUrl.trim()) return
    await projectsApi.addAttachment(project.id, newAttLabel.trim(), newAttUrl.trim())
    setNewAttLabel('')
    setNewAttUrl('')
    await load()
  }

  async function removeAttachment(attId: number) {
    await projectsApi.removeAttachment(attId)
    await load()
  }

  async function postComment(e: React.FormEvent) {
    e.preventDefault()
    if (!project) return
    if (!commentText.trim()) return
    setPostingComment(true)
    try {
      await projectsApi.addComment(project.id, commentText.trim())
      setCommentText('')
      await load()
    } finally {
      setPostingComment(false)
    }
  }

  async function removeComment(commentId: number) {
    await projectsApi.removeComment(commentId)
    await load()
  }

  if (loading) {
    return (
      <div className="flex-1 flex items-center justify-center text-slate-500">
        {t('board.loading')}
      </div>
    )
  }

  if (error || !project) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center gap-3 p-6">
        <p className="text-sm text-red-700">{t('detail.notFound')}</p>
        <Link to="/" className="text-brand-700 hover:text-brand-800 font-medium">
          {t('detail.back')}
        </Link>
      </div>
    )
  }

  const created = new Date(project.createdAt).toLocaleDateString(
    i18n.resolvedLanguage === 'en' ? 'en-GB' : 'uk-UA',
    { day: '2-digit', month: 'short', year: 'numeric' }
  )

  const assignedIds = new Set(project.members.map(m => m.id))
  const availableMembers = members.filter(m => !assignedIds.has(m.id))

  return (
    <div className="flex-1 overflow-y-auto bg-slate-50">
      <div className="mx-auto max-w-5xl px-6 py-6">
        <div className="flex items-center justify-between mb-4">
          <Link
            to="/"
            className="text-sm font-medium text-slate-600 hover:text-brand-700"
          >
            {t('detail.back')}
          </Link>
          <div className="flex items-center gap-3">
            {savedAt && !isGuest && (
              <span className="text-xs text-emerald-600">{t('detail.saved')}</span>
            )}
            {!isGuest && (
              <button
                onClick={handleSave}
                disabled={saving || !title.trim()}
                className="px-4 py-2 text-sm font-semibold text-white bg-brand-600 hover:bg-brand-700 rounded-md disabled:opacity-50"
              >
                {t('detail.save')}
              </button>
            )}
          </div>
        </div>

        {isGuest && (
          <div className="mb-4 flex items-center justify-between gap-3 bg-amber-50 border border-amber-200 rounded-md px-4 py-2.5">
            <p className="text-sm text-amber-800">{t('detail.guestBanner')}</p>
            <Link
              to={`/login?next=${encodeURIComponent(`/projects/${projectId}`)}`}
              className="shrink-0 px-3 py-1.5 text-xs font-semibold text-white bg-brand-600 hover:bg-brand-700 rounded-md"
            >
              {t('nav.login')}
            </Link>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-[1fr_320px] gap-6">
          <div className="space-y-6">
            <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm">
              <input
                value={title}
                onChange={e => setTitle(e.target.value)}
                placeholder={t('detail.title')}
                readOnly={isGuest}
                className="block w-full text-2xl font-semibold text-slate-900 bg-transparent border-0 border-b border-transparent focus:border-brand-400 focus:outline-none pb-2 mb-4 read-only:cursor-default"
              />

              <Field label={t('detail.description')}>
                <textarea
                  value={description}
                  onChange={e => setDescription(e.target.value)}
                  rows={5}
                  placeholder={t('detail.descriptionPlaceholder')}
                  readOnly={isGuest}
                  className="detail-input resize-none"
                />
              </Field>
            </div>

            <Section label={t('detail.attachments')}>
              {project.attachments.length === 0 && (
                <p className="text-xs text-slate-400 italic mb-3">—</p>
              )}
              <ul className="space-y-2 mb-3">
                {project.attachments.map(a => (
                  <li
                    key={a.id}
                    className="flex items-center justify-between bg-slate-50 border border-slate-200 rounded-md px-3 py-2"
                  >
                    <div className="min-w-0 flex-1">
                      <div className="text-sm font-medium text-slate-800 truncate">{a.label}</div>
                      <a
                        href={a.url}
                        target="_blank"
                        rel="noreferrer"
                        className="text-xs text-brand-700 hover:text-brand-800 underline truncate block"
                      >
                        {a.url}
                      </a>
                    </div>
                    {!isGuest && (
                      <button
                        onClick={() => removeAttachment(a.id)}
                        className="ml-3 text-slate-400 hover:text-red-600 text-sm shrink-0"
                      >
                        ×
                      </button>
                    )}
                  </li>
                ))}
              </ul>
              {!isGuest && (
                <div className="flex flex-col sm:flex-row gap-2">
                  <input
                    value={newAttLabel}
                    onChange={e => setNewAttLabel(e.target.value)}
                    placeholder={t('detail.attachmentLabel')}
                    className="detail-input sm:flex-1"
                  />
                  <input
                    value={newAttUrl}
                    onChange={e => setNewAttUrl(e.target.value)}
                    placeholder={t('detail.attachmentUrl')}
                    className="detail-input sm:flex-[2]"
                  />
                  <button
                    onClick={addAttachment}
                    disabled={!newAttLabel.trim() || !newAttUrl.trim()}
                    className="px-3 py-2 text-xs font-semibold text-white bg-brand-600 hover:bg-brand-700 rounded-md disabled:opacity-50"
                  >
                    {t('detail.addAttachment')}
                  </button>
                </div>
              )}
            </Section>

            <Section label={t('detail.comments')}>
              {project.comments.length === 0 && (
                <p className="text-xs text-slate-400 italic mb-3">{t('detail.noComments')}</p>
              )}
              <ul className="space-y-3 mb-4">
                {project.comments.map(c => (
                  <li
                    key={c.id}
                    className="bg-slate-50 border border-slate-200 rounded-md p-3"
                  >
                    <div className="flex items-center justify-between mb-1">
                      <div className="flex items-center gap-2">
                        <div className="w-7 h-7 rounded-full bg-brand-100 text-brand-700 text-xs font-semibold flex items-center justify-center">
                          {initials(c.author)}
                        </div>
                        <span className="text-sm font-medium text-slate-800">{c.author}</span>
                        <span className="text-xs text-slate-400">
                          {new Date(c.createdAt).toLocaleString(
                            i18n.resolvedLanguage === 'en' ? 'en-GB' : 'uk-UA',
                            { day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit' }
                          )}
                        </span>
                      </div>
                      {!isGuest && (
                        <button
                          onClick={() => removeComment(c.id)}
                          className="text-slate-300 hover:text-red-600 text-sm"
                        >
                          ×
                        </button>
                      )}
                    </div>
                    <p className="text-sm text-slate-700 whitespace-pre-wrap pl-9">{c.text}</p>
                  </li>
                ))}
              </ul>
              {isGuest ? (
                <Link
                  to={`/login?next=${encodeURIComponent(`/projects/${projectId}`)}`}
                  className="inline-block text-xs font-medium text-brand-700 hover:text-brand-800"
                >
                  {t('detail.loginToComment')}
                </Link>
              ) : (
                <form onSubmit={postComment} className="space-y-2">
                  <textarea
                    value={commentText}
                    onChange={e => setCommentText(e.target.value)}
                    placeholder={t('detail.commentPlaceholder')}
                    rows={3}
                    className="detail-input resize-none"
                  />
                  <div className="flex justify-end">
                    <button
                      type="submit"
                      disabled={postingComment || !commentText.trim()}
                      className="px-3 py-1.5 text-xs font-semibold text-white bg-brand-600 hover:bg-brand-700 rounded-md disabled:opacity-50"
                    >
                      {t('detail.post')}
                    </button>
                  </div>
                </form>
              )}
            </Section>
          </div>

          <aside className="space-y-4">
            <SidebarCard>
              <SidebarField label={t('detail.stage')}>
                <select
                  value={stage}
                  onChange={e => setStage(e.target.value as Stage)}
                  disabled={isGuest}
                  className="detail-input"
                >
                  {STAGES.map(s => (
                    <option key={s} value={s}>{t(`stage.${s}`)}</option>
                  ))}
                </select>
              </SidebarField>

              <SidebarField label={t('detail.priority')}>
                <div className="flex items-center gap-2">
                  <span className={`w-2 h-2 rounded-full ${priorityDot[priority]}`} />
                  <select
                    value={priority}
                    onChange={e => setPriority(e.target.value as Priority)}
                    disabled={isGuest}
                    className="detail-input flex-1"
                  >
                    {PRIORITIES.map(p => (
                      <option key={p} value={p}>{t(`priority.${p}`)}</option>
                    ))}
                  </select>
                </div>
              </SidebarField>

              <SidebarField label={t('detail.issuer')}>
                <input
                  value={clientName}
                  onChange={e => setClientName(e.target.value)}
                  readOnly={isGuest}
                  className="detail-input"
                />
              </SidebarField>

              <SidebarField label={t('detail.dueDate')}>
                <input
                  type="date"
                  value={dueDate}
                  onChange={e => setDueDate(e.target.value)}
                  readOnly={isGuest}
                  className="detail-input"
                />
              </SidebarField>

              <div className="text-xs text-slate-400 pt-1">
                {t('detail.createdAt')}: {created}
              </div>
            </SidebarCard>

            <SidebarCard>
              <div className="text-xs font-semibold uppercase tracking-wider text-slate-500 mb-3">
                {t('detail.members')}
              </div>

              {project.members.length === 0 ? (
                <p className="text-xs text-slate-400 italic mb-3">{t('detail.noAssignees')}</p>
              ) : (
                <div className="flex flex-wrap gap-1.5 mb-3">
                  {project.members.map(m => (
                    <span
                      key={m.id}
                      className={`inline-flex items-center gap-1 text-xs font-medium pl-2 ${isGuest ? 'pr-2' : 'pr-1'} py-1 rounded-full border ${roleStyles[m.role]}`}
                      title={t(`role.${m.role}`)}
                    >
                      {m.name}
                      {!isGuest && (
                        <button
                          type="button"
                          onClick={() => unassignMember(m.id)}
                          className="ml-1 w-4 h-4 rounded-full hover:bg-white/60 flex items-center justify-center text-slate-500 hover:text-red-600"
                          aria-label="Remove"
                        >
                          ×
                        </button>
                      )}
                    </span>
                  ))}
                </div>
              )}

              {!isGuest && (
                members.length === 0 ? (
                  <p className="text-xs text-slate-500">{t('detail.noMembersHint')}</p>
                ) : availableMembers.length === 0 ? (
                  <p className="text-xs text-slate-400 italic">{t('detail.noAvailableMembers')}</p>
                ) : (
                  <AssigneeDropdown
                    available={availableMembers}
                    onPick={id => void assignMember(id)}
                  />
                )
              )}
            </SidebarCard>

            {!isGuest && (
              <button
                onClick={handleDelete}
                className="w-full px-3 py-2 text-sm font-medium text-red-600 hover:bg-red-50 rounded-md border border-red-200"
              >
                {t('detail.delete')}
              </button>
            )}
          </aside>
        </div>
      </div>

      <style>{`
        .detail-input {
          display: block;
          width: 100%;
          border-radius: 0.5rem;
          border: 1px solid rgb(203 213 225);
          background-color: white;
          padding: 0.5rem 0.75rem;
          font-size: 0.875rem;
          color: rgb(15 23 42);
          outline: none;
        }
        .detail-input:focus {
          border-color: rgb(13 148 136);
          box-shadow: 0 0 0 3px rgb(204 251 241);
        }
        .detail-input:read-only,
        .detail-input:disabled {
          background-color: rgb(248 250 252);
          color: rgb(71 85 105);
          cursor: default;
        }
      `}</style>
    </div>
  )
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <label className="block">
      <span className="block text-xs font-medium uppercase tracking-wide text-slate-500 mb-1">
        {label}
      </span>
      {children}
    </label>
  )
}

function Section({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm">
      <h2 className="text-sm font-semibold uppercase tracking-wider text-slate-500 mb-3">
        {label}
      </h2>
      {children}
    </div>
  )
}

function SidebarCard({ children }: { children: React.ReactNode }) {
  return (
    <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm space-y-3">
      {children}
    </div>
  )
}

function SidebarField({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div>
      <div className="text-[10px] font-semibold uppercase tracking-wider text-slate-500 mb-1">
        {label}
      </div>
      {children}
    </div>
  )
}

function initials(name: string) {
  return name
    .split(' ')
    .map(s => s[0])
    .filter(Boolean)
    .slice(0, 2)
    .join('')
    .toUpperCase()
}
