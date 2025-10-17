import { useState, useEffect, useRef } from 'react';

// API Configuration
// const API_BASE_URL = 'http://localhost:8000';

import config from './config';
const API_BASE_URL = config.apiBaseUrl;

// Icons
const Icons = {
    Plus: () => (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
        </svg>
    ),
    Search: () => (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
    ),
    Send: () => (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" />
        </svg>
    ),
    Star: ({ filled }) => (
        <svg className="w-5 h-5" fill={filled ? "currentColor" : "none"} stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
        </svg>
    ),
    ThumbUp: () => (
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 10h4.764a2 2 0 011.789 2.894l-3.5 7A2 2 0 0115.263 21h-4.017c-.163 0-.326-.02-.485-.06L7 20m7-10V5a2 2 0 00-2-2h-.095c-.5 0-.905.405-.905.905 0 .714-.211 1.412-.608 2.006L7 11v9m7-10h-2M7 20H5a2 2 0 01-2-2v-6a2 2 0 012-2h2.5" />
        </svg>
    ),
    Copy: () => (
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
        </svg>
    ),
    Trash: () => (
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
        </svg>
    ),
    Settings: () => (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
        </svg>
    ),
    Menu: () => (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
        </svg>
    ),
    Close: () => (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
        </svg>
    ),
};

const fetchTitleFromAPI = async (question) => {
    try {
        const resp = await fetch(`${API_BASE_URL}/api/topic-title`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query: question })
        });
        if (!resp.ok) throw new Error();
        const data = await resp.json();
        return data.title || question.split(' ').slice(0, 7).join(' ') + '...';
    } catch (err) {
        return question.split(' ').slice(0, 7).join(' ') + '...';
    }
};

// Main App Component
function MathAgentApp() {
    const [conversations, setConversations] = useState({});
    const [activeConversationId, setActiveConversationId] = useState(null);
    const [inputValue, setInputValue] = useState('');
    const [loading, setLoading] = useState(false);
    const [showFeedback, setShowFeedback] = useState(null);
    const [feedbackRating, setFeedbackRating] = useState(0);
    const [feedbackCorrection, setFeedbackCorrection] = useState('');
    const [sidebarOpen, setSidebarOpen] = useState(true);
    const [isRenaming, setIsRenaming] = useState(false);
    const [renameValue, setRenameValue] = useState('');
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [conversations, activeConversationId]);

    useEffect(() => {
        loadConversations();
    }, []);

    const loadConversations = async () => {
        try {
            const response = await fetch(`${API_BASE_URL}/api/conversations/recent?limit=50`);
            const data = await response.json();
            
            const grouped = {};
            (data.conversations || []).forEach(conv => {
                const threadId = conv.id;
                if (!grouped[threadId]) {
                    grouped[threadId] = {
                        id: threadId,
                        title: conv.query.substring(0, 50) + (conv.query.length > 50 ? '...' : ''),
                        createdAt: conv.created_at,
                        messages: []
                    };
                }
                grouped[threadId].messages.push(
                    { id: `${conv.id}-q`, role: 'user', content: conv.query, timestamp: conv.created_at },
                    { id: `${conv.id}-a`, role: 'assistant', content: conv.answer, source: conv.source, confidence: conv.confidence_score, conversationId: conv.id, timestamp: conv.created_at }
                );
            });
            
            setConversations(grouped);
        } catch (error) {
            console.error('Failed to load conversations:', error);
        }
    };

    const handleNewChat = () => {
        const newId = Date.now();
        setConversations(prev => ({
            ...prev,
            [newId]: {
                id: newId,
                title: 'New conversation',
                createdAt: new Date().toISOString(),
                messages: []
            }
        }));
        setActiveConversationId(newId);
    };

    const handleSelectConversation = (id) => {
        setActiveConversationId(id);
    };

    const handleDeleteConversation = async (id) => {
        if (!confirm('Delete this conversation?')) return;
        
        setConversations(prev => {
            const newConvs = { ...prev };
            delete newConvs[id];
            return newConvs;
        });
        
        if (activeConversationId === id) {
            setActiveConversationId(null);
        }
    };

    const handleDeleteMessage = (conversationId, messageId) => {
        if (!confirm('Delete this message?')) return;
        
        setConversations(prev => ({
            ...prev,
            [conversationId]: {
                ...prev[conversationId],
                messages: prev[conversationId].messages.filter(m => m.id !== messageId)
            }
        }));
    };

    const handleClearAll = () => {
        if (!confirm('Delete all conversations? This cannot be undone.')) return;
        setConversations({});
        setActiveConversationId(null);
    };

   const handleSubmit = async (e) => {
    e.preventDefault();
    if (!inputValue.trim() || loading) return;

    const savedInputValue = inputValue;
    
    // Check if there's an active conversation to continue
    let convId = activeConversationId;
    
    // If no active conversation OR active conversation doesn't exist in state, create new one
    if (!convId || !conversations[convId]) {
        convId = Date.now();
        setConversations(prev => ({
            ...prev,
            [convId]: {
                id: convId,
                title: 'Loading...', // Will be replaced by auto-title
                createdAt: new Date().toISOString(),
                messages: []
            }
        }));
        setActiveConversationId(convId);
    }

    // Add user message to the conversation
    const userMessage = {
        id: Date.now(),
        role: 'user',
        content: savedInputValue,
        timestamp: new Date().toISOString()
    };

    setConversations(prev => ({
        ...prev,
        [convId]: {
            ...prev[convId],
            messages: [...(prev[convId]?.messages || []), userMessage]
        }
    }));

    setInputValue('');
    setLoading(true);

    try {
        // Only fetch title if this is the first message in conversation
        const isFirstMessage = (conversations[convId]?.messages || []).length === 0;
        
        let autoTitle = conversations[convId]?.title || savedInputValue.split(' ').slice(0, 7).join(' ') + '...';
        
        if (isFirstMessage) {
            autoTitle = await fetchTitleFromAPI(savedInputValue);
            setConversations(prev => ({
                ...prev,
                [convId]: {
                    ...prev[convId],
                    title: autoTitle
                }
            }));
        }

        // Fetch answer from backend
        const response = await fetch(`${API_BASE_URL}/api/query`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query: savedInputValue })
        });

        const data = await response.json();

        const assistantMessage = {
            id: Date.now() + 1,
            role: 'assistant',
            content: data.answer,
            source: data.source,
            confidence: data.confidence_score,
            conversationId: data.conversation_id,
            timestamp: new Date().toISOString()
        };

        // Add assistant message to the SAME conversation
        setConversations(prev => ({
            ...prev,
            [convId]: {
                ...prev[convId],
                messages: [...(prev[convId]?.messages || []), assistantMessage]
            }
        }));

    } catch (error) {
        console.error('Query failed:', error);
        setConversations(prev => ({
            ...prev,
            [convId]: {
                ...prev[convId],
                messages: [...(prev[convId]?.messages || []), {
                    id: Date.now() + 1,
                    role: 'error',
                    content: 'Failed to get response. Please check if the backend is running.',
                    timestamp: new Date().toISOString()
                }]
            }
        }));
    } finally {
        setLoading(false);
    }
};


    const handleFeedback = async (messageId, rating) => {
        const activeConv = conversations[activeConversationId];
        const message = activeConv?.messages.find(m => m.id === messageId);
        if (!message) return;

        const messageIndex = activeConv.messages.indexOf(message);
        const userMessage = activeConv.messages[messageIndex - 1];

        try {
            await fetch(`${API_BASE_URL}/api/feedback`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    query: userMessage?.content || '',
                    answer: message.content,
                    rating: rating,
                    is_correct: rating >= 4,
                    correction: feedbackCorrection || null,
                    notes: null,
                    conversation_id: message.conversationId
                })
            });

            alert('Feedback submitted! Thank you 🎉');
            setShowFeedback(null);
            setFeedbackRating(0);
            setFeedbackCorrection('');

        } catch (error) {
            console.error('Feedback submission failed:', error);
        }
    };

    const activeConversation = conversations[activeConversationId];
    const conversationList = Object.values(conversations).sort((a, b) => 
        new Date(b.createdAt) - new Date(a.createdAt)
    );

    return (
        <div className="flex h-screen bg-gray-50">
            {/* Sidebar */}
            <div className={`${sidebarOpen ? 'w-64' : 'w-0'} transition-all duration-300 bg-white border-r border-gray-200 flex flex-col overflow-hidden`}>
                <div className="p-4 border-b border-gray-200 flex items-center justify-between">
                    <h1 className="text-xl font-bold text-gray-900">MATH A.I+</h1>
                    <button
                        onClick={() => setSidebarOpen(false)}
                        className="text-gray-500 hover:text-gray-700 lg:hidden"
                    >
                        <Icons.Close />
                    </button>
                </div>

                <div className="p-3">
                    <button
                        onClick={handleNewChat}
                        className="w-full flex items-center gap-2 px-4 py-2.5 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
                    >
                        <Icons.Plus />
                        <span className="font-medium">New chat</span>
                    </button>
                </div>

                <div className="flex-1 overflow-y-auto px-3 py-2">
                    <div className="flex items-center justify-between mb-2 px-2">
                        <span className="text-xs font-semibold text-gray-500 uppercase">Your conversations</span>
                        <button 
                            onClick={handleClearAll}
                            className="text-xs text-red-600 hover:underline"
                        >
                            Clear All
                        </button>
                    </div>

                    {conversationList.length === 0 ? (
                        <p className="text-sm text-gray-500 px-2 py-4">No conversations yet</p>
                    ) : (
                        conversationList.map((conv) => (
                            <div
                                key={conv.id}
                                className={`group flex items-start gap-2 px-3 py-2 rounded-lg cursor-pointer hover:bg-gray-100 transition-colors mb-1 ${activeConversationId === conv.id ? 'bg-gray-100' : ''}`}
                            >
                                <div
                                    onClick={() => handleSelectConversation(conv.id)}
                                    className="flex-1 min-w-0"
                                >
                                    <div className="flex items-center gap-2">
                                        <Icons.Search />
                                        <p className="text-sm text-gray-900 truncate">{conv.title}</p>
                                    </div>
                                    <p className="text-xs text-gray-500 ml-7">{new Date(conv.createdAt).toLocaleDateString()}</p>
                                </div>
                                <button
                                    onClick={(e) => {
                                        e.stopPropagation();
                                        handleDeleteConversation(conv.id);
                                    }}
                                    className="opacity-0 group-hover:opacity-100 text-red-600 hover:text-red-700 transition-opacity"
                                >
                                    <Icons.Trash />
                                </button>
                            </div>
                        ))
                    )}
                </div>

                <div className="border-t border-gray-200 p-4">
                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-full bg-indigo-600 text-white flex items-center justify-center font-semibold">
                            U
                        </div>
                        <div className="flex-1">
                            <p className="text-sm font-medium text-gray-900">Student User</p>
                            <p className="text-xs text-gray-500">Free Plan</p>
                        </div>
                        <button className="text-gray-500 hover:text-gray-700">
                            <Icons.Settings />
                        </button>
                    </div>
                </div>
            </div>

            {/* Main Chat Area */}
            <div className="flex-1 flex flex-col">
                <div className="bg-white border-b border-gray-200 p-4 flex items-center gap-3">
                    <button
                        onClick={() => setSidebarOpen(!sidebarOpen)}
                        className="text-gray-500 hover:text-gray-700"
                    >
                        <Icons.Menu />
                    </button>
                    <h2 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
                        {isRenaming ? (
                            <input
                                value={renameValue}
                                onChange={e => setRenameValue(e.target.value)}
                                onBlur={() => {
                                    setConversations(prev => ({
                                        ...prev,
                                        [activeConversationId]: {
                                            ...prev[activeConversationId],
                                            title: renameValue
                                        }
                                    }));
                                    setIsRenaming(false);
                                }}
                                onKeyDown={e => {
                                    if (e.key === 'Enter' || e.key === 'Escape') {
                                        setConversations(prev => ({
                                            ...prev,
                                            [activeConversationId]: {
                                                ...prev[activeConversationId],
                                                title: renameValue
                                            }
                                        }));
                                        setIsRenaming(false);
                                    }
                                }}
                                className="border px-2 py-0.5 text-base rounded"
                                autoFocus
                            />
                        ) : (
                            <>
                                {activeConversation?.title || 'Math A.I+ Assistant'}
                                {activeConversation && (
                                    <button
                                        className="ml-1 px-2 py-1 text-xs text-gray-400 hover:text-gray-900"
                                        onClick={() => {
                                            setRenameValue(activeConversation?.title || '');
                                            setIsRenaming(true);
                                        }}>
                                        ✎
                                    </button>
                                )}
                            </>
                        )}
                    </h2>
                </div>

                <div className="flex-1 overflow-y-auto px-4 py-6">
                    {!activeConversation || activeConversation.messages.length === 0 ? (
                        <div className="h-full flex items-center justify-center">
                            <div className="text-center max-w-md">
                                <div className="w-16 h-16 bg-indigo-600 rounded-full flex items-center justify-center mx-auto mb-4">
                                    <span className="text-2xl text-white">∫</span>
                                </div>
                                <h2 className="text-2xl font-bold text-gray-900 mb-2">Math A.I+ Assistant</h2>
                                <p className="text-gray-600 mb-6">Ask me any math question! I can solve equations, explain concepts, and help with calculus, algebra, geometry, and more.</p>
                                <div className="grid grid-cols-2 gap-3 text-left">
                                    {[
                                        'What is the quadratic formula?',
                                        'Solve: 2x + 5 = 15',
                                        'Explain derivatives',
                                        'Find integral of 2x dx'
                                    ].map((example, i) => (
                                        <button
                                            key={i}
                                            onClick={() => setInputValue(example)}
                                            className="p-3 text-sm text-gray-700 bg-white border border-gray-200 rounded-lg hover:border-indigo-600 hover:bg-gray-50 transition-colors text-left"
                                        >
                                            {example}
                                        </button>
                                    ))}
                                </div>
                            </div>
                        </div>
                    ) : (
                        <div className="max-w-3xl mx-auto space-y-6">
                            {activeConversation.messages.map((message) => (
                                <div key={message.id} className="group">
                                    {message.role === 'user' ? (
                                        <div className="flex gap-4">
                                            <div className="w-8 h-8 rounded-full bg-blue-500 text-white flex items-center justify-center flex-shrink-0 font-semibold">
                                                U
                                            </div>
                                            <div className="flex-1 pt-1">
                                                <p className="text-gray-900">{message.content}</p>
                                            </div>
                                            <button
                                                onClick={() => handleDeleteMessage(activeConversationId, message.id)}
                                                className="opacity-0 group-hover:opacity-100 text-red-600 hover:text-red-700 transition-opacity"
                                            >
                                                <Icons.Trash />
                                            </button>
                                        </div>
                                    ) : message.role === 'assistant' ? (
                                        <div className="flex gap-4">
                                            <div className="w-8 h-8 rounded-full bg-indigo-600 text-white flex items-center justify-center flex-shrink-0">
                                                <span className="text-lg">∑</span>
                                            </div>
                                            <div className="flex-1">
                                                <div className="flex items-center gap-2 mb-2">
                                                    <span className="text-sm font-semibold text-gray-900">MATH A.I+</span>
                                                    <span className={`text-xs px-2 py-0.5 rounded-full ${
                                                        message.source === 'knowledge_base' ? 'bg-green-100 text-green-700' :
                                                        message.source === 'web_search' ? 'bg-blue-100 text-blue-700' :
                                                        'bg-gray-100 text-gray-700'
                                                    }`}>
                                                        {message.source === 'knowledge_base' ? '📚 Knowledge Base' :
                                                         message.source === 'web_search' ? '🌐 Web Search' :
                                                         '🤖 AI Generated'}
                                                    </span>
                                                    {message.confidence > 0 && (
                                                        <span className="text-xs text-gray-500">
                                                            {(message.confidence * 100).toFixed(0)}% confidence
                                                        </span>
                                                    )}
                                                </div>
                                                <div className="prose prose-sm max-w-none text-gray-800 whitespace-pre-wrap">
                                                    {message.content}
                                                </div>
                                                
                                                <div className="flex items-center gap-2 mt-4">
                                                    <button 
                                                        onClick={() => navigator.clipboard.writeText(message.content)}
                                                        className="flex items-center gap-1 px-3 py-1.5 text-sm text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
                                                    >
                                                        <Icons.Copy />
                                                        Copy
                                                    </button>
                                                    <button
                                                        onClick={() => setShowFeedback(message.id)}
                                                        className="flex items-center gap-1 px-3 py-1.5 text-sm text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
                                                    >
                                                        <Icons.ThumbUp />
                                                        Feedback
                                                    </button>
                                                    <button
                                                        onClick={() => handleDeleteMessage(activeConversationId, message.id)}
                                                        className="flex items-center gap-1 px-3 py-1.5 text-sm text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                                                    >
                                                        <Icons.Trash />
                                                        Delete
                                                    </button>
                                                </div>

                                                {showFeedback === message.id && (
                                                    <div className="mt-4 p-4 bg-gray-50 border border-gray-200 rounded-lg">
                                                        <p className="text-sm font-medium text-gray-900 mb-3">Rate this response:</p>
                                                        <div className="flex gap-2 mb-4">
                                                            {[1, 2, 3, 4, 5].map(star => (
                                                                <button
                                                                    key={star}
                                                                    onClick={() => setFeedbackRating(star)}
                                                                    className={`transition-colors ${feedbackRating >= star ? 'text-yellow-500' : 'text-gray-300'}`}
                                                                >
                                                                    <Icons.Star filled={feedbackRating >= star} />
                                                                </button>
                                                            ))}
                                                        </div>
                                                        <textarea
                                                            value={feedbackCorrection}
                                                            onChange={(e) => setFeedbackCorrection(e.target.value)}
                                                            placeholder="Optional: Provide correction or feedback..."
                                                            className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-600 focus:border-transparent resize-none"
                                                            rows="3"
                                                        />
                                                        <div className="flex gap-2 mt-3">
                                                            <button
                                                                onClick={() => handleFeedback(message.id, feedbackRating)}
                                                                disabled={feedbackRating === 0}
                                                                className="px-4 py-2 text-sm bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
                                                            >
                                                                Submit Feedback
                                                            </button>
                                                            <button
                                                                onClick={() => {
                                                                    setShowFeedback(null);
                                                                    setFeedbackRating(0);
                                                                    setFeedbackCorrection('');
                                                                }}
                                                                className="px-4 py-2 text-sm text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                                                            >
                                                                Cancel
                                                            </button>
                                                        </div>
                                                    </div>
                                                )}
                                            </div>
                                        </div>
                                    ) : (
                                        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                                            <p className="text-sm text-red-800">{message.content}</p>
                                        </div>
                                    )}
                                </div>
                            ))}
                            {loading && (
                                <div className="flex gap-4">
                                    <div className="w-8 h-8 rounded-full bg-indigo-600 text-white flex items-center justify-center flex-shrink-0">
                                        <span className="text-lg">∑</span>
                                    </div>
                                    <div className="flex-1 pt-2">
                                        <div className="flex gap-1">
                                            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                                            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                                            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                                        </div>
                                    </div>
                                </div>
                            )}
                            <div ref={messagesEndRef} />
                        </div>
                    )}
                </div>

                <div className="border-t border-gray-200 bg-white px-4 py-4">
                    <div className="max-w-3xl mx-auto">
                        <form onSubmit={handleSubmit} className="flex gap-3">
                            <input
                                type="text"
                                value={inputValue}
                                onChange={(e) => setInputValue(e.target.value)}
                                placeholder="What's your math question?"
                                className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-600 focus:border-transparent outline-none"
                                disabled={loading}
                            />
                            <button
                                type="submit"
                                disabled={!inputValue.trim() || loading}
                                className="px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
                            >
                                <Icons.Send />
                                <span>Send</span>
                            </button>
                        </form>
                        <p className="text-xs text-gray-500 text-center mt-3">
                            Math A.I+ can make mistakes. Verify important information.
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default MathAgentApp;
