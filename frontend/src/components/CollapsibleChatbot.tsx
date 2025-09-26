'use client';

import React, { useState, useRef, useEffect } from 'react';

interface Message {
  type: 'user' | 'bot';
  message: string;
  timestamp?: Date;
}

interface CollapsibleChatbotProps {
  messages: Message[];
  onSendMessage: (message: string) => void;
  onResumeUpdate: (data: any) => void;
  onNewSession?: () => void;
  onShowHistory?: () => void;
}

export default function CollapsibleChatbot({ messages, onSendMessage, onResumeUpdate, onNewSession, onShowHistory }: CollapsibleChatbotProps) {
  const [isExpanded, setIsExpanded] = useState(true);
  const [inputMessage, setInputMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [isMounted, setIsMounted] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    setIsMounted(true);
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputMessage.trim()) return;

    const message = inputMessage.trim();
    setInputMessage('');
    setIsTyping(true);

    // Send message to parent component
    onSendMessage(message);

    // Simulate typing delay
    setTimeout(() => {
      setIsTyping(false);
    }, 1000);
  };

  const quickActions = [
    "Improve my summary",
    "Add more skills",
    "Enhance work experience",
    "Fix formatting",
    "Make it more professional",
    "Suggest improvements"
  ];

  return (
    <div className={`bg-white border-l border-gray-200 flex flex-col transition-all duration-300 ease-in-out ${
      isExpanded ? 'w-[500px]' : 'w-16'
    }`}>
      {/* Header */}
      <div className="p-4 border-b border-gray-200 bg-gradient-to-r from-green-600 to-teal-600">
        <div className="flex items-center justify-between">
          {isExpanded ? (
            <>
              <div className="flex items-center text-white">
                <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M18 10c0 3.866-3.582 7-8 7a8.841 8.841 0 01-4.083-.98L2 17l1.338-3.123C2.493 12.767 2 11.434 2 10c0-3.866 3.582-7 8-7s8 3.134 8 7zM7 9H5v2h2V9zm8 0h-2v2h2V9zM9 9h2v2H9V9z" clipRule="evenodd" />
                </svg>
                <h2 className="text-lg font-semibold">AI Assistant</h2>
              </div>
              <div className="flex items-center space-x-2">
                {/* Chat History Button */}
                <button
                  onClick={onShowHistory}
                  className="text-white hover:bg-white hover:bg-opacity-20 p-2 rounded transition-colors"
                  title="Chat History"
                >
                  <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clipRule="evenodd" />
                  </svg>
                </button>
                
                {/* New Chat Button */}
                <button
                  onClick={onNewSession}
                  className="text-white hover:bg-white hover:bg-opacity-20 p-2 rounded transition-colors"
                  title="Start New Chat"
                >
                  <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z" clipRule="evenodd" />
                  </svg>
                </button>
                
                {/* Collapse Button */}
                <button
                  onClick={() => setIsExpanded(false)}
                  className="text-white hover:bg-white hover:bg-opacity-20 p-2 rounded transition-colors"
                  title="Collapse Chat"
                >
                  <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clipRule="evenodd" />
                  </svg>
                </button>
              </div>
            </>
          ) : (
            <button
              onClick={() => setIsExpanded(true)}
              className="w-full flex justify-center text-white hover:bg-white hover:bg-opacity-20 p-2 rounded transition-colors"
              title="Expand Chat"
            >
              <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M18 10c0 3.866-3.582 7-8 7a8.841 8.841 0 01-4.083-.98L2 17l1.338-3.123C2.493 12.767 2 11.434 2 10c0-3.866 3.582-7 8-7s8 3.134 8 7zM7 9H5v2h2V9zm8 0h-2v2h2V9zM9 9h2v2H9V9z" clipRule="evenodd" />
              </svg>
            </button>
          )}
        </div>
        
        {isExpanded && (
          <div className="mt-2">
            <p className="text-sm text-green-100">
              💬 {messages.length} messages • Online
            </p>
          </div>
        )}
      </div>

      {isExpanded ? (
        <>
          {/* Messages Area */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4 min-h-0">
            {messages.map((msg, index) => (
              <div key={index} className={`flex ${msg.type === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-xs px-4 py-3 rounded-2xl ${
                  msg.type === 'user' 
                    ? 'bg-blue-600 text-white rounded-br-md shadow-md' 
                    : 'bg-gray-100 text-gray-800 rounded-bl-md shadow-sm'
                }`}>
                  <p className="text-sm leading-relaxed">{msg.message}</p>
                  {msg.timestamp && isMounted && (
                    <p className="text-xs opacity-70 mt-2">
                      {msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </p>
                  )}
                </div>
              </div>
            ))}
            
            {/* Typing Indicator */}
            {isTyping && (
              <div className="flex justify-start">
                <div className="bg-gray-100 text-gray-800 rounded-2xl rounded-bl-md px-4 py-3 max-w-xs shadow-sm">
                  <div className="flex space-x-1 items-center">
                    <span className="text-sm text-gray-500 mr-2">AI is typing</span>
                    <div className="flex space-x-1">
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                    </div>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Quick Actions */}
          <div className="px-4 py-3 border-t border-gray-200 bg-gray-50">
            <p className="text-xs text-gray-500 mb-3 font-medium">✨ Quick actions:</p>
            <div className="grid grid-cols-2 gap-2">
              {quickActions.map((action, index) => (
                <button
                  key={index}
                  onClick={() => onSendMessage(action)}
                  className="px-3 py-2 text-xs bg-white hover:bg-blue-50 hover:text-blue-700 text-gray-700 rounded-lg border border-gray-200 transition-all duration-200 text-left hover:border-blue-200 hover:shadow-sm"
                >
                  {action}
                </button>
              ))}
            </div>
          </div>

          {/* Input Area */}
          <div className="p-4 border-t border-gray-200">
            <form onSubmit={handleSendMessage} className="space-y-3">
              <div className="relative">
                <input
                  ref={inputRef}
                  type="text"
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  placeholder="Ask me to improve your resume..."
                  className="w-full px-4 py-3 pr-12 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
                  disabled={isTyping}
                />
                <button
                  type="submit"
                  disabled={!inputMessage.trim() || isTyping}
                  className="absolute right-2 top-1/2 transform -translate-y-1/2 p-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200"
                >
                  <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M10.894 2.553a1 1 0 00-1.788 0l-7 14a1 1 0 001.169 1.409l5-1.429A1 1 0 009 15.571V11a1 1 0 112 0v4.571a1 1 0 00.725.962l5 1.428a1 1 0 001.17-1.408l-7-14z"/>
                  </svg>
                </button>
              </div>
              
              <div className="flex items-center justify-between text-xs text-gray-500">
                <span>Press Enter to send</span>
                <div className="flex items-center space-x-1">
                  <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                  <span>AI Online</span>
                </div>
              </div>
            </form>
          </div>
        </>
      ) : (
        /* Collapsed State */
        <div className="flex-1 flex flex-col items-center justify-center space-y-4 p-2">
          {/* Notification badge */}
          {messages.length > 0 && (
            <div className="relative">
              <div className="w-3 h-3 bg-red-500 rounded-full absolute -top-1 -right-1 animate-pulse"></div>
              <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                <span className="text-blue-600 text-xs font-bold">{messages.length}</span>
              </div>
            </div>
          )}
          
          <div className="text-center">
            <div className="text-2xl mb-2">💬</div>
            <p className="text-xs text-gray-500 transform rotate-90 whitespace-nowrap">
              Chat
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
