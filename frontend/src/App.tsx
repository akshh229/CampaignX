import { useState } from 'react'
import BriefInput from './components/BriefInput'
import ApprovalPanel from './components/ApprovalPanel'
import MetricsDashboard from './components/MetricsDashboard'

const API_BASE = 'http://localhost:8000'

function App() {
  const [threadId, setThreadId] = useState<string | null>(null)
  const [campaignState, setCampaignState] = useState<any>(null)
  const [phase, setPhase] = useState<'input' | 'approval' | 'metrics'>('input')
  const [error, setError] = useState<string | null>(null)

  const handleBriefSubmit = async (brief: string) => {
    setError(null)
    try {
      const res = await fetch(`${API_BASE}/api/campaign/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ brief }),
      })
      const data = await res.json()
      setThreadId(data.thread_id)
      setCampaignState(data.state)
      setPhase('approval')
    } catch (e: any) {
      setError(e.message || 'Failed to start campaign')
    }
  }

  const handleApproval = async (decision: 'approved' | 'rejected') => {
    setError(null)
    try {
      const res = await fetch(`${API_BASE}/api/campaign/approve`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ thread_id: threadId, decision }),
      })
      const data = await res.json()
      setCampaignState(data.state)
      if (decision === 'approved') setPhase('metrics')
      else setPhase('approval')
    } catch (e: any) {
      setError(e.message || 'Failed to process approval')
    }
  }

  return (
    <div style={{ minHeight: '100vh', background: '#0f172a', color: '#f1f5f9', fontFamily: 'Inter, sans-serif', padding: '2rem' }}>
      <h1 style={{ color: '#38bdf8', fontSize: '2rem', marginBottom: '0.5rem' }}>🚀 CampaignX — AI Campaign Manager</h1>
      <p style={{ color: '#64748b', marginBottom: '2rem', fontSize: '14px' }}>Multi-agent AI system for SuperBFSI email campaigns</p>
      {error && <div style={{ background: '#7f1d1d', color: '#fca5a5', padding: '1rem', borderRadius: '8px', marginBottom: '1rem', maxWidth: '800px' }}>{error}</div>}
      {phase === 'input' && <BriefInput onSubmit={handleBriefSubmit} />}
      {phase === 'approval' && campaignState && <ApprovalPanel state={campaignState} onApprove={handleApproval} />}
      {phase === 'metrics' && campaignState && <MetricsDashboard state={campaignState} />}
    </div>
  )
}

export default App
