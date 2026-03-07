export default function MetricsDashboard({ state }: { state: any }) {
  const campaigns = state.metrics?.campaigns || []
  const score = state.metrics?.score || 0

  return (
    <div style={{ background: '#1e293b', borderRadius: '12px', padding: '2rem', maxWidth: '900px' }}>
      <h2 style={{ color: '#38bdf8' }}>📈 Campaign Performance</h2>

      <div style={{ background: '#334155', borderRadius: '8px', padding: '1rem', marginTop: '1rem' }}>
        <h3>
          Weighted Score:{' '}
          <span style={{ color: '#22c55e' }}>{(score * 100).toFixed(1)}%</span>
        </h3>
        <p style={{ fontSize: '12px', color: '#94a3b8' }}>(Click Rate × 70% + Open Rate × 30%)</p>
      </div>

      {campaigns.map((c: any, i: number) => (
        <div key={i} style={{ background: '#334155', borderRadius: '8px', padding: '1rem', marginTop: '1rem' }}>
          <h3>Campaign {i + 1}: {c.campaign_id || `Variant ${i === 0 ? 'A' : 'B'}`}</h3>
          <p>
            📬 Open Rate:{' '}
            <strong style={{ color: '#38bdf8' }}>{((c.open_rate || 0) * 100).toFixed(1)}%</strong>
          </p>
          <p>
            🖱️ Click Rate:{' '}
            <strong style={{ color: '#22c55e' }}>{((c.click_rate || 0) * 100).toFixed(1)}%</strong>
          </p>
        </div>
      ))}

      <div style={{ marginTop: '1.5rem', display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
        {state.content_a && (
          <div style={{ background: '#334155', borderRadius: '8px', padding: '1rem', flex: 1, minWidth: '300px' }}>
            <h4 style={{ color: '#38bdf8' }}>Final Variant A</h4>
            <p><strong>{state.content_a.subject}</strong></p>
            <p style={{ fontSize: '12px', color: '#cbd5e1' }}>{state.content_a.body}</p>
          </div>
        )}
        {state.content_b && (
          <div style={{ background: '#334155', borderRadius: '8px', padding: '1rem', flex: 1, minWidth: '300px' }}>
            <h4 style={{ color: '#38bdf8' }}>Final Variant B</h4>
            <p><strong>{state.content_b.subject}</strong></p>
            <p style={{ fontSize: '12px', color: '#cbd5e1' }}>{state.content_b.body}</p>
          </div>
        )}
      </div>

      <p style={{ marginTop: '1rem', color: '#94a3b8', fontSize: '13px' }}>
        Iteration: {state.iteration}/3 | Status: {state.status}
      </p>
    </div>
  )
}
