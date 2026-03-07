export default function ApprovalPanel({
  state,
  onApprove,
}: {
  state: any
  onApprove: (d: 'approved' | 'rejected') => void
}) {
  if (!state?.content_a && !state?.content_b) {
    return (
      <div style={{ background: '#1e293b', borderRadius: '12px', padding: '2rem', maxWidth: '900px' }}>
        <p style={{ color: '#94a3b8' }}>Waiting for content generation...</p>
      </div>
    )
  }

  return (
    <div style={{ background: '#1e293b', borderRadius: '12px', padding: '2rem', maxWidth: '900px' }}>
      <h2 style={{ color: '#38bdf8' }}>👤 Human Approval Required</h2>

      {state.strategy_text && (
        <div style={{ marginTop: '1rem', background: '#334155', borderRadius: '8px', padding: '1rem' }}>
          <h3 style={{ color: '#38bdf8' }}>🎯 Campaign Strategy</h3>
          <p style={{ fontSize: '13px', color: '#cbd5e1' }}>{state.strategy_text}</p>
        </div>
      )}

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginTop: '1rem' }}>
        {(['content_a', 'content_b'] as const).map((key, i) => (
          <div key={key} style={{ background: '#334155', borderRadius: '8px', padding: '1rem' }}>
            <h3 style={{ color: '#38bdf8' }}>Variant {i === 0 ? 'A (Professional)' : 'B (Friendly)'}</h3>
            <p>
              <strong>Subject:</strong> {state[key]?.subject || 'N/A'}
            </p>
            <p style={{ fontSize: '13px', color: '#cbd5e1', whiteSpace: 'pre-wrap' }}>
              {state[key]?.body || 'No content generated'}
            </p>
          </div>
        ))}
      </div>

      <div style={{ marginTop: '1rem', background: '#334155', borderRadius: '8px', padding: '1rem' }}>
        <h3 style={{ color: '#38bdf8' }}>📊 Segments</h3>
        <p>Segment A: {state.segments?.segment_a?.length ?? 0} customers</p>
        <p>Segment B: {state.segments?.segment_b?.length ?? 0} customers</p>
        <p>Strategy: {state.segments?.strategy ?? 'N/A'}</p>
      </div>

      {state.parsed_brief && (
        <div style={{ marginTop: '1rem', background: '#334155', borderRadius: '8px', padding: '1rem' }}>
          <h3 style={{ color: '#38bdf8' }}>📋 Parsed Brief</h3>
          <p>Product: {state.parsed_brief.product_name ?? 'N/A'}</p>
          <p>USP: {state.parsed_brief.usp ?? 'N/A'}</p>
          <p>Tone: {state.parsed_brief.tone ?? 'N/A'}</p>
          {state.parsed_brief.special_offers && <p>Special Offers: {state.parsed_brief.special_offers}</p>}
        </div>
      )}

      <div style={{ marginTop: '1.5rem', display: 'flex', gap: '1rem' }}>
        <button
          onClick={() => onApprove('approved')}
          style={{
            background: '#22c55e',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            padding: '0.75rem 2rem',
            fontSize: '16px',
            fontWeight: 'bold',
            cursor: 'pointer',
          }}
        >
          ✅ Approve & Schedule
        </button>
        <button
          onClick={() => onApprove('rejected')}
          style={{
            background: '#ef4444',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            padding: '0.75rem 2rem',
            fontSize: '16px',
            fontWeight: 'bold',
            cursor: 'pointer',
          }}
        >
          ❌ Reject & Regenerate
        </button>
      </div>
    </div>
  )
}
