import React from 'react';
import { X, FileText, CheckCircle2, Award, Calendar, Layers } from 'lucide-react';

export default function CitationModal({ citation, onClose }) {
  if (!citation) return null;

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      backgroundColor: 'rgba(0, 0, 0, 0.75)',
      backdropFilter: 'blur(8px)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 100,
      padding: '24px'
    }}>
      <div className="glass-panel" style={{
        maxWidth: '680px',
        width: '100%',
        padding: '28px',
        background: '#0F172A',
        position: 'relative',
        animation: 'fadeIn 0.2s ease-out'
      }}>
        <button
          onClick={onClose}
          style={{
            position: 'absolute',
            top: '20px',
            right: '20px',
            background: 'transparent',
            border: 'none',
            color: '#9CA3AF',
            cursor: 'pointer'
          }}
        >
          <X size={22} />
        </button>

        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
          <div style={{ padding: '10px', background: 'rgba(59, 130, 246, 0.2)', borderRadius: '10px' }}>
            <FileText size={24} color="#60A5FA" />
          </div>
          <div>
            <h3 style={{ fontSize: '1.15rem', color: '#F9FAFB', fontWeight: 700 }}>
              {citation.doc_name}
            </h3>
            <p style={{ fontSize: '0.8rem', color: '#9CA3AF' }}>
              Official Source Verification & Chunk Inspection
            </p>
          </div>
        </div>

        {/* Metadata Grid */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(3, 1fr)',
          gap: '12px',
          padding: '16px',
          background: 'rgba(30, 41, 59, 0.6)',
          borderRadius: '12px',
          marginBottom: '20px',
          fontSize: '0.85rem'
        }}>
          <div>
            <span style={{ color: '#9CA3AF', display: 'block', fontSize: '0.75rem' }}>Authority</span>
            <strong style={{ color: '#60A5FA' }}>{citation.authority}</strong>
          </div>
          <div>
            <span style={{ color: '#9CA3AF', display: 'block', fontSize: '0.75rem' }}>Effective Date</span>
            <strong style={{ color: '#34D399' }}>{citation.effective_date}</strong>
          </div>
          <div>
            <span style={{ color: '#9CA3AF', display: 'block', fontSize: '0.75rem' }}>Page & Version</span>
            <strong style={{ color: '#FBBF24' }}>Page {citation.page_number} (v{citation.version})</strong>
          </div>
        </div>

        <h4 style={{ fontSize: '0.9rem', color: '#E5E7EB', marginBottom: '8px' }}>
          Retrieved Excerpt Text:
        </h4>
        <div style={{
          padding: '16px',
          background: 'rgba(15, 23, 42, 0.9)',
          border: '1px solid rgba(255, 255, 255, 0.08)',
          borderRadius: '10px',
          color: '#D1D5DB',
          fontFamily: 'var(--font-sans)',
          fontSize: '0.9rem',
          lineHeight: '1.6',
          maxHeight: '260px',
          overflowY: 'auto'
        }}>
          {citation.snippet}
        </div>

        <div style={{ marginTop: '20px', display: 'flex', justifyContent: 'flex-end' }}>
          <button className="glass-button" onClick={onClose}>
            Close Inspector
          </button>
        </div>
      </div>
    </div>
  );
}
