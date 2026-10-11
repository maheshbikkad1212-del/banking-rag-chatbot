import React, { useState, useEffect } from "react";

import Navbar from "./components/Navbar";
import ChatContainer from "./components/ChatContainer";
import CitationModal from "./components/CitationModal";
import PipelineVisualizer from "./components/PipelineVisualizer";
import DocumentManager from "./components/DocumentManager";

import {
  sendChatMessage,
  fetchDocumentList,
  fetchCacheStats,
  clearSystemCache,
  triggerReSeed,
  fetchHealth,
} from "./api/client";

export default function App() {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);

  const [lastResponse, setLastResponse] = useState(null);
  const [selectedCitation, setSelectedCitation] = useState(null);
  const [showDocManager, setShowDocManager] = useState(false);

  const [health, setHealth] = useState(null);
  const [documents, setDocuments] = useState([]);

  const [cacheStats, setCacheStats] = useState({
    l1_hits: 0,
    l2_hits: 0,
    l3_hits: 0,
  });

  // -----------------------------------------
  // Load backend information
  // -----------------------------------------
  const refreshSystemData = async () => {
    try {
      const h = await fetchHealth();
      setHealth(h);

      const docs = await fetchDocumentList();
      setDocuments(docs);

      const stats = await fetchCacheStats();
      setCacheStats(stats);
    } catch (error) {
      console.warn("Backend not available:", error.message);
    }
  };

  // -----------------------------------------
  // Initial backend check
  // -----------------------------------------
  useEffect(() => {
    refreshSystemData();

    const interval = setInterval(() => {
      refreshSystemData();
    }, 10000);

    return () => clearInterval(interval);
  }, []);

  // -----------------------------------------
  // SEND QUERY TO FASTAPI
  // -----------------------------------------
  const handleSendQuery = async (queryText) => {
    if (!queryText || !queryText.trim()) {
      return;
    }

    const userMessage = {
      role: "user",
      text: queryText,
    };

    setMessages((prev) => [...prev, userMessage]);
    setLoading(true);

    try {
      console.log("Sending query to backend:", queryText);

      const response = await sendChatMessage(queryText);

      console.log("Backend response:", response);

      setLastResponse(response);

      const assistantMessage = {
        role: "assistant",
        text:
          response.answer ||
          "The backend returned no answer.",

        citations: response.citations || [],

        intent: response.intent || null,

        crag: response.crag_evaluation || null,

        numVal: response.numerical_validation || null,
      };

      setMessages((prev) => [
        ...prev,
        assistantMessage,
      ]);

      // Refresh backend information
      refreshSystemData();

    } catch (error) {
      console.error("RAG API ERROR:", error);

      const errorMessage = {
        role: "assistant",
        text:
          "⚠️ Unable to connect to the RAG backend.\n\n" +
          error.message,
      };

      setMessages((prev) => [
        ...prev,
        errorMessage,
      ]);
    } finally {
      setLoading(false);
    }
  };

  // -----------------------------------------
  // CLEAR CACHE
  // -----------------------------------------
  const handleClearCache = async () => {
    try {
      await clearSystemCache();
      await refreshSystemData();
    } catch (error) {
      console.error("Cache clear error:", error);
    }
  };

  // -----------------------------------------
  // RE-SEED DOCUMENTS
  // -----------------------------------------
  const handleSeed = async () => {
    try {
      await triggerReSeed();
      await refreshSystemData();
    } catch (error) {
      console.error("Seed error:", error);
    }
  };

  return (
    <div
      style={{
        minHeight: "100vh",
        display: "flex",
        flexDirection: "column",
      }}
    >
      {/* NAVBAR */}
      <Navbar
        health={health}
        onOpenDocuments={() =>
          setShowDocManager(true)
        }
        onClearCache={handleClearCache}
        onSeed={handleSeed}
      />

      {/* MAIN APPLICATION */}
      <main
        style={{
          flex: 1,
          display: "grid",
          gridTemplateColumns:
            "minmax(0, 1fr) 380px",
          gap: "24px",
          padding: "24px 32px",
          maxWidth: "1600px",
          width: "100%",
          margin: "0 auto",
          height: "calc(100vh - 75px)",
          overflow: "hidden",
          boxSizing: "border-box",
        }}
      >
        {/* CHAT */}
        <section
          style={{
            height: "100%",
            overflow: "hidden",
          }}
        >
          <ChatContainer
            messages={messages}
            loading={loading}
            onSendQuery={handleSendQuery}
            onSelectCitation={(citation) =>
              setSelectedCitation(citation)
            }
          />
        </section>

        {/* PIPELINE */}
        <aside
          style={{
            height: "100%",
            overflowY: "auto",
          }}
        >
          <PipelineVisualizer
            lastResponse={lastResponse}
            cacheStats={cacheStats}
            onClearCache={handleClearCache}
          />
        </aside>
      </main>

      {/* CITATION MODAL */}
      {selectedCitation && (
        <CitationModal
          citation={selectedCitation}
          onClose={() =>
            setSelectedCitation(null)
          }
        />
      )}

      {/* DOCUMENT MANAGER */}
      {showDocManager && (
        <DocumentManager
          documents={documents}
          onClose={() =>
            setShowDocManager(false)
          }
          onRefreshDocs={refreshSystemData}
        />
      )}
    </div>
  );
}