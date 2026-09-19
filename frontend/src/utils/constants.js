/**
 * TriageAI Constants
 * ESI levels, colors, and configuration
 */

export const ESI_LEVELS = {
  1: {
    label: 'Resuscitation',
    color: '#ff1744',
    bgColor: 'rgba(255, 23, 68, 0.15)',
    borderColor: 'rgba(255, 23, 68, 0.4)',
    description: 'Immediate life-threatening condition',
    maxWait: 0,
    icon: '🔴',
  },
  2: {
    label: 'Emergent',
    color: '#ff6d00',
    bgColor: 'rgba(255, 109, 0, 0.15)',
    borderColor: 'rgba(255, 109, 0, 0.4)',
    description: 'High risk of deterioration',
    maxWait: 10,
    icon: '🟠',
  },
  3: {
    label: 'Urgent',
    color: '#ffd600',
    bgColor: 'rgba(255, 214, 0, 0.15)',
    borderColor: 'rgba(255, 214, 0, 0.4)',
    description: 'Stable, needs multiple resources',
    maxWait: 30,
    icon: '🟡',
  },
  4: {
    label: 'Less Urgent',
    color: '#00e676',
    bgColor: 'rgba(0, 230, 118, 0.15)',
    borderColor: 'rgba(0, 230, 118, 0.4)',
    description: 'Needs one resource',
    maxWait: 60,
    icon: '🟢',
  },
  5: {
    label: 'Non-Urgent',
    color: '#448aff',
    bgColor: 'rgba(68, 138, 255, 0.15)',
    borderColor: 'rgba(68, 138, 255, 0.4)',
    description: 'No resources needed',
    maxWait: 120,
    icon: '🔵',
  },
};

export const PATIENT_STATUSES = ['Waiting', 'In Treatment', 'Discharged', 'Admitted'];

export const STATUS_COLORS = {
  'Waiting': '#ffd600',
  'In Treatment': '#448aff',
  'Discharged': '#00e676',
  'Admitted': '#ab47bc',
};

export const ARRIVAL_MODES = ['Walk-in', 'Ambulance', 'Helicopter', 'Police', 'Transfer'];
export const GENDERS = ['Male', 'Female', 'Other'];

// API Base URL - change this for production
export const API_BASE_URL = '/api';
