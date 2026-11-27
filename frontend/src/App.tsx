import { useRef, useState, type FormEvent } from 'react'
import './App.css'

type EvidenceItem = {
  source?: string
  page?: number
  document_id?: string
  section?: string | null
}

type AnswerResponse = {
  answer: string
  evidence: EvidenceItem[]
  confidence: 'high' | 'medium' | 'low' | string
  confidence_reason: string
  escalation_required: boolean
  escalation_reason?: string | null
  follow_up_questions: string[]
}

type ChatMessage = {
  id: number
  role: 'user' | 'assistant'
  content: string
}

const suggestions = [
  {
    label: 'ONBOARDING',
    question: 'What documents are required before onboarding?',
  },
  {
    label: 'EMPLOYEE BENEFITS',
    question: 'What does the policy say about annual leave?',
  },
  {
    label: 'EMPLOYEE LIFECYCLE',
    question: 'What are the steps in the employee lifecycle?',
  },
  {
    label: 'POLICY REVIEW',
    question: 'What information is missing from the uploaded policy?',
  },
]

function App() {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [question, setQuestion] = useState('')
  const [isSending, setIsSending] = useState(false)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [isUploading, setIsUploading] = useState(false)
  const [uploadStatus, setUploadStatus] = useState(
    'No document uploaded in this session.',
  )
  const [uploadedDocument, setUploadedDocument] = useState<{
    name: string
    details: string
  } | null>(null)
  const [answerData, setAnswerData] = useState<AnswerResponse | null>(null)
  const [errorMessage, setErrorMessage] = useState('')

  const fileInputRef = useRef<HTMLInputElement>(null)

  async function askQuestion(
    event?: FormEvent<HTMLFormElement>,
    suggestedQuestion?: string,
  ) {
    event?.preventDefault()

    const cleanQuestion = (suggestedQuestion ?? question).trim()
    if (!cleanQuestion || isSending) return

    setMessages((current) => [
      ...current,
      { id: Date.now(), role: 'user', content: cleanQuestion },
    ])
    setQuestion('')
    setErrorMessage('')
    setIsSending(true)

    setMessages((current) => [
      ...current,
      {
        id: Date.now() + 1,
        role: 'assistant',
        content: 'Searching policy evidence and assessing the answer…',
      },
    ])

    try {
      const response = await fetch('/api/v1/chat/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: cleanQuestion }),
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.detail || 'The chat request failed.')
      }

      setMessages((current) =>
        current.map((message) =>
          message.role === 'assistant' &&
          message.content === 'Searching policy evidence and assessing the answer…'
            ? {
                ...message,
                content: data.answer || 'No answer was returned.',
              }
            : message,
        ),
      )
      setAnswerData(data)
    } catch (error) {
      const detail =
        error instanceof Error ? error.message : 'Unexpected request error.'

      setErrorMessage(`Request error: ${detail}`)
      setMessages((current) =>
        current.map((message) =>
          message.role === 'assistant' &&
          message.content === 'Searching policy evidence and assessing the answer…'
            ? { ...message, content: "I couldn't complete that request." }
            : message,
        ),
      )
    } finally {
      setIsSending(false)
    }
  }

  function handleFileChange(event: React.ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0] ?? null
    setSelectedFile(file)
    setUploadStatus(
      file ? `Selected: ${file.name}` : 'No document selected.',
    )
  }

  async function uploadDocument(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()

    if (!selectedFile) {
      setUploadStatus('Choose a PDF file first.')
      return
    }

    if (selectedFile.size > 10 * 1024 * 1024) {
      setUploadStatus('The PDF must be 10 MB or smaller.')
      return
    }

    setIsUploading(true)
    setUploadStatus('Uploading and indexing document…')

    const formData = new FormData()
    formData.append('file', selectedFile)

    try {
      const response = await fetch('/api/v1/documents/upload', {
        method: 'POST',
        body: formData,
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.detail || 'Upload failed.')
      }

      const pages = data.pages_processed ?? '?'
      const chunks = data.chunks_created ?? '?'

      setUploadStatus(`Upload complete · ${pages} pages · ${chunks} chunks`)
      setUploadedDocument({
        name: data.filename || selectedFile.name,
        details: `${pages} pages · Indexed`,
      })
      setSelectedFile(null)

      if (fileInputRef.current) {
        fileInputRef.current.value = ''
      }
    } catch (error) {
      const detail =
        error instanceof Error ? error.message : 'Unexpected upload error.'
      setUploadStatus(`Upload error: ${detail}`)
    } finally {
      setIsUploading(false)
    }
  }

  function startNewChat() {
    setMessages([])
    setQuestion('')
    setErrorMessage('')
    setAnswerData(null)
  }

  function renderEvidence(items: EvidenceItem[] = []) {
    if (!items.length) {
      return <p className="evidence-empty">No supporting evidence was returned.</p>
    }

    return items.map((item, index) => (
      <div className="evidence-item" key={`${item.document_id}-${item.page}-${index}`}>
        <strong>{item.source || 'Policy source'}</strong>
        <small>
          {item.page ? `Page ${item.page}` : 'Page not specified'}
          {item.section ? ` · ${item.section}` : ''}
          {item.document_id ? ` · ID: ${item.document_id}` : ''}
        </small>
      </div>
    ))
  }

  return (
    <div className="app">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">E</div>
          <div>
            EOR Copilot
            <small>Compliance workspace</small>
          </div>
        </div>

        <button className="new-chat" id="new-chat" onClick={startNewChat}>
          ＋ New conversation
        </button>

        <div>
          <p className="nav-label">Workspace</p>
          <div className="nav-item active">
            <span className="nav-icon">◈</span>
            Compliance assistant
          </div>
          <div className="nav-item">
            <span className="nav-icon">▤</span>
            Policy documents
          </div>
          <div className="nav-item">
            <span className="nav-icon">✓</span>
            Review &amp; escalation
          </div>
        </div>

        <div className="sidebar-spacer" />

        <div className="workspace-card">
          <strong>
            <span className="status-dot" />
            Local demo environment
          </strong>
          <p>
            Answers are grounded in uploaded policy documents. Missing or
            high-risk information should be escalated.
          </p>
        </div>
      </aside>

      <main className="main">
        <header className="topbar">
          <div>
            <h1>Compliance assistant</h1>
            <p>Ask questions about employment policies and EOR processes.</p>
          </div>
          <div className="topbar-status">
            <span className="status-dot" />
            Local assistant
          </div>
        </header>

        <div className="content">
          <section className="chat-column">
            {messages.length === 0 && (
              <div className="welcome">
                <div className="welcome-mark">✦</div>
                <h2>Your EOR compliance copilot</h2>
                <p>
                  Get policy-grounded answers with supporting evidence,
                  confidence signals, and escalation when the documents don’t
                  provide enough information.
                </p>

                <div className="suggestions">
                  {suggestions.map((item) => (
                    <button
                      className="suggestion"
                      key={item.label}
                      onClick={() => void askQuestion(undefined, item.question)}
                      disabled={isSending}
                    >
                      <span>{item.label}</span>
                      {item.question}
                    </button>
                  ))}
                </div>
              </div>
            )}

            <div className="messages">
              {messages.map((message) => (
                <div className={`message ${message.role}`} key={message.id}>
                  <div className="avatar">
                    {message.role === 'user' ? 'You' : 'AI'}
                  </div>
                  <div className="message-body">
                    <p className="message-label">
                      {message.role === 'user' ? 'You' : 'EOR Copilot'}
                    </p>
                    <div className="bubble">{message.content}</div>
                  </div>
                </div>
              ))}
            </div>

            <div className="composer-wrap">
              <form
                className="composer"
                onSubmit={(event) => void askQuestion(event)}
              >
                <textarea
                  value={question}
                  onChange={(event) => setQuestion(event.target.value)}
                  maxLength={5000}
                  required
                  placeholder="Ask a question about your employment policy…"
                  disabled={isSending}
                />
                <div className="composer-bottom">
                  <span className="composer-hint">
                    Answers use uploaded evidence · Verify high-risk decisions
                  </span>
                  <button
                    className="send-button"
                    type="submit"
                    disabled={!question.trim() || isSending}
                  >
                    {isSending ? 'Thinking…' : 'Ask Copilot ↗'}
                  </button>
                </div>
              </form>
              <p className="error-message">{errorMessage}</p>
            </div>
          </section>

          <aside className="side-panel">
            <section className="panel">
              <div className="panel-heading">
                <h2>Knowledge base</h2>
                <span className="panel-kicker">PDF</span>
              </div>

              <form onSubmit={(event) => void uploadDocument(event)}>
                <div className="upload-zone">
                  <div className="upload-icon">⇧</div>
                  <p>
                    Upload a policy document
                    <br />
                    PDF format · Maximum 10 MB
                  </p>
                  <input
                    ref={fileInputRef}
                    className="file-input"
                    type="file"
                    accept="application/pdf,.pdf"
                    onChange={handleFileChange}
                  />
                  <button
                    className="secondary-button"
                    type="button"
                    onClick={() => fileInputRef.current?.click()}
                  >
                    Choose PDF
                  </button>
                </div>

                <p className="upload-status">{uploadStatus}</p>
                {selectedFile && (
                  <button
                    className="secondary-button"
                    type="submit"
                    disabled={isUploading}
                  >
                    {isUploading ? 'Uploading…' : 'Upload selected PDF'}
                  </button>
                )}
              </form>

              {uploadedDocument && (
                <div className="document-status">
                  <div className="file-icon">PDF</div>
                  <div>
                    <strong>{uploadedDocument.name}</strong>
                    <small>{uploadedDocument.details}</small>
                  </div>
                </div>
              )}
            </section>

            <section className="panel">
              <div className="panel-heading">
                <h2>Answer assessment</h2>
                <span className="panel-kicker">Latest</span>
              </div>

              <div className="metric-row">
                <span>Confidence</span>
                <strong
                  className={`confidence-value ${answerData?.confidence ?? ''}`}
                >
                  {answerData?.confidence ?? 'Not assessed'}
                </strong>
              </div>
              <div className="metric-row">
                <span>Escalation</span>
                <strong>
                  {answerData
                    ? answerData.escalation_required
                      ? 'Required'
                      : 'Not required'
                    : '—'}
                </strong>
              </div>

              {answerData?.escalation_required && answerData.escalation_reason && (
                <div className="escalation-box">
                  {answerData.escalation_reason}
                </div>
              )}

              <div className="metric-row" style={{ marginTop: 10 }}>
                <span>Assessment rationale</span>
              </div>
              <p className="evidence-empty">
                {answerData?.confidence_reason ||
                  'Submit a question to see the assessment rationale.'}
              </p>
            </section>

            <section className="panel">
              <div className="panel-heading">
                <h2>Evidence</h2>
                <span className="panel-kicker">
                  {answerData?.evidence?.length ?? 0} sources
                </span>
              </div>
              {renderEvidence(answerData?.evidence)}
            </section>

            {Boolean(answerData?.follow_up_questions?.length) && (
              <section className="panel">
                <div className="panel-heading">
                  <h2>Suggested follow-ups</h2>
                </div>
                <ul className="followup-list">
                  {answerData?.follow_up_questions.map((followUp, index) => (
                    <li key={`${followUp}-${index}`}>
                      <button
                        type="button"
                        onClick={() => void askQuestion(undefined, followUp)}
                        disabled={isSending}
                      >
                        {followUp}
                      </button>
                    </li>
                  ))}
                </ul>
              </section>
            )}
          </aside>
        </div>
      </main>
    </div>
  )
}

export default App