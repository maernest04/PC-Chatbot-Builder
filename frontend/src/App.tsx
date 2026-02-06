import { useCallback, useEffect, useState } from 'react';
import { BuildCard } from './components/BuildCard';
import { ChatInput } from './components/ChatInput';
import { MessageList } from './components/MessageList';
import { SessionList } from './components/SessionList';
import { getSession, getSessions, postChat } from './api/client';
import type { Build, Message, Session } from './api/client';

function App() {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [build, setBuild] = useState<Build | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadSessions = useCallback(async () => {
    try {
      const list = await getSessions();
      setSessions(list);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to load sessions');
    }
  }, []);

  const loadSession = useCallback(async (id: string) => {
    setError(null);
    try {
      const detail = await getSession(id);
      setMessages(detail.messages);
      setBuild(detail.build);
      setSessionId(id);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to load session');
    }
  }, []);

  useEffect(() => {
    loadSessions();
  }, [loadSessions]);

  const handleNewChat = () => {
    setSessionId(null);
    setMessages([]);
    setBuild(null);
    setError(null);
  };

  const handleSend = async (content: string) => {
    setError(null);
    setLoading(true);
    try {
      const res = await postChat(sessionId, content);
      setSessionId(res.session_id);
      setMessages((prev) => [
        ...prev,
        { role: 'user', content, created_at: new Date().toISOString() },
        { role: 'assistant', content: res.reply, created_at: new Date().toISOString() },
      ]);
      if (res.build) setBuild(res.build);
      await loadSessions();
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to send message');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="h-screen flex flex-col bg-slate-100 dark:bg-slate-950 text-slate-900 dark:text-slate-100">
      <header className="shrink-0 border-b border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 px-5 py-3.5 shadow-sm">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-indigo-500 flex items-center justify-center shadow-md shadow-indigo-500/25">
            <svg className="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09z" />
            </svg>
          </div>
          <div>
            <h1 className="text-lg font-bold text-slate-900 dark:text-slate-100">PC Builder</h1>
            <p className="text-xs text-slate-500 dark:text-slate-400">Part suggestions and pricing with tax</p>
          </div>
        </div>
      </header>
      <div className="flex-1 flex min-h-0">
        <SessionList
          sessions={sessions}
          currentId={sessionId}
          onSelect={loadSession}
          onNew={handleNewChat}
        />
        <div className="flex-1 flex flex-col min-w-0">
          {error && (
            <div className="shrink-0 px-4 py-2.5 bg-red-50 dark:bg-red-900/20 border-b border-red-200 dark:border-red-800 text-red-700 dark:text-red-300 text-sm font-medium flex items-center gap-2">
              <svg className="w-4 h-4 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              {error}
            </div>
          )}
          <div className="flex-1 flex flex-col min-h-0 overflow-hidden">
            <MessageList messages={messages} onSuggestion={handleSend} />
            {build && (
              <div className="shrink-0 p-4 border-t border-slate-200 dark:border-slate-700 bg-slate-50/50 dark:bg-slate-900/30">
                <div className="max-w-3xl mx-auto">
                  <BuildCard build={build} />
                </div>
              </div>
            )}
          </div>
          <ChatInput onSend={handleSend} disabled={loading} />
        </div>
      </div>
    </div>
  );
}

export default App;
