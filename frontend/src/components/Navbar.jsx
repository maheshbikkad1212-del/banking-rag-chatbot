import React from 'react';
import { ShieldCheck, Database, RefreshCw, Upload, Cpu, Zap } from 'lucide-react';

export default function Navbar({ health, onOpenDocuments, onClearCache, onSeed }) {
  return (
    <nav style={{
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '16px 32px',
      background: 'rgba(15, 23, 42, 0.85)',
      backdropFilter: 'blur(16px)',
      borderBottom: '1px solid rgba(255, 255, 255, 0.08)',
      position: 'sticky',
      top: 0,
      zIndex: 50
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
        <div style={{
          width: '42px',
          height: '42px',
          borderRadius: '12px',
          background: 'linear-gradient(135deg, #3B82F6, #10B981)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          boxShadow: '0 0 20px rgba(59, 130, 246, 0.4)'
        }}>
          <ShieldCheck size={26} color="#FFFFFF" />
        </div>
        <div>
          <h1 style={{ fontSize: '1.25rem', fontWeight: 800, letterSpacing: '-0.02em', background: 'linear-gradient(to right, #FFFFFF, #93C5FD)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
            BankSmart RAG
          </h1>
          <p style={{ fontSize: '0.75rem', color: '#9CA3AF', fontWeight: 500 }}>
            Smart Document Understanding System &bull; Zero Hallucination Engine
          </p>
        </div>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
        {/* Status Indicators */}
        <div className="glass-pill" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span className="glowing-dot"></span>
          <span style={{ fontSize: '0.8rem', color: '#E5E7EB' }}>
            {health ? `${health.vector_store_chunks} Chunks Vectorized` : 'Connecting...'}
          </span>
        </div>

        <div className="glass-pill" style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#60A5FA' }}>
          <Cpu size={14} />
          <span style={{ fontSize: '0.8rem' }}>all-MiniLM-L6-v2 + BM25</span>
        </div>

        {/* Action Buttons */}
        <button className="glass-button" onClick={onOpenDocuments} title="Manage Indexed Documents">
          <Upload size={16} />
          <span>Documents</span>
        </button>

        <button className="glass-button" onClick={onSeed} style={{ background: 'rgba(16, 185, 129, 0.15)', borderColor: 'rgba(16, 185, 129, 0.4)' }} title="Re-seed Default Policies">
          <RefreshCw size={16} color="#34D399" />
          <span style={{ color: '#34D399' }}>Re-Seed</span>
        </button>
      </div>
    </nav>
  );
}
