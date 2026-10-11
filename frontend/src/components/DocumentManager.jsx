import React, { useState } from 'react';
import { X, UploadCloud, FileText, CheckCircle2, AlertCircle, BookOpen } from 'lucide-react';
import { uploadDocumentFile } from '../api/client';

export default function DocumentManager({ documents, onClose, onRefreshDocs }) {
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState(null);

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setUploading(true);
    setMessage(null);

    try {
      const res = await uploadDocumentFile(file);
      setMessage({ type: 'success', text: `Successfully ingested "${res.filename}" into ${res.chunks_indexed} vectorized chunks!` });
      onRefreshDocs();
    } catch (err) {
      setMessage({ type: 'error', text: err.message || 'Upload failed' });
    } finally {
      setUploading(false);
    }
  };

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
        maxWidth: '720px',
        width: '100%',
        padding: '32px',
        background: '#0F172A',
        position: 'relative'
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

        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '24px' }}>
          <div style={{ padding: '10px', background: 'rgba(59, 130, 246, 0.2)', borderRadius: '12px' }}>
            <BookOpen size={26} color="#60A5FA" />
          </div>
          <div>
            <h2 style={{ fontSize: '1.3rem', color: '#F9FAFB', fontWeight: 800 }}>
              Authorized Document Knowledge Base
            </h2>
            <p style={{ fontSize: '0.85rem', color: '#9CA3AF' }}>
              Upload new regulatory manuals, loan guidelines, or interest rate circulars (PDF, DOCX, TXT).
            </p>
          </div>
        </div>

        {/* Upload Box */}
        <div style={{
          border: '2px dashed rgba(59, 130, 246, 0.4)',
          borderRadius: '16px',
          padding: '28px',
          textAlign: 'center',
          background: 'rgba(30, 41, 59, 0.3)',
          marginBottom: '24px',
          transition: 'all 0.2s ease'
        }}>
          <UploadCloud size={38} color="#3B82F6" style={{ margin: '0 auto 12px auto' }} />
          <p style={{ fontSize: '0.95rem', color: '#E5E7EB', fontWeight: 600, marginBottom: '4px' }}>
            {uploading ? 'Processing Ingestion Pipeline & Embeddings...' : 'Click to select or drag document file'}
          </p>
          <p style={{ fontSize: '0.8rem', color: '#9CA3AF', marginBottom: '16px' }}>
            Supports PDF (PyMuPDF + OCR), Word (.docx), and Plain Text (.txt)
          </p>
          <label className="glass-button" style={{ display: 'inline-flex', cursor: 'pointer' }}>
            <input type="file" onChange={handleFileUpload} accept=".pdf,.docx,.doc,.txt" style={{ display: 'none' }} disabled={uploading} />
            Select Document
          </label>
        </div>

        {message && (
          <div style={{
            padding: '12px 16px',
            borderRadius: '10px',
            marginBottom: '20px',
            fontSize: '0.88rem',
            background: message.type === 'success' ? 'rgba(16, 185, 129, 0.15)' : 'rgba(239, 68, 68, 0.15)',
            border: `1px solid ${message.type === 'success' ? 'rgba(16, 185, 129, 0.4)' : 'rgba(239, 68, 68, 0.4)'}`,
            color: message.type === 'success' ? '#34D399' : '#F87171'
          }}>
            {message.text}
          </div>
        )}

        <h3 style={{ fontSize: '1rem', color: '#F3F4F6', marginBottom: '12px' }}>
          Currently Indexed Policy Library ({documents?.length || 0} Documents)
        </h3>

        <div style={{ maxHeight: '220px', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '10px' }}>
          {documents && documents.map((doc, idx) => (
            <div key={idx} style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              padding: '12px 16px',
              background: 'rgba(30, 41, 59, 0.6)',
              borderRadius: '12px',
              border: '1px solid var(--border-glass)'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                <FileText size={20} color="#60A5FA" />
                <div>
                  <h4 style={{ fontSize: '0.9rem', color: '#F9FAFB', fontWeight: 600 }}>{doc.doc_name}</h4>
                  <p style={{ fontSize: '0.75rem', color: '#9CA3AF' }}>
                    Authority: {doc.authority} &bull; Effective: {doc.effective_date} &bull; v{doc.version}
                  </p>
                </div>
              </div>
              <span className="glass-pill" style={{ fontSize: '0.75rem', color: '#34D399' }}>
                {doc.chunk_count} Chunks
              </span>
            </div>
          ))}
        </div>

        <div style={{ marginTop: '24px', display: 'flex', justifyContent: 'flex-end' }}>
          <button className="glass-button" onClick={onClose}>
            Done
          </button>
        </div>
      </div>
    </div>
  );
}
