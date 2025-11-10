import React from 'react';

function DetectionFeed({ detections, liveData }) {
  const getObjectCounts = (detectionList) => {
    const counts = {};
    detectionList.forEach(det => {
      counts[det.class_name] = (counts[det.class_name] || 0) + 1;
    });
    return counts;
  };

  return (
    <div className="card">
      <h2>🔍 Recent Detections</h2>

      {liveData && liveData.latest_detection && (
        <div className="detection-item" style={{ borderLeftColor: '#10b981' }}>
          <div className="detection-header">
            <span><strong>LIVE: {liveData.latest_detection.stream_id}</strong></span>
            <span>Frame {liveData.latest_detection.frame_number}</span>
          </div>
          <div className="detection-objects">
            {Object.entries(getObjectCounts(liveData.latest_detection.detections)).map(([obj, count]) => (
              <span key={obj} className="object-badge">
                {obj}: {count}
              </span>
            ))}
          </div>
        </div>
      )}

      <h3 style={{ marginTop: '1.5rem', marginBottom: '1rem', color: '#cbd5e1' }}>
        Historical
      </h3>

      {detections && detections.length > 0 ? (
        detections.slice(0, 8).map((detection) => (
          <div key={detection.id} className="detection-item">
            <div className="detection-header">
              <span>{detection.stream_id}</span>
              <span>Frame {detection.frame_number}</span>
            </div>
            <div className="detection-objects">
              {detection.detections.length > 0 ? (
                Object.entries(getObjectCounts(detection.detections)).map(([obj, count]) => (
                  <span key={obj} className="object-badge">
                    {obj}: {count}
                  </span>
                ))
              ) : (
                <span style={{ color: '#64748b', fontSize: '0.875rem' }}>No objects detected</span>
              )}
            </div>
          </div>
        ))
      ) : (
        <div className="no-data">No detections yet</div>
      )}
    </div>
  );
}

export default DetectionFeed;