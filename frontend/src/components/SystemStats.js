import React from 'react';

function SystemStats({ stats, streams, liveData }) {
  return (
    <div className="card">
      <h2>🖥️ System Status</h2>

      {liveData && (
        <div className="live-indicator" style={{ marginBottom: '1rem' }}>
          <span className="status-dot connected"></span>
          Live Updates Active
        </div>
      )}

      <h3 style={{ marginTop: '1.5rem', marginBottom: '1rem', color: '#cbd5e1' }}>
        Active Streams
      </h3>

      {streams && streams.length > 0 ? (
        streams.map((stream) => (
          <div key={stream.id} className="detection-item">
            <div className="detection-header">
              <span><strong>{stream.stream_id}</strong></span>
              <span className="object-badge">
                {stream.status}
              </span>
            </div>
            <div style={{ fontSize: '0.875rem', color: '#94a3b8', marginTop: '0.5rem' }}>
              <div>Frames: {stream.frames_processed.toLocaleString()}</div>
              <div>Detections: {stream.total_detections.toLocaleString()}</div>
              <div>Source: {stream.video_source}</div>
            </div>
          </div>
        ))
      ) : (
        <div className="no-data">No active streams</div>
      )}

      {stats && (
        <>
          <h3 style={{ marginTop: '1.5rem', marginBottom: '1rem', color: '#cbd5e1' }}>
            Queue Health
          </h3>
          <div className="stat-grid">
            <div className="stat-card">
              <div className="stat-label">Frame Queue</div>
              <div className="stat-value" style={{ fontSize: '1.5rem' }}>
                {liveData ? liveData.frame_queue_size : stats.frame_queue_size}
              </div>
              <div style={{ fontSize: '0.75rem', color: '#64748b', marginTop: '0.5rem' }}>
                {(liveData?.frame_queue_size || stats.frame_queue_size) === 0
                  ? '✅ Healthy'
                  : '⚠️ Backlog'
                }
              </div>
            </div>

            <div className="stat-card">
              <div className="stat-label">Results Queue</div>
              <div className="stat-value" style={{ fontSize: '1.5rem' }}>
                {liveData ? liveData.results_queue_size : stats.results_queue_size}
              </div>
              <div style={{ fontSize: '0.75rem', color: '#64748b', marginTop: '0.5rem' }}>
                {(liveData?.results_queue_size || stats.results_queue_size) === 0
                  ? '✅ Healthy'
                  : '⚠️ Backlog'
                }
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
}

export default SystemStats;