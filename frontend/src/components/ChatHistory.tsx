'use client';

import React, { useState, useEffect } from 'react';

interface Session {
  session_id: string;
  title: string;
  message_count: number;
  created_at: string;
  last_activity: string;
  is_active: boolean;
}

interface Message {
  id: string;
  type: 'user' | 'bot';
  message: string;
  timestamp: string;
  metadata?: any;
}

interface ChatHistoryProps {
  userId: string;
  currentSessionId?: string;
  onSessionSelect: (sessionId: string) => void;
  onNewSession: () => void;
  onClose: () => void;
  isVisible: boolean;
}

export default function ChatHistory({ 
  userId, 
  currentSessionId, 
  onSessionSelect, 
  onNewSession, 
  onClose, 
  isVisible 
}: ChatHistoryProps) {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [selectedSession, setSelectedSession] = useState<Session | null>(null);
  const [sessionMessages, setSessionMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [showDeleteConfirm, setShowDeleteConfirm] = useState<string | null>(null);

  // Load user sessions
  useEffect(() => {
    if (isVisible && userId) {
      loadSessions();
    }
  }, [isVisible, userId]);

  const loadSessions = async () => {
    setLoading(true);
    try {
      const response = await fetch(`http://localhost:8000/chat/sessions?user_id=${userId}&limit=50`);
      if (response.ok) {
        const data = await response.json();
        setSessions(data);
      } else {
        console.error('Failed to load sessions');
      }
    } catch (error) {
      console.error('Error loading sessions:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadSessionMessages = async (sessionId: string) => {
    setLoading(true);
    try {
      const response = await fetch(
        `http://localhost:8000/chat/sessions/${sessionId}?user_id=${userId}&limit=100`
      );
      if (response.ok) {
        const messages = await response.json();
        setSessionMessages(messages);
        const session = sessions.find(s => s.session_id === sessionId);
        setSelectedSession(session || null);
      }
    } catch (error) {
      console.error('Error loading session messages:', error);
    } finally {
      setLoading(false);
    }
  };

  const deleteSession = async (sessionId: string) => {
    try {
      const response = await fetch(
        `http://localhost:8000/chat/sessions/${sessionId}?user_id=${userId}`,
        { method: 'DELETE' }
      );
      if (response.ok) {
        setSessions(sessions.filter(s => s.session_id !== sessionId));
        if (selectedSession?.session_id === sessionId) {
          setSelectedSession(null);
          setSessionMessages([]);
        }
        setShowDeleteConfirm(null);
      }
    } catch (error) {
      console.error('Error deleting session:', error);
    }
  };

  const switchToSession = (sessionId: string) => {
    onSessionSelect(sessionId);
    onClose();
  };

  const filteredSessions = sessions.filter(session =>
    session.title.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffDays = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60 * 24));
    
    if (diffDays === 0) {
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    } else if (diffDays === 1) {
      return 'Yesterday';
    } else if (diffDays < 7) {
      return `${diffDays} days ago`;
    } else {
      return date.toLocaleDateString();
    }
  };

  if (!isVisible) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex justify-end">
      <div className="w-96 bg-white h-full shadow-xl flex flex-col">
        {/* Header */}
        <div className="bg-blue-600 text-white p-4 flex items-center justify-between">
          <h2 className="text-lg font-semibold">Chat History</h2>
          <button
            onClick={onClose}
            className="text-white hover:bg-white hover:bg-opacity-20 p-1 rounded transition-colors"
          >
            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
            </svg>
          </button>
        </div>

        {/* Search and New Session */}
        <div className="p-4 border-b border-gray-200">
          <div className="flex space-x-2 mb-3">
            <button
              onClick={onNewSession}
              className="flex-1 bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors flex items-center justify-center"
            >
              <svg className="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z" clipRule="evenodd" />
              </svg>
              New Chat
            </button>
          </div>
          <div className="relative">
            <input
              type="text"
              placeholder="Search sessions..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 pr-10"
            />
            <svg className="w-4 h-4 text-gray-400 absolute right-3 top-3" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" clipRule="evenodd" />
            </svg>
          </div>
        </div>

        {/* Sessions List */}
        <div className="flex-1 overflow-y-auto">
          {loading && (
            <div className="p-4 text-center text-gray-500">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
              <p className="mt-2">Loading sessions...</p>
            </div>
          )}

          {!loading && filteredSessions.length === 0 && (
            <div className="p-4 text-center text-gray-500">
              <svg className="w-12 h-12 mx-auto mb-3 text-gray-300" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M18 10c0 3.866-3.582 7-8 7a8.841 8.841 0 01-4.083-.98L2 17l1.338-3.123C2.493 12.767 2 11.434 2 10c0-3.866 3.582-7 8-7s8 3.134 8 7zM7 9H5v2h2V9zm8 0h-2v2h2V9zM9 9h2v2H9V9z" clipRule="evenodd" />
              </svg>
              <p>No chat sessions found</p>
            </div>
          )}

          {!loading && filteredSessions.map((session) => (
            <div
              key={session.session_id}
              className={`p-4 border-b border-gray-100 hover:bg-gray-50 cursor-pointer relative group ${
                currentSessionId === session.session_id ? 'bg-blue-50 border-l-4 border-l-blue-600' : ''
              }`}
            >
              <div onClick={() => switchToSession(session.session_id)}>
                <div className="flex items-start justify-between">
                  <div className="flex-1 min-w-0">
                    <h3 className="text-sm font-medium text-gray-900 truncate">
                      {session.title}
                    </h3>
                    <p className="text-xs text-gray-500 mt-1">
                      {session.message_count} messages • {formatDate(session.last_activity)}
                    </p>
                  </div>
                  {session.is_active && (
                    <div className="w-2 h-2 bg-green-400 rounded-full ml-2 mt-1"></div>
                  )}
                </div>
              </div>

              {/* Session Actions */}
              <div className="absolute right-2 top-2 opacity-0 group-hover:opacity-100 transition-opacity">
                <div className="flex space-x-1">
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      loadSessionMessages(session.session_id);
                    }}
                    className="p-1 text-gray-400 hover:text-blue-600 rounded"
                    title="View messages"
                  >
                    <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M10 12a2 2 0 100-4 2 2 0 000 4z"/>
                      <path fillRule="evenodd" d="M.458 10C1.732 5.943 5.522 3 10 3s8.268 2.943 9.542 7c-1.274 4.057-5.064 7-9.542 7S1.732 14.057.458 10zM14 10a4 4 0 11-8 0 4 4 0 018 0z" clipRule="evenodd"/>
                    </svg>
                  </button>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      setShowDeleteConfirm(session.session_id);
                    }}
                    className="p-1 text-gray-400 hover:text-red-600 rounded"
                    title="Delete session"
                  >
                    <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M9 2a1 1 0 000 2h2a1 1 0 100-2H9zM4 5a2 2 0 012-2h8a2 2 0 012 2v6a2 2 0 01-2 2H6a2 2 0 01-2-2V5zm3 4a1 1 0 102 0v3a1 1 0 11-2 0V9zm4 0a1 1 0 10-2 0v3a1 1 0 102 0V9z" clipRule="evenodd"/>
                    </svg>
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Session Messages Modal */}
        {selectedSession && (
          <div className="absolute inset-0 bg-white z-10 flex flex-col">
            <div className="bg-gray-50 border-b border-gray-200 p-4 flex items-center justify-between">
              <div>
                <h3 className="font-medium text-gray-900">{selectedSession.title}</h3>
                <p className="text-sm text-gray-500">
                  {selectedSession.message_count} messages • {formatDate(selectedSession.created_at)}
                </p>
              </div>
              <button
                onClick={() => {
                  setSelectedSession(null);
                  setSessionMessages([]);
                }}
                className="text-gray-400 hover:text-gray-600 p-1 rounded"
              >
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                </svg>
              </button>
            </div>

            <div className="flex-1 overflow-y-auto p-4 space-y-3">
              {sessionMessages.map((message) => (
                <div
                  key={message.id}
                  className={`flex ${message.type === 'human' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-xs px-3 py-2 rounded-lg text-sm ${
                      message.type === 'human'
                        ? 'bg-blue-600 text-white rounded-br-none'
                        : 'bg-gray-100 text-gray-800 rounded-bl-none'
                    }`}
                  >
                    <p>{message.message}</p>
                    <p className="text-xs opacity-70 mt-1">
                      {new Date(message.timestamp).toLocaleTimeString([], { 
                        hour: '2-digit', 
                        minute: '2-digit' 
                      })}
                    </p>
                  </div>
                </div>
              ))}
            </div>

            <div className="border-t border-gray-200 p-4">
              <button
                onClick={() => switchToSession(selectedSession.session_id)}
                className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 transition-colors"
              >
                Switch to This Session
              </button>
            </div>
          </div>
        )}

        {/* Delete Confirmation Modal */}
        {showDeleteConfirm && (
          <div className="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center z-20">
            <div className="bg-white rounded-lg p-6 max-w-sm mx-4">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Delete Session</h3>
              <p className="text-gray-600 mb-6">
                Are you sure you want to delete this chat session? This action cannot be undone.
              </p>
              <div className="flex justify-end space-x-3">
                <button
                  onClick={() => setShowDeleteConfirm(null)}
                  className="px-4 py-2 text-gray-600 border border-gray-300 rounded-md hover:bg-gray-50 transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={() => deleteSession(showDeleteConfirm)}
                  className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors"
                >
                  Delete
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
