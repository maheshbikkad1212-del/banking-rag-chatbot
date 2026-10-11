import React from 'react';
import { Target, Search, CheckCircle, AlertTriangle, ShieldCheck, Zap, Layers, Activity } from 'lucide-react';

export default function PipelineVisualizer({ lastResponse, cacheStats, onClearCache }) {
  if (!lastResponse) {
    return (
      <div className="glass-panel" style={{ padding: '24px', textAlign: 'center', color: '#9CA3AF' }}>
        <Activity size={32} color="#3B82F6" style={{ margin: '0 auto 12px auto', display: 'block' }} />
        <h3 style={{ fontSize: '0.95rem', color: '#E5E7EB', marginBottom: '4px' }}>RAG Architecture Diagnostics</h3>
        <p style={{ fontSize: '0.8rem' }}>Ask a banking policy question to inspect live retrieval, CRAG score & numerical verification pipeline.</p>
      </div>
    );
  }

  const { intent, intent_confidence, crag_evaluation, numerical_validation, cache_hit_level, citations } = lastResponse;

  return (
    <div className="glass-panel" style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '20px' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <h3 style={{ fontSize: '1rem', fontWeight: 700, color: '#F9FAFB', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Zap size={18} color="#3B82F6" />
          RAG Pipeline Execution Traces
        </h3>
        {cache_hit_level ? (
          <span className="glass-pill" style={{ background: 'rgba(59, 130, 246, 0.2)', color: '#60A5FA', borderColor: '#3B82F6' }}>
            ⚡ {cache_hit_level}
          </span>
        ) : (
          <span className="glass-pill" style={{ color: '#34D399' }}>Live Real-Time Run</span>
        )}
      </div>

      {/* Pipeline Steps Grid */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
        
        {/* Step 1: Intent Detection */}
        <div style={{ padding: '12px 16px', background: 'rgba(30, 41, 59, 0.5)', borderRadius: '12px', borderLeft: '3px solid #3B82F6' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.8rem' }}>
            <span style={{ color: '#9CA3AF', display: 'flex', alignItems: 'center', gap: '6px' }}>
              <Target size={14} color="#3B82F6" /> Step 1: Intent Detection
            </span>
            <span style={{ color: '#60A5FA', fontWeight: 600 }}>{(intent_confidence * 100).toFixed(0)}% Confidence</span>
          </div>
          <p style={{ fontSize: '0.88rem', color: '#F3F4F6', fontWeight: 600, marginTop: '4px' }}>
            {intent}
          </p>
        </div>

        {/* Step 2: Hybrid Retrieval */}
        <div style={{ padding: '12px 16px', background: 'rgba(30, 41, 59, 0.5)', borderRadius: '12px', borderLeft: '3px solid #8B5CF6' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.8rem' }}>
            <span style={{ color: '#9CA3AF', display: 'flex', alignItems: 'center', gap: '6px' }}>
              <Search size={14} color="#8B5CF6" /> Step 2: Hybrid Search & MMR
            </span>
            <span style={{ color: '#C084FC', fontWeight: 600 }}>{citations ? citations.length : 0} Chunks Selected</span>
          </div>
          <p style={{ fontSize: '0.82rem', color: '#D1D5DB', marginTop: '4px' }}>
            Dense vector cosine similarity + Sparse BM25 exact keyword match with MMR diversification.
          </p>
        </div>

        {/* Step 3: Corrective RAG (CRAG) */}
        <div style={{
          padding: '12px 16px',
          background: crag_evaluation?.evaluation_status === 'CORRECT' ? 'rgba(16, 185, 129, 0.1)' : 'rgba(245, 158, 11, 0.1)',
          borderRadius: '12px',
          borderLeft: `3px solid ${crag_evaluation?.evaluation_status === 'CORRECT' ? '#10B981' : '#F59E0B'}`
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.8rem' }}>
            <span style={{ color: '#9CA3AF', display: 'flex', alignItems: 'center', gap: '6px' }}>
              <Layers size={14} color={crag_evaluation?.evaluation_status === 'CORRECT' ? '#10B981' : '#F59E0B'} /> Step 3: Corrective RAG (CRAG)
            </span>
            <span className={crag_evaluation?.evaluation_status === 'CORRECT' ? 'glass-pill badge-correct' : 'glass-pill badge-ambiguous'}>
              {crag_evaluation?.evaluation_status} ({(crag_evaluation?.confidence_score * 100).toFixed(0)}%)
            </span>
          </div>
          <p style={{ fontSize: '0.82rem', color: '#D1D5DB', marginTop: '4px' }}>
            {crag_evaluation?.recommendation}
          </p>
        </div>

        {/* Step 4: Post-Generation Numerical Validation */}
        <div style={{ padding: '12px 16px', background: 'rgba(59, 130, 246, 0.1)', borderRadius: '12px', borderLeft: '3px solid #3B82F6' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.8rem' }}>
            <span style={{ color: '#9CA3AF', display: 'flex', alignItems: 'center', gap: '6px' }}>
              <ShieldCheck size={14} color="#3B82F6" /> Step 4: Numerical Validation Guardrail
            </span>
            <span className="glass-pill badge-pass">
              {numerical_validation?.passed ? 'PASS: Verified' : 'Checked'}
            </span>
          </div>
          <p style={{ fontSize: '0.82rem', color: '#D1D5DB', marginTop: '4px' }}>
            {numerical_validation?.status}
          </p>
        </div>

      </div>

      {/* Multi-Level Cache Metrics */}
      <div style={{ paddingTop: '12px', borderTop: '1px solid var(--border-glass)' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
          <span style={{ fontSize: '0.8rem', color: '#9CA3AF' }}>Multi-Level Cache Performance</span>
          <button onClick={onClearCache} style={{ background: 'none', border: 'none', color: '#EF4444', fontSize: '0.75rem', cursor: 'pointer', fontWeight: 600 }}>
            Clear Caches
          </button>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '8px', textAlign: 'center', fontSize: '0.75rem' }}>
          <div style={{ padding: '8px', background: 'rgba(15, 23, 42, 0.6)', borderRadius: '8px' }}>
            <div style={{ color: '#9CA3AF' }}>L1 Query</div>
            <strong style={{ color: '#60A5FA' }}>{cacheStats?.l1_hits || 0} hits</strong>
          </div>
          <div style={{ padding: '8px', background: 'rgba(15, 23, 42, 0.6)', borderRadius: '8px' }}>
            <div style={{ color: '#9CA3AF' }}>L2 Retrieval</div>
            <strong style={{ color: '#C084FC' }}>{cacheStats?.l2_hits || 0} hits</strong>
          </div>
          <div style={{ padding: '8px', background: 'rgba(15, 23, 42, 0.6)', borderRadius: '8px' }}>
            <div style={{ color: '#9CA3AF' }}>L3 Response</div>
            <strong style={{ color: '#34D399' }}>{cacheStats?.l3_hits || 0} hits</strong>
          </div>
        </div>
      </div>
    </div>
  );
}
