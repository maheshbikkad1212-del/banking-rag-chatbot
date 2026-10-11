import React, { useState, useRef, useEffect } from "react";
import {
  Send,
  Bot,
  User,
  FileText,
  Sparkles,
} from "lucide-react";

const SUGGESTED_PROMPTS = [
  "What is the maximum LTV ratio for home loans up to ₹30 Lakhs?",
  "What is the FD interest rate for senior citizens on a 3-year deposit?",
  "What mandatory KYC documents are required to open an NRE account?",
  "What is the minimum Total Capital Adequacy Ratio (CRAR) under RBI Basel III?",
  "Are there foreclosure charges on floating rate housing loans?",
];

export default function ChatContainer({
  messages = [],
  loading = false,
  onSendQuery,
  onSelectCitation,
}) {
  const [input, setInput] = useState("");
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({
      behavior: "smooth",
    });
  }, [messages, loading]);

  const handleSubmit = (e) => {
    e.preventDefault();

    if (!input.trim() || loading) {
      return;
    }

    if (onSendQuery) {
      onSendQuery(input.trim());
    }

    setInput("");
  };

  const handleChipClick = (promptText) => {
    if (loading) {
      return;
    }

    if (onSendQuery) {
      onSendQuery(promptText);
    }
  };

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        height: "100%",
        gap: "16px",
      }}
    >
      {/* Messages Area */}
      <div
        style={{
          flex: 1,
          overflowY: "auto",
          paddingRight: "8px",
          display: "flex",
          flexDirection: "column",
          gap: "20px",
        }}
      >
        {messages.length === 0 ? (
          <div
            className="glass-panel"
            style={{
              padding: "40px 24px",
              textAlign: "center",
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              justifyContent: "center",
              marginTop: "20px",
            }}
          >
            {/* Bot Icon */}
            <div
              style={{
                width: "60px",
                height: "60px",
                borderRadius: "20px",
                background:
                  "linear-gradient(135deg, rgba(59, 130, 246, 0.3), rgba(16, 185, 129, 0.3))",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                marginBottom: "16px",
                boxShadow:
                  "0 0 30px rgba(59, 130, 246, 0.3)",
              }}
            >
              <Bot size={32} color="#60A5FA" />
            </div>

            <h2
              style={{
                fontSize: "1.4rem",
                color: "#F9FAFB",
                fontWeight: 800,
                marginBottom: "8px",
              }}
            >
              BankSmart RAG Policy Assistant
            </h2>

            <p
              style={{
                fontSize: "0.9rem",
                color: "#9CA3AF",
                maxWidth: "520px",
                lineHeight: "1.6",
                marginBottom: "24px",
              }}
            >
              Ask policy questions on Loan Eligibility, Fixed Deposit
              Rates, KYC Onboarding, or RBI Regulatory Guidelines.
            </p>

            {/* Suggested Questions */}
            <div
              style={{
                width: "100%",
                maxWidth: "640px",
              }}
            >
              <p
                style={{
                  fontSize: "0.78rem",
                  color: "#6B7280",
                  textTransform: "uppercase",
                  letterSpacing: "0.05em",
                  fontWeight: 700,
                  marginBottom: "12px",
                }}
              >
                Suggested Banking Queries
              </p>

              <div
                style={{
                  display: "flex",
                  flexWrap: "wrap",
                  gap: "8px",
                  justifyContent: "center",
                }}
              >
                {SUGGESTED_PROMPTS.map((prompt, idx) => (
                  <button
                    key={idx}
                    onClick={() => handleChipClick(prompt)}
                    disabled={loading}
                    className="glass-pill"
                    style={{
                      cursor: loading
                        ? "not-allowed"
                        : "pointer",
                      color: "#D1D5DB",
                      background:
                        "rgba(30, 41, 59, 0.6)",
                      border:
                        "1px solid rgba(255, 255, 255, 0.08)",
                      textAlign: "left",
                      padding: "8px 12px",
                    }}
                  >
                    💡 {prompt}
                  </button>
                ))}
              </div>
            </div>
          </div>
        ) : (
          messages.map((msg, idx) => (
            <div
              key={idx}
              style={{
                display: "flex",
                flexDirection: "column",
                alignSelf:
                  msg.role === "user"
                    ? "flex-end"
                    : "flex-start",
                maxWidth:
                  msg.role === "user" ? "80%" : "100%",
                gap: "6px",
              }}
            >
              {/* Header */}
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "8px",
                  alignSelf:
                    msg.role === "user"
                      ? "flex-end"
                      : "flex-start",
                  fontSize: "0.75rem",
                  color: "#9CA3AF",
                }}
              >
                {msg.role === "user" ? (
                  <>
                    <span>You</span>
                    <User size={14} color="#60A5FA" />
                  </>
                ) : (
                  <>
                    <Bot size={14} color="#34D399" />
                    <span>BankSmart Assistant</span>
                  </>
                )}
              </div>

              {/* Message */}
              <div
                className="glass-panel"
                style={{
                  padding: "18px 22px",
                  background:
                    msg.role === "user"
                      ? "linear-gradient(135deg, rgba(59, 130, 246, 0.25), rgba(30, 58, 138, 0.3))"
                      : "rgba(17, 24, 39, 0.85)",
                  borderColor:
                    msg.role === "user"
                      ? "rgba(59, 130, 246, 0.4)"
                      : "rgba(255, 255, 255, 0.08)",
                  whiteSpace: "pre-wrap",
                  lineHeight: "1.7",
                  fontSize: "0.94rem",
                  color: "#F9FAFB",
                }}
              >
                {msg.text}

                {/* Citations */}
                {msg.citations &&
                  msg.citations.length > 0 && (
                    <div
                      style={{
                        marginTop: "16px",
                        paddingTop: "14px",
                        borderTop:
                          "1px solid rgba(255, 255, 255, 0.08)",
                      }}
                    >
                      <p
                        style={{
                          fontSize: "0.75rem",
                          color: "#9CA3AF",
                          textTransform: "uppercase",
                          letterSpacing: "0.05em",
                          fontWeight: 700,
                          marginBottom: "8px",
                        }}
                      >
                        Official Policy References (
                        {msg.citations.length})
                      </p>

                      <div
                        style={{
                          display: "flex",
                          flexWrap: "wrap",
                          gap: "8px",
                        }}
                      >
                        {msg.citations.map((cit, cIdx) => (
                          <button
                            key={cIdx}
                            onClick={() =>
                              onSelectCitation &&
                              onSelectCitation(cit)
                            }
                            className="glass-pill"
                            style={{
                              cursor: "pointer",
                              color: "#60A5FA",
                              background:
                                "rgba(59, 130, 246, 0.12)",
                              borderColor:
                                "rgba(59, 130, 246, 0.3)",
                              display: "flex",
                              alignItems: "center",
                              gap: "6px",
                            }}
                          >
                            <FileText size={13} />

                            <span>
                              {cit.doc_name}{" "}
                              (Page {cit.page_number})
                            </span>
                          </button>
                        ))}
                      </div>
                    </div>
                  )}
              </div>
            </div>
          ))
        )}

        {/* Loading */}
        {loading && (
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: "10px",
              color: "#60A5FA",
              padding: "12px 18px",
            }}
          >
            <Sparkles
              size={18}
              className="glowing-dot"
            />

            <span
              style={{
                fontSize: "0.88rem",
              }}
            >
              Processing Hybrid Search, CRAG Evaluation &
              Numerical Guardrails...
            </span>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <form
        onSubmit={handleSubmit}
        style={{
          position: "relative",
          display: "flex",
          alignItems: "center",
        }}
      >
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask policy question..."
          className="glass-input"
          style={{
            paddingRight: "120px",
            height: "54px",
            width: "100%",
            boxSizing: "border-box",
          }}
          disabled={loading}
        />

        <button
          type="submit"
          disabled={loading || !input.trim()}
          className="glass-button"
          style={{
            position: "absolute",
            right: "8px",
            height: "38px",
            padding: "0 16px",
            fontSize: "0.85rem",
            display: "flex",
            alignItems: "center",
            gap: "6px",
          }}
        >
          <span>Ask Policy</span>
          <Send size={15} />
        </button>
      </form>
    </div>
  );
}