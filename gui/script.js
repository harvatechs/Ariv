// Ariv GUI - Main JavaScript
class ArivChat {
    constructor() {
        this.messages = [];
        this.currentLanguage = 'hindi';
        this.isTyping = false;
        this.messageCount = 0;
        this.totalResponseTime = 0;
        this.settings = {
            enableCritic: true,
            enableDeepCoT: true,
            enableSelfConsistency: true,
            enableTools: false
        };
        
        this.initializeElements();
        this.bindEvents();
        this.loadPreferences();
    }

    initializeElements() {
        this.chatMessages = document.getElementById('chat-messages');
        this.messageInput = document.getElementById('message-input');
        this.sendButton = document.getElementById('send-button');
        this.typingIndicator = document.getElementById('typing-indicator');
        this.languageSelect = document.getElementById('language-select');
        this.toastContainer = document.getElementById('toast-container');
        
        // Settings checkboxes
        this.enableCriticCheckbox = document.getElementById('enable-critic');
        this.enableDeepCoTCheckbox = document.getElementById('enable-deep-cot');
        this.enableSelfConsistencyCheckbox = document.getElementById('enable-self-consistency');
        this.enableToolsCheckbox = document.getElementById('enable-tools');
        
        // Stats elements
        this.messageCountElement = document.getElementById('message-count');
        this.avgTimeElement = document.getElementById('avg-time');
        this.currentLangElement = document.getElementById('current-lang');
    }

    bindEvents() {
        // Send message events
        this.sendButton.addEventListener('click', () => this.sendMessage());
        this.messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        // Auto-resize textarea
        this.messageInput.addEventListener('input', () => {
            this.autoResizeTextarea();
        });
        
        // Language change
        this.languageSelect.addEventListener('change', (e) => {
            this.currentLanguage = e.target.value;
            this.updateStats();
            this.showToast(`Language changed to ${this.getLanguageName(this.currentLanguage)}`, 'info');
        });
        
        // Settings changes
        this.enableCriticCheckbox.addEventListener('change', (e) => {
            this.settings.enableCritic = e.target.checked;
            this.savePreferences();
        });
        
        this.enableDeepCoTCheckbox.addEventListener('change', (e) => {
            this.settings.enableDeepCoT = e.target.checked;
            this.savePreferences();
        });
        
        this.enableSelfConsistencyCheckbox.addEventListener('change', (e) => {
            this.settings.enableSelfConsistency = e.target.checked;
            this.savePreferences();
        });
        
        this.enableToolsCheckbox.addEventListener('change', (e) => {
            this.settings.enableTools = e.target.checked;
            this.savePreferences();
        });
        
        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            // Ctrl/Cmd + Enter to send
            if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
                this.sendMessage();
            }
            
            // Ctrl/Cmd + L to clear chat
            if ((e.ctrlKey || e.metaKey) && e.key === 'l') {
                e.preventDefault();
                this.clearChat();
            }
        });
    }

    getLanguageName(code) {
        const languages = {
            hindi: 'हिन्दी (Hindi)',
            tamil: 'தமிழ் (Tamil)',
            bengali: 'বাংলা (Bengali)',
            telugu: 'తెలుగు (Telugu)',
            marathi: 'मराठी (Marathi)',
            gujarati: 'ગુજરાતી (Gujarati)',
            kannada: 'ಕನ್ನಡ (Kannada)',
            malayalam: 'മലയാളം (Malayalam)',
            odia: 'ଓଡ଼ିଆ (Odia)',
            punjabi: 'ਪੰਜਾਬੀ (Punjabi)',
            english: 'English',
            hinglish: 'Hinglish'
        };
        return languages[code] || code;
    }

    autoResizeTextarea() {
        this.messageInput.style.height = 'auto';
        this.messageInput.style.height = Math.min(this.messageInput.scrollHeight, 120) + 'px';
    }

    async sendMessage() {
        const message = this.messageInput.value.trim();
        if (!message || this.isTyping) return;

        // Clear input
        this.messageInput.value = '';
        this.autoResizeTextarea();

        // Add user message
        this.addMessage(message, 'user');

        // Show typing indicator
        this.showTypingIndicator();

        // Simulate API call (replace with actual API call)
        try {
            const response = await this.callArivAPI(message);
            this.hideTypingIndicator();
            this.addMessage(response.answer, 'bot', response.metadata);
        } catch (error) {
            this.hideTypingIndicator();
            this.addMessage(`Sorry, I encountered an error: ${error.message}`, 'bot');
            this.showToast('Failed to get response', 'error');
        }
    }

    async callArivAPI(message) {
        // Simulate API delay
        await new Promise(resolve => setTimeout(resolve, 1500 + Math.random() * 1000));

        // Simulate different responses based on message content
        const responses = this.generateMockResponse(message);
        
        // Update statistics
        this.messageCount++;
        this.totalResponseTime += responses.time;
        this.updateStats();

        return {
            answer: responses.answer,
            metadata: responses.metadata
        };
    }

    generateMockResponse(message) {
        const lowerMessage = message.toLowerCase();
        const language = this.currentLanguage;

        // Mathematical problems
        if (lowerMessage.includes('add') || lowerMessage.includes('+') || lowerMessage.includes('plus')) {
            const numbers = this.extractNumbers(lowerMessage);
            if (numbers.length >= 2) {
                const sum = numbers.reduce((a, b) => a + b, 0);
                return {
                    answer: `The sum is ${sum}.`,
                    time: 2.1,
                    metadata: { usedCalculator: true }
                };
            }
        }

        if (lowerMessage.includes('multiply') || lowerMessage.includes('×') || lowerMessage.includes('*')) {
            const numbers = this.extractNumbers(lowerMessage);
            if (numbers.length >= 2) {
                const product = numbers.reduce((a, b) => a * b, 1);
                return {
                    answer: `The product is ${product}.`,
                    time: 2.3,
                    metadata: { usedCalculator: true }
                };
            }
        }

        // Language-specific responses
        const languageResponses = {
            hindi: {
                greeting: "नमस्ते! मैं Ariv हूं। आपकी कैसे मदद कर सकता हूं?",
                math: "मैं गणितीय समस्याओं को हल करने में मदद कर सकता हूं।",
                logic: "तर्कसंगत विश्लेषण मेरा एक मजबूत पक्ष है।"
            },
            tamil: {
                greeting: "வணக்கம்! நான் Ariv. உங்களுக்கு எப்படி உதவ முடியும்?",
                math: "நான் கணிதக் கணக்குகளில் உதவ முடியும்.",
                logic: "தர்க்கரீதியான பகுப்பாய்வு என் வலுவான பக்கம்."
            },
            english: {
                greeting: "Hello! I'm Ariv. How can I assist you today?",
                math: "I can help with mathematical calculations and reasoning.",
                logic: "Logical analysis and problem-solving are my strengths."
            }
        };

        // Check for greetings
        if (lowerMessage.includes('hello') || lowerMessage.includes('hi') || lowerMessage.includes('namaste') || lowerMessage.includes('வணக்கம்')) {
            return {
                answer: languageResponses[language]?.greeting || languageResponses.english.greeting,
                time: 1.5,
                metadata: { type: 'greeting' }
            };
        }

        // Check for math-related questions
        if (lowerMessage.includes('math') || lowerMessage.includes('calculate') || lowerMessage.includes('गणित') || lowerMessage.includes('கணிதம்')) {
            return {
                answer: languageResponses[language]?.math || languageResponses.english.math,
                time: 1.8,
                metadata: { type: 'math_info' }
            };
        }

        // Check for logic-related questions
        if (lowerMessage.includes('logic') || lowerMessage.includes('reasoning') || lowerMessage.includes('तर्क') || lowerMessage.includes('தர்க்கம்')) {
            return {
                answer: languageResponses[language]?.logic || languageResponses.english.logic,
                time: 2.0,
                metadata: { type: 'logic_info' }
            };
        }

        // Default response
        const defaultResponses = [
            "I understand your question. Let me think through this step by step...",
            "That's an interesting question! Here's my analysis...",
            "I'll help you with that. Let me break it down...",
            "Good question! Let me work through this systematically..."
        ];

        const randomResponse = defaultResponses[Math.floor(Math.random() * defaultResponses.length)];
        return {
            answer: randomResponse + "\n\nBased on my analysis, I can help you with this using advanced chain-of-thought reasoning with cultural context preservation.",
            time: 2.5 + Math.random(),
            metadata: { type: 'general', reasoning: 'chain-of-thought' }
        };
    }

    extractNumbers(text) {
        const matches = text.match(/\d+/g);
        return matches ? matches.map(Number) : [];
    }

    addMessage(text, sender, metadata = null) {
        const message = {
            id: Date.now(),
            text,
            sender,
            timestamp: new Date(),
            metadata
        };

        this.messages.push(message);
        this.renderMessage(message);
    }

    renderMessage(message) {
        const messageElement = document.createElement('div');
        messageElement.className = `message ${message.sender}-message`;
        
        const timeString = message.timestamp.toLocaleTimeString('en-US', { 
            hour: '2-digit', 
            minute: '2-digit' 
        });

        messageElement.innerHTML = `
            <div class="message-avatar">
                <i class="fas fa-${message.sender === 'bot' ? 'robot' : 'user'}"></i>
            </div>
            <div class="message-content">
                <div class="message-header">
                    <span class="message-author">${message.sender === 'bot' ? 'Ariv AI' : 'You'}</span>
                    <span class="message-time">${timeString}</span>
                </div>
                <div class="message-text">${this.formatMessage(message.text)}</div>
            </div>
        `;

        this.chatMessages.appendChild(messageElement);
        this.scrollToBottom();
    }

    formatMessage(text) {
        // Convert URLs to links
        text = text.replace(/(https?:\/\/[^\s]+)/g, '<a href="$1" target="_blank" rel="noopener">$1</a>');
        
        // Convert code blocks
        text = text.replace(/`([^`]+)`/g, '<code>$1</code>');
        
        // Convert newlines to <br>
        text = text.replace(/\n/g, '<br>');
        
        return text;
    }

    scrollToBottom() {
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }

    showTypingIndicator() {
        this.isTyping = true;
        this.typingIndicator.style.display = 'block';
        this.scrollToBottom();
    }

    hideTypingIndicator() {
        this.isTyping = false;
        this.typingIndicator.style.display = 'none';
    }

    clearChat() {
        if (confirm('Are you sure you want to clear the chat?')) {
            this.messages = [];
            this.chatMessages.innerHTML = '';
            this.messageCount = 0;
            this.totalResponseTime = 0;
            this.updateStats();
            this.showToast('Chat cleared', 'info');
        }
    }

    updateStats() {
        this.messageCountElement.textContent = this.messageCount;
        this.currentLangElement.textContent = this.getLanguageName(this.currentLanguage);
        
        const avgTime = this.messageCount > 0 ? (this.totalResponseTime / this.messageCount).toFixed(1) : 0;
        this.avgTimeElement.textContent = `${avgTime}s`;
    }

    showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.innerHTML = `
            <div class="toast-content">
                <i class="fas fa-${this.getToastIcon(type)}"></i>
                <span>${message}</span>
            </div>
        `;

        this.toastContainer.appendChild(toast);

        // Auto remove after 3 seconds
        setTimeout(() => {
            toast.style.animation = 'slideOut 0.3s ease-in-out';
            setTimeout(() => {
                if (toast.parentNode) {
                    toast.parentNode.removeChild(toast);
                }
            }, 300);
        }, 3000);
    }

    getToastIcon(type) {
        const icons = {
            success: 'check-circle',
            error: 'exclamation-circle',
            info: 'info-circle',
            warning: 'exclamation-triangle'
        };
        return icons[type] || 'info-circle';
    }

    savePreferences() {
        const preferences = {
            language: this.currentLanguage,
            settings: this.settings
        };
        localStorage.setItem('ariv-preferences', JSON.stringify(preferences));
    }

    loadPreferences() {
        try {
            const saved = localStorage.getItem('ariv-preferences');
            if (saved) {
                const preferences = JSON.parse(saved);
                this.currentLanguage = preferences.language || 'hindi';
                this.languageSelect.value = this.currentLanguage;
                
                if (preferences.settings) {
                    this.settings = { ...this.settings, ...preferences.settings };
                    this.enableCriticCheckbox.checked = this.settings.enableCritic;
                    this.enableDeepCoTCheckbox.checked = this.settings.enableDeepCoT;
                    this.enableSelfConsistencyCheckbox.checked = this.settings.enableSelfConsistency;
                    this.enableToolsCheckbox.checked = this.settings.enableTools;
                }
            }
        } catch (error) {
            console.error('Failed to load preferences:', error);
        }
    }

    // Export chat functionality
    exportChat() {
        const chatData = {
            timestamp: new Date().toISOString(),
            messages: this.messages,
            settings: this.settings,
            language: this.currentLanguage,
            stats: {
                messageCount: this.messageCount,
                avgResponseTime: this.messageCount > 0 ? this.totalResponseTime / this.messageCount : 0
            }
        };

        const blob = new Blob([JSON.stringify(chatData, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `ariv-chat-${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);

        this.showToast('Chat exported successfully', 'success');
    }
}

// Initialize the chat when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.arivChat = new ArivChat();
    
    // Add global keyboard shortcuts info
    console.log('Ariv Chat initialized. Keyboard shortcuts:');
    console.log('- Ctrl/Cmd + Enter: Send message');
    console.log('- Ctrl/Cmd + L: Clear chat');
});

// Service Worker for offline support (optional)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/sw.js')
            .then(registration => {
                console.log('SW registered: ', registration);
            })
            .catch(registrationError => {
                console.log('SW registration failed: ', registrationError);
            });
    });
}
