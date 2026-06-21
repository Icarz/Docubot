"use client";

import { useState, useRef, useCallback, useEffect } from "react";
import { Composer } from "./components/chat/Composer";
import { MessageBubble, Source } from "./components/chat/MessageBubble";
import { TypingIndicator } from "./components/feedback/TypingIndicator";
import { DocumentChip } from "./components/display/DocumentChip";
import { Button } from "./components/forms/Button";
import { IconButton } from "./components/forms/IconButton";
import { sendMessage, uploadPDF, getCollections, Collection } from "@/lib/api";

interface Message {
  id: string;
  role: "user" | "assistant";
  text: string;
  confidence?: "high" | "medium" | "low";
  section?: string;
  sources?: Source[];
}

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [collections, setCollections] = useState<Collection[]>([]);
  const [activeCollection, setActiveCollection] = useState<string | undefined>();
  const [uploadedFile, setUploadedFile] = useState<{ name: string; status: "indexed" | "processing" | "error"; meta?: string } | null>(null);
  const [conversationId] = useState(() => crypto.randomUUID());
  const [userId] = useState(() => crypto.randomUUID());
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    getCollections().then(setCollections).catch(() => {});
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const handleSend = useCallback(async (text: string) => {
    const userMsg: Message = { id: crypto.randomUUID(), role: "user", text };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    try {
      const res = await sendMessage(text, activeCollection || "docubot", conversationId, userId);
      const botMsg: Message = {
        id: crypto.randomUUID(),
        role: "assistant",
        text: res.answer || "I couldn't find an answer in the documents.",
        confidence: res.confidence || undefined,
        section: res.section_referenced || undefined,
        sources: (res.sources || []).map((s) => (typeof s === "string" ? { quote: s } : s)),
      };
      setMessages((prev) => [...prev, botMsg]);
    } catch (err) {
      const errMsg: Message = {
        id: crypto.randomUUID(),
        role: "assistant",
        text: err instanceof Error ? err.message : "Something went wrong. Please try again.",
      };
      setMessages((prev) => [...prev, errMsg]);
    } finally {
      setLoading(false);
    }
  }, [activeCollection, conversationId, userId]);

  const handleUpload = useCallback(async (file: File) => {
    setUploadedFile({ name: file.name, status: "processing", meta: "Uploading…" });
    setSidebarOpen(false);
    try {
      const res = await uploadPDF(file);
      setUploadedFile({ name: file.name, status: "indexed", meta: `${res.chunks_ingested} chunks indexed` });
      setActiveCollection(res.collection_name);
      const cols = await getCollections();
      setCollections(cols);
    } catch {
      setUploadedFile({ name: file.name, status: "error", meta: "Upload failed" });
    }
  }, []);

  const handleFileSelect = () => {
    fileInputRef.current?.click();
  };

  return (
    <div className="app-shell">
      {/* Mobile overlay */}
      {sidebarOpen && (
        <div
          className="sidebar-overlay"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside className={`sidebar ${sidebarOpen ? "sidebar--open" : ""}`}>
        <div style={{ display: "flex", alignItems: "center", gap: 10, justifyContent: "space-between" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
            <span style={{
              width: 32, height: 32, borderRadius: "var(--radius-sm)",
              background: "var(--brand)", color: "#fff",
              display: "inline-flex", alignItems: "center", justifyContent: "center",
            }}>
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <rect x="4" y="8" width="16" height="11" rx="3" />
                <path d="M12 8V4M9 4h6" />
                <circle cx="9" cy="13.5" r="1.3" fill="currentColor" stroke="none" />
                <circle cx="15" cy="13.5" r="1.3" fill="currentColor" stroke="none" />
              </svg>
            </span>
            <h2 style={{ fontSize: "var(--text-lg)", letterSpacing: "var(--tracking-tight)" }}>DocuBot</h2>
          </div>
          <button
            className="sidebar-close"
            onClick={() => setSidebarOpen(false)}
            aria-label="Close sidebar"
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><path d="M18 6 6 18M6 6l12 12" /></svg>
          </button>
        </div>

        <div style={{ flex: 1, display: "flex", flexDirection: "column", gap: "var(--space-3)", overflowY: "auto" }}>
          <span style={{
            fontFamily: "var(--font-sans)", fontSize: "var(--text-2xs)", fontWeight: "var(--weight-bold)",
            color: "var(--text-faint)", textTransform: "uppercase", letterSpacing: "var(--tracking-caps)",
            padding: "0 10px",
          }}>Documents</span>

          {uploadedFile && (
            <DocumentChip
              name={uploadedFile.name}
              status={uploadedFile.status}
              meta={uploadedFile.meta}
              active={true}
              onRemove={() => setUploadedFile(null)}
            />
          )}

          {collections.length === 0 && !uploadedFile && (
            <p style={{ fontSize: "var(--text-sm)", color: "var(--text-muted)", padding: "0 10px" }}>
              No documents uploaded yet. Upload a PDF to get started.
            </p>
          )}

          {collections.map((col) => (
            <DocumentChip
              key={col.name}
              name={col.name.replace("pdf_", "").replace(/_/g, " ")}
              status="indexed"
              meta={`${col.count} chunks`}
              active={activeCollection === col.name}
              onClick={() => { setActiveCollection(col.name); setSidebarOpen(false); }}
            />
          ))}
        </div>

        <Button
          variant="secondary"
          fullWidth
          onClick={handleFileSelect}
          leadingIcon={
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 5v14M5 12h14" /></svg>
          }
        >
          Upload PDF
        </Button>
      </aside>

      {/* Main chat area */}
      <main className="chat-main">
        {/* Mobile header */}
        <header className="mobile-header">
          <IconButton aria-label="Open menu" onClick={() => setSidebarOpen(true)}>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><path d="M3 12h18M3 6h18M3 18h18" /></svg>
          </IconButton>
          <h2 style={{ fontSize: "var(--text-md)", letterSpacing: "var(--tracking-tight)", fontFamily: "var(--font-display)", color: "var(--text-strong)" }}>DocuBot</h2>
          <IconButton aria-label="Upload PDF" onClick={handleFileSelect}>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 5v14M5 12h14" /></svg>
          </IconButton>
        </header>

        {/* Messages */}
        <div className="messages-area">
          {messages.length === 0 && (
            <div className="empty-state">
              <span style={{
                width: 64, height: 64, borderRadius: "var(--radius-lg)",
                background: "var(--brand-subtle)", color: "var(--brand)",
                display: "inline-flex", alignItems: "center", justifyContent: "center",
              }}>
                <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
                  <rect x="4" y="8" width="16" height="11" rx="3" />
                  <path d="M12 8V4M9 4h6" />
                  <circle cx="9" cy="13.5" r="1.3" fill="currentColor" stroke="none" />
                  <circle cx="15" cy="13.5" r="1.3" fill="currentColor" stroke="none" />
                </svg>
              </span>
              <h1 className="empty-state-title">
                Ask your documents anything
              </h1>
              <p className="empty-state-desc">
                Upload a PDF and ask questions. DocuBot will find relevant passages and give you grounded answers with citations.
              </p>
            </div>
          )}

          <div className="messages-container">
            {messages.map((msg) => (
              <MessageBubble
                key={msg.id}
                role={msg.role}
                confidence={msg.confidence}
                section={msg.section}
                sources={msg.sources}
              >
                {msg.text}
              </MessageBubble>
            ))}

            {loading && (
              <div style={{ display: "flex", gap: 12, alignItems: "center" }}>
                <span style={{
                  width: 38, height: 38, borderRadius: "var(--radius-md)",
                  background: "var(--brand)", color: "#fff",
                  display: "inline-flex", alignItems: "center", justifyContent: "center", flexShrink: 0,
                }}>
                  <svg width={21} height={21} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <rect x="4" y="8" width="16" height="11" rx="3" />
                    <path d="M12 8V4M9 4h6" />
                    <circle cx="9" cy="13.5" r="1.3" fill="currentColor" stroke="none" />
                    <circle cx="15" cy="13.5" r="1.3" fill="currentColor" stroke="none" />
                  </svg>
                </span>
                <TypingIndicator label="Searching documents…" />
              </div>
            )}
          </div>
          <div ref={messagesEndRef} />
        </div>

        {/* Composer */}
        <div className="composer-area">
          <div style={{ maxWidth: "var(--composer-max)", margin: "0 auto" }}>
            <Composer
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onSend={handleSend}
              onAttach={handleFileSelect}
              disabled={loading}
              attachedName={uploadedFile?.status === "indexed" ? uploadedFile.name : undefined}
            />
          </div>
        </div>
      </main>

      <input
        ref={fileInputRef}
        type="file"
        accept=".pdf"
        style={{ display: "none" }}
        onChange={(e) => {
          const file = e.target.files?.[0];
          if (file) handleUpload(file);
          e.target.value = "";
        }}
      />
    </div>
  );
}
