import React from 'react';

function Dashboard({ stats, liveData }) {
  return (
    <div className="card">
      <h2>📊 System Dashboard</h2>

      {stats ? (
        <div className="stat-grid">
          <div className="stat-card">
            <div className="stat-label">Total Frames</div>
            <div className="stat-value">{stats.total_frames_processed.toLocaleString()}</div>
          </div>

          <div className="stat-card">
            <div className="stat-label">Total Detections</div>
            <div className="stat-value">{stats.total_detections.toLocaleString()}</div>
          </div>

          <div className="stat-card">
            <div className="stat-label">Active Streams</div>
            <div className="stat-value">{stats.active_streams}</div>
          </div>

          <div className="stat-card">
            <div className="stat-label">Frame Queue</div>
            <div className="stat-value">{liveData ? liveData.frame_queue_size : stats.frame_queue_size}</div>
          </div>

          <div className="stat-card">
            <div className="stat-label">Results Queue</div>
            <div className="stat-value">{liveData ? liveData.results_queue_size : stats.results_queue_size}</div>
          </div>

          <div className="stat-card">
            <div className="stat-label">Avg Detections/Frame</div>
            <div className="stat-value">
              {stats.total_frames_processed > 0
                ? (stats.total_detections / stats.total_frames_processed).toFixed(1)
                : '0.0'
              }
            </div>
          </div>
        </div>
      ) : (
        <div className="no-data">Loading system stats...</div>
      )}
    </div>
  );
}

export default Dashboard;