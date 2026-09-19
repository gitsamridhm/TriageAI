import { useState } from 'react';
import { ESI_LEVELS } from '../utils/constants';
import { updatePatientStatus, deletePatient } from '../services/api';

export default function PriorityQueue({ patients, onSelectPatient, onPatientUpdated, addToast }) {
  const [filter, setFilter] = useState('all');
  const [statusFilter, setStatusFilter] = useState('all');

  const getWaitTime = (createdAt) => {
    const diff = Date.now() - new Date(createdAt).getTime();
    const mins = Math.floor(diff / 60000);
    if (mins < 60) return `${mins}m`;
    return `${Math.floor(mins / 60)}h ${mins % 60}m`;
  };

  const filteredPatients = patients.filter(p => {
    if (filter !== 'all' && p.esi_level !== parseInt(filter)) return false;
    if (statusFilter !== 'all' && p.status !== statusFilter) return false;
    return true;
  });

  const handleStatusChange = async (e, patientId) => {
    e.stopPropagation();
    const newStatus = e.target.value;
    try {
      await updatePatientStatus(patientId, newStatus);
      addToast(`Patient status updated to "${newStatus}"`, 'success');
      onPatientUpdated();
    } catch (error) {
      addToast('Failed to update status', 'error');
    }
  };

  const handleDelete = async (e, patient) => {
    e.stopPropagation();
    if (!window.confirm(`Delete patient "${patient.name}"? This cannot be undone.`)) return;
    try {
      await deletePatient(patient.id);
      addToast(`Patient "${patient.name}" deleted`, 'success');
      onPatientUpdated();
    } catch (error) {
      addToast('Failed to delete patient', 'error');
    }
  };

  return (
    <div>
      <div className="section-header">
        <div>
          <h1 className="section-title">Priority Queue</h1>
          <p className="section-subtitle">
            {filteredPatients.length} patient{filteredPatients.length !== 1 ? 's' : ''} — sorted by severity
          </p>
        </div>
      </div>

      {/* Filters */}
      <div style={{ display: 'flex', gap: '12px', marginBottom: '20px', flexWrap: 'wrap', alignItems: 'center' }}>
        <div style={{ fontSize: '12px', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '1px' }}>
          ESI Level:
        </div>
        <div className="queue-filters">
          <button
            className={`queue-filter-btn ${filter === 'all' ? 'active' : ''}`}
            onClick={() => setFilter('all')}
          >
            All
          </button>
          {[1, 2, 3, 4, 5].map(level => (
            <button
              key={level}
              className={`queue-filter-btn ${filter === String(level) ? 'active' : ''}`}
              onClick={() => setFilter(String(level))}
              style={filter === String(level) ? {
                background: ESI_LEVELS[level].bgColor,
                borderColor: ESI_LEVELS[level].borderColor,
                color: ESI_LEVELS[level].color,
              } : {}}
            >
              {ESI_LEVELS[level].icon} ESI {level}
            </button>
          ))}
        </div>
        <div style={{ fontSize: '12px', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '1px', marginLeft: '12px' }}>
          Status:
        </div>
        <div className="queue-filters">
          {['all', 'Waiting', 'In Treatment', 'Discharged'].map(s => (
            <button
              key={s}
              className={`queue-filter-btn ${statusFilter === s ? 'active' : ''}`}
              onClick={() => setStatusFilter(s)}
            >
              {s === 'all' ? 'All' : s}
            </button>
          ))}
        </div>
      </div>

      {/* Patient List */}
      <div className="queue-container">
        {filteredPatients.length === 0 ? (
          <div className="empty-state">
            <div className="empty-state-icon">🔍</div>
            <div className="empty-state-text">No patients match the current filters</div>
          </div>
        ) : (
          filteredPatients.map((patient, index) => (
            <div
              key={patient.id}
              className="patient-card"
              onClick={() => onSelectPatient(patient)}
              style={{ animationDelay: `${index * 0.05}s` }}
            >
              {/* ESI Level */}
              <div
                className="patient-card-esi"
                style={{
                  background: patient.esi_level ? ESI_LEVELS[patient.esi_level]?.bgColor : 'var(--bg-input)',
                  color: patient.esi_level ? ESI_LEVELS[patient.esi_level]?.color : 'var(--text-muted)',
                  border: `1px solid ${patient.esi_level ? ESI_LEVELS[patient.esi_level]?.borderColor : 'var(--border-color)'}`,
                }}
              >
                {patient.esi_level || '?'}
              </div>

              {/* Patient Info */}
              <div className="patient-card-info">
                <div className="patient-card-name">{patient.name}</div>
                <div className="patient-card-complaint">{patient.chief_complaint}</div>
                <div className="patient-card-meta">
                  <span>Age {patient.age}</span>
                  <span>•</span>
                  <span>{patient.gender}</span>
                  <span>•</span>
                  <span>{patient.arrival_mode}</span>
                  {patient.esi_level && (
                    <>
                      <span>•</span>
                      <span style={{ color: ESI_LEVELS[patient.esi_level]?.color }}>
                        {ESI_LEVELS[patient.esi_level]?.label}
                      </span>
                    </>
                  )}
                </div>
              </div>

              {/* Wait Time */}
              <div className="patient-card-wait">
                <div
                  className="patient-card-wait-time"
                  style={{ color: patient.esi_level ? ESI_LEVELS[patient.esi_level]?.color : 'var(--text-secondary)' }}
                >
                  {getWaitTime(patient.created_at)}
                </div>
                <div className="patient-card-wait-label">wait time</div>
              </div>

              {/* Status Dropdown + Delete Button */}
              <div className="patient-card-actions" onClick={e => e.stopPropagation()} style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <select
                  className="form-select"
                  value={patient.status}
                  onChange={(e) => handleStatusChange(e, patient.id)}
                  style={{
                    fontSize: '11px',
                    padding: '4px 8px',
                    minWidth: '120px',
                  }}
                >
                  <option value="Waiting">⏳ Waiting</option>
                  <option value="In Treatment">💉 In Treatment</option>
                  <option value="Discharged">✅ Discharged</option>
                  <option value="Admitted">🏥 Admitted</option>
                </select>
                <button
                  onClick={(e) => handleDelete(e, patient)}
                  title="Delete patient"
                  style={{
                    background: 'rgba(239,68,68,0.15)',
                    border: '1px solid rgba(239,68,68,0.4)',
                    borderRadius: '6px',
                    color: '#ef4444',
                    cursor: 'pointer',
                    fontSize: '14px',
                    fontWeight: 700,
                    lineHeight: 1,
                    padding: '4px 8px',
                    flexShrink: 0,
                  }}
                >
                  ✕
                </button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
