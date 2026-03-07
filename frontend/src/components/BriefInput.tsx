import { useState } from 'react'

export default function BriefInput({ onSubmit }: { onSubmit: (brief: string) => void }) {
  const [brief, setBrief] = useState(
    "Run email campaign for launching XDeposit, a flagship term deposit product from SuperBFSI, that gives 1 percentage point higher returns than its competitors. Announce an additional 0.25 percentage point higher returns for female senior citizens. Optimise for open rate and click rate. Don't skip emails to customers marked 'inactive'. Include the call to action: https://superbfsi.com/xdeposit/explore/."
  )
  const [loading, setLoading] = useState(false)

  const handleSubmit = async () => {
    setLoading(true)
    await onSubmit(brief)
    setLoading(false)
  }

  return (
    <div style={{ background: '#1e293b', borderRadius: '12px', padding: '2rem', maxWidth: '800px' }}>
      <h2 style={{ color: '#38bdf8', marginBottom: '1rem' }}>📝 Campaign Brief</h2>
      <textarea
        value={brief}
        onChange={e => setBrief(e.target.value)}
        rows={6}
        style={{
          width: '100%',
          background: '#334155',
          color: '#f1f5f9',
          border: '1px solid #38bdf8',
          borderRadius: '8px',
          padding: '1rem',
          fontSize: '14px',
          resize: 'vertical',
          boxSizing: 'border-box',
        }}
      />
      <button
        onClick={handleSubmit}
        disabled={loading || !brief.trim()}
        style={{
          marginTop: '1rem',
          background: loading ? '#475569' : '#38bdf8',
          color: '#0f172a',
          border: 'none',
          borderRadius: '8px',
          padding: '0.75rem 2rem',
          fontSize: '16px',
          fontWeight: 'bold',
          cursor: loading ? 'not-allowed' : 'pointer',
        }}
      >
        {loading ? '⏳ AI Agents Working...' : '🚀 Launch Campaign Planning'}
      </button>
    </div>
  )
}
