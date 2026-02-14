// DOM 元素
const chatMessages = document.getElementById('chatMessages');
const questionInput = document.getElementById('questionInput');
const inputForm = document.getElementById('inputForm');
const loadingOverlay = document.getElementById('loadingOverlay');
const welcomeSection = document.querySelector('.welcome-section');
const sidebar = document.getElementById('sidebar');
const conversationsList = document.getElementById('conversationsList');

// 应用状态
let isLoading = false;
let messageHistory = [];
let hasStartedConversation = false;
let currentConversationId = null;
let conversations = [];

// 初始化
document.addEventListener('DOMContentLoaded', function() {
    // 焦点到输入框
    questionInput.focus();
    
    // 延迟初始化输入框高度，确保DOM完全渲染
    setTimeout(() => {
        autoResizeTextarea();
    }, 100);
    
    // 监听输入变化
    questionInput.addEventListener('input', handleInputChange);
    
    // 监听表单提交
    inputForm.addEventListener('submit', handleFormSubmit);
    
    // 监听回车键
    questionInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleFormSubmit(e);
        }
    });
    
    // 加载对话列表
    loadConversationsList();
    
    // 初始化系统状态
    updateSystemStatus();
});

// 处理输入变化
function handleInputChange() {
    // 自动调整输入框高度
    autoResizeTextarea();
}

// 自动调整输入框高度
function autoResizeTextarea() {
    if (!questionInput) return;
    
    // 重置高度为auto以获取真实的scrollHeight
    questionInput.style.height = 'auto';
    
    // 获取内容的实际高度
    let scrollHeight = questionInput.scrollHeight;
    
    // 确保最小高度为40px，最大高度为200px
    let newHeight = Math.max(40, Math.min(scrollHeight, 200));
    
    // 设置新高度
    questionInput.style.height = newHeight + 'px';
}

// 处理表单提交
async function handleFormSubmit(e) {
    e.preventDefault();
    
    const question = questionInput.value.trim();
    if (!question || isLoading) return;
    
    // 如果这是第一次对话，创建新对话或使用现有对话
    if (!hasStartedConversation) {
        if (!currentConversationId) {
            // 创建新对话
            const newTitle = `对话 ${new Date().toLocaleString('zh-CN')}`;
            await fetch('/api/conversations', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ title: newTitle, messages: [] })
            })
            .then(response => response.json())
            .then(data => {
                currentConversationId = data._id;
                loadConversationsList();
            })
            .catch(error => console.error('Failed to create conversation:', error));
        }
        
        hideWelcomeSection();
        hasStartedConversation = true;
    }
    
    // 添加用户消息
    addMessage('user', question);
    
    // 清空输入框
    questionInput.value = '';
    handleInputChange();
    
    // 显示加载状态 - 在聊天区域显示加载指示器
    const loadingMessageId = showLoadingMessage();
    
    try {
        // 模拟API调用 - 在实际应用中这里会调用后端API
        const response = await simulateAPICall(question);
        
        // 移除加载消息，添加机器人回复
        removeLoadingMessage(loadingMessageId);
        addMessage('bot', response);
        
    } catch (error) {
        console.error('Error:', error);
        removeLoadingMessage(loadingMessageId);
        addMessage('bot', '抱歉，处理您的问题时出现了错误。请稍后再试。');
    } finally {
        questionInput.focus();
    }
}

// 添加消息
function addMessage(sender, text) {
    const messageId = `msg-${Date.now()}`;
    
    // 如果是机器人消息，移除所有之前消息的重新生成按钮
    if (sender === 'bot') {
        removeAllRegenerateButtons();
    }
    
    const messageElement = createMessageElement(sender, text, messageId, sender === 'bot');
    chatMessages.appendChild(messageElement);
    
    // 滚动到底部
    scrollToBottom();
    
    // 保存到历史记录
    const message = {
        id: messageId,
        sender,
        text,
        timestamp: new Date().toISOString()
    };
    
    messageHistory.push(message);
    saveMessageHistory();
    
    return messageId;
}

// 创建消息元素
function createMessageElement(sender, text, messageId = null, isLatest = false) {
    const isUser = sender === 'user';
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isUser ? 'user-message' : 'bot-message'}`;
    if (messageId) {
        messageDiv.id = messageId;
    }
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    const textDiv = document.createElement('div');
    textDiv.className = 'message-text';
    
    // 处理文本格式化
    textDiv.innerHTML = formatMessage(text);
    
    contentDiv.appendChild(textDiv);
    
    // 为最新的机器人消息添加重新生成按钮
    if (!isUser && isLatest) {
        const actionDiv = document.createElement('div');
        actionDiv.className = 'message-actions';
        
        const regenerateBtn = document.createElement('button');
        regenerateBtn.className = 'regenerate-btn';
        regenerateBtn.innerHTML = '<i class="fas fa-redo"></i>';
        regenerateBtn.title = 'Regenerate response';
        regenerateBtn.onclick = (e) => {
            e.preventDefault();
            regenerateResponse(messageId);
        };
        
        actionDiv.appendChild(regenerateBtn);
        contentDiv.appendChild(actionDiv);
    }
    
    messageDiv.appendChild(contentDiv);
    
    return messageDiv;
}

// 格式化消息文本
function formatMessage(text) {
    // 简单的格式化：换行、粗体、链接等
    return text
        .replace(/\n/g, '<br>')
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/(https?:\/\/[^\s]+)/g, '<a href="$1" target="_blank" rel="noopener">$1</a>');
}

// 格式化时间
function formatTime(date) {
    return date.toLocaleTimeString('zh-CN', {
        hour: '2-digit',
        minute: '2-digit'
    });
}

// 滚动到底部
function scrollToBottom() {
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// 显示加载消息（在聊天区域中）
function showLoadingMessage() {
    const loadingId = `loading-${Date.now()}`;
    const messageDiv = document.createElement('div');
    messageDiv.id = loadingId;
    messageDiv.className = 'message bot-message';
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    const textDiv = document.createElement('div');
    textDiv.className = 'message-text loading-text';
    textDiv.innerHTML = `
        <div class="loading-dots">
            <span></span>
            <span></span>
            <span></span>
        </div>
    `;
    
    contentDiv.appendChild(textDiv);
    messageDiv.appendChild(contentDiv);
    chatMessages.appendChild(messageDiv);
    
    scrollToBottom();
    return loadingId;
}

// 移除加载消息
function removeLoadingMessage(loadingId) {
    const loadingElement = document.getElementById(loadingId);
    if (loadingElement) {
        loadingElement.remove();
    }
}

// 移除所有重新生成按钮
function removeAllRegenerateButtons() {
    const allActionDivs = chatMessages.querySelectorAll('.message-actions');
    allActionDivs.forEach(actionDiv => {
        actionDiv.remove();
    });
}

// 重新生成响应
async function regenerateResponse(messageId) {
    // 找到要重新生成的消息所对应的最后一条用户消息
    const messageIndex = messageHistory.findIndex(msg => msg.id === messageId);
    
    if (messageIndex === -1) return;
    
    // 查找前面最近的用户消息
    let userMessageIndex = messageIndex - 1;
    while (userMessageIndex >= 0 && messageHistory[userMessageIndex].sender !== 'user') {
        userMessageIndex--;
    }
    
    if (userMessageIndex < 0) return;
    
    const userQuestion = messageHistory[userMessageIndex].text;
    
    // 移除旧的机器人回复
    const messageElement = document.getElementById(messageId);
    if (messageElement) {
        messageElement.remove();
    }
    
    // 从历史记录中移除旧的机器人消息
    messageHistory = messageHistory.filter(msg => msg.id !== messageId);
    
    // 显示加载状态
    const loadingMessageId = showLoadingMessage();
    
    try {
        // 调用API获取新的回复
        const response = await simulateAPICall(userQuestion);
        
        // 移除加载消息，添加新的机器人回复
        removeLoadingMessage(loadingMessageId);
        addMessage('bot', response);
        
    } catch (error) {
        console.error('Error:', error);
        removeLoadingMessage(loadingMessageId);
        addMessage('bot', '抱歉，重新生成回复时出现了错误。请稍后再试。');
    }
}

// 设置加载状态
function setLoading(loading) {
    isLoading = loading;
    loadingOverlay.style.display = loading ? 'flex' : 'none';
    
    if (loading) {
        document.body.style.overflow = 'hidden';
    } else {
        document.body.style.overflow = '';
    }
}

// 模拟API调用
async function simulateAPICall(question) {
    try {
        // 调用后端API
        const response = await fetch('/api/ask', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ question: question })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.success) {
            return data.answer;
        } else {
            throw new Error(data.error || '服务器返回错误');
        }
        
    } catch (error) {
        console.error('API调用失败:', error);
        
        // 如果API调用失败，回退到本地模拟
        return await simulateLocalResponse(question);
    }
}

// 本地模拟响应（备用方案）
async function simulateLocalResponse(question) {
    // 模拟网络延迟
    await new Promise(resolve => setTimeout(resolve, 1000 + Math.random() * 2000));
    
    // 模拟不同类型的回答
    const responses = {
        '摩擦力': '滑动摩擦力是物体相对滑动时产生的阻碍相对运动的力。它的大小与接触面间的正压力成正比，方向与物体相对运动方向相反。\n\n**计算公式：** f = μN\n其中：\n- f 是滑动摩擦力\n- μ 是滑动摩擦系数\n- N 是正压力\n\n**特点：**\n- 方向与相对运动方向相反\n- 大小与相对运动速度无关\n- 与接触面的性质和粗糙程度有关',
        
        '牛顿第一定律': '牛顿第一定律，也称为**惯性定律**，表述为：任何物体在没有外力作用或合外力为零的情况下，都会保持静止状态或匀速直线运动状态。\n\n**要点：**\n1. 物体具有保持原有运动状态的性质，这种性质称为惯性\n2. 力不是维持物体运动的原因，而是改变物体运动状态的原因\n3. 该定律描述了物体的惯性，为后续牛顿定律奠定了基础',
        
        '加速度': '物体的加速度可以通过以下公式计算：\n\n**基本公式：**\na = (v₂ - v₁) / t\n\n其中：\n- a 是加速度（m/s²）\n- v₁ 是初始速度（m/s）\n- v₂ 是末速度（m/s）\n- t 是时间间隔（s）\n\n**根据牛顿第二定律：**\na = F / m\n\n其中：\n- F 是合外力（N）\n- m 是物体质量（kg）\n\n加速度的方向与合外力的方向相同。',
        
        '动能势能': '**动能**和**势能**是机械能的两种基本形式：\n\n**动能（Kinetic Energy）：**\n- 定义：物体由于运动而具有的能量\n- 公式：Ek = ½mv²\n- 单位：焦耳(J)\n- 标量，只有大小没有方向\n\n**势能（Potential Energy）：**\n- 定义：物体由于位置或状态而具有的能量\n- 重力势能：Ep = mgh\n- 弹性势能：Ep = ½kx²\n\n**机械能守恒定律：**\n在只有重力或弹力做功的情况下，物体的动能与势能之和保持不变。'
    };
    
    // 查找匹配的关键词
    for (const [keyword, response] of Object.entries(responses)) {
        if (question.includes(keyword)) {
            return response;
        }
    }
    
    // 默认回复
    const defaultResponses = [
        `关于"${question}"这个问题，这是一个很好的学习问题。根据我的知识库，我建议您查阅相关的教材章节，或者提供更具体的问题描述，这样我能给出更准确的答案。`,
        
        `您提到了"${question}"，这涉及到重要的学科知识。为了给您提供更精确的回答，建议您：\n\n1. 明确问题的具体方面\n2. 提供相关的背景信息\n3. 说明您希望了解的深度\n\n这样我就能为您提供更有针对性的帮助。`,
        
        `感谢您的提问："${question}"。基于RAG技术，我正在从知识库中检索相关信息。目前我找到了一些相关内容，但为了给您最准确的答案，建议您将问题表述得更加具体一些。`
    ];
    
    return defaultResponses[Math.floor(Math.random() * defaultResponses.length)];
}

// 示例问题点击
function askQuestion(question) {
    questionInput.value = question;
    questionInput.focus();
    handleInputChange();
}

// 清除聊天记录
function clearChat() {
    if (confirm('确定要清除当前对话吗？')) {
        startNewConversation();
    }
}
// 显示欢迎信息
function showWelcomeSection() {
    if (welcomeSection) {
        welcomeSection.style.display = 'block';
        welcomeSection.style.opacity = '0';
        welcomeSection.style.transform = 'translateY(20px)';
        
        // 添加动画效果
        setTimeout(() => {
            welcomeSection.style.transition = 'all 0.3s ease-out';
            welcomeSection.style.opacity = '1';
            welcomeSection.style.transform = 'translateY(0)';
        }, 50);
    }
    
    // 重置chat-area的class，从has-messages切换回no-messages
    const chatArea = document.querySelector('.chat-area');
    if (chatArea) {
        chatArea.classList.remove('has-messages');
        chatArea.classList.add('no-messages');
    }
}

// 隐藏欢迎信息
function hideWelcomeSection() {
    if (welcomeSection) {
        welcomeSection.style.transition = 'all 0.3s ease-out';
        welcomeSection.style.opacity = '0';
        welcomeSection.style.transform = 'translateY(-20px)';
        
        setTimeout(() => {
            welcomeSection.style.display = 'none';
        }, 300);
    }
    
    // 更新chat-area的class，从no-messages切换到has-messages
    const chatArea = document.querySelector('.chat-area');
    if (chatArea) {
        chatArea.classList.remove('no-messages');
        chatArea.classList.add('has-messages');
    }
}

// 保存消息历史
// 保存对话到服务器
function saveConversationToServer() {
    if (!currentConversationId) {
        return;
    }
    
    fetch(`/api/conversations/${currentConversationId}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            messages: messageHistory,
            updated_at: new Date().toISOString()
        })
    }).catch(error => {
        console.error('Failed to save conversation:', error);
    });
}

// 加载对话列表
function loadConversationsList() {
    fetch('/api/conversations')
        .then(response => response.json())
        .then(data => {
            conversations = data.conversations || [];
            renderConversationsList();
        })
        .catch(error => {
            console.error('Failed to load conversations:', error);
        });
}

// 渲染对话列表
function renderConversationsList() {
    conversationsList.innerHTML = '';
    
    conversations.forEach(conv => {
        const item = document.createElement('div');
        item.className = `conversation-item ${conv._id === currentConversationId ? 'active' : ''}`;
        
        const title = document.createElement('span');
        title.textContent = conv.title || '未命名对话';
        title.style.flex = '1';
        title.style.cursor = 'pointer';
        title.onclick = () => loadConversation(conv._id);
        
        const deleteBtn = document.createElement('button');
        deleteBtn.className = 'conversation-item-delete';
        deleteBtn.innerHTML = '<i class="fas fa-trash"></i>';
        deleteBtn.onclick = (e) => {
            e.stopPropagation();
            deleteConversation(conv._id);
        };
        
        item.appendChild(title);
        item.appendChild(deleteBtn);
        conversationsList.appendChild(item);
    });
}

// 加载指定对话
function loadConversation(conversationId) {
    fetch(`/api/conversations/${conversationId}`)
        .then(response => response.json())
        .then(data => {
            currentConversationId = conversationId;
            messageHistory = data.messages || [];
            chatMessages.innerHTML = '';
            
            if (messageHistory.length > 0) {
                // 找到最后一条机器人消息的索引
                let lastBotMessageIndex = -1;
                for (let i = messageHistory.length - 1; i >= 0; i--) {
                    if (messageHistory[i].sender === 'bot') {
                        lastBotMessageIndex = i;
                        break;
                    }
                }
                
                messageHistory.forEach((message, index) => {
                    const isLatestBot = message.sender === 'bot' && index === lastBotMessageIndex;
                    const messageElement = createMessageElement(message.sender, message.text, message.id, isLatestBot);
                    chatMessages.appendChild(messageElement);
                });
                hideWelcomeSection();
                hasStartedConversation = true;
                scrollToBottom();
            } else {
                showWelcomeSection();
                hasStartedConversation = false;
            }
            
            renderConversationsList();
        })
        .catch(error => {
            console.error('Failed to load conversation:', error);
        });
}

// 删除对话
function deleteConversation(conversationId) {
    if (!confirm('确定要删除这个对话吗？')) {
        return;
    }
    
    fetch(`/api/conversations/${conversationId}`, {
        method: 'DELETE'
    })
    .then(response => {
        if (response.ok) {
            if (currentConversationId === conversationId) {
                startNewConversation();
            } else {
                loadConversationsList();
            }
        }
    })
    .catch(error => {
        console.error('Failed to delete conversation:', error);
    });
}

// 开始新对话
function startNewConversation() {
    // 保存当前对话
    if (currentConversationId) {
        saveConversationToServer();
    }
    
    // 创建新对话
    fetch('/api/conversations', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            title: `新对话 ${new Date().toLocaleString('zh-CN')}`,
            messages: []
        })
    })
    .then(response => response.json())
    .then(data => {
        currentConversationId = data._id;
        messageHistory = [];
        chatMessages.innerHTML = '';
        showWelcomeSection();
        hasStartedConversation = false;
        questionInput.value = '';
        questionInput.focus();
        loadConversationsList();
    })
    .catch(error => {
        console.error('Failed to create conversation:', error);
    });
}

// 侧边栏切换
function toggleSidebar() {
    sidebar.classList.toggle('collapsed');
}

function saveMessageHistory() {
    // MongoDB 版本：保存到服务器
    saveConversationToServer();
}

// 加载消息历史
function loadMessageHistory() {
    // MongoDB 版本：从服务器加载
    loadConversationsList();
}

// 更新系统状态
async function updateSystemStatus() {
    // 系统状态检查（可选，用于后台监控）
    try {
        const response = await fetch('/api/status');
        if (response.ok) {
            const data = await response.json();
            console.log('系统状态:', data.system_status);
            console.log('运行模式:', data.mode);
        }
    } catch (error) {
        console.log('系统状态检查失败，使用本地模式');
    }
}

// 工具函数：防抖
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// 工具函数：节流
function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// 监听窗口大小变化
window.addEventListener('resize', debounce(() => {
    // 重新计算聊天容器高度
    scrollToBottom();
}, 250));

// 监听在线状态
window.addEventListener('online', () => {
    updateSystemStatus();
});

window.addEventListener('offline', () => {
    const systemStatus = document.getElementById('systemStatus');
    if (systemStatus) {
        systemStatus.innerHTML = '<i class="fas fa-circle" style="color: #ef4444;"></i> 离线';
    }
});

// 键盘快捷键
document.addEventListener('keydown', (e) => {
    // Ctrl/Cmd + K 快速聚焦到输入框
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        questionInput.focus();
        questionInput.select();
    }
    
    // Esc 键清除输入
    if (e.key === 'Escape' && document.activeElement === questionInput) {
        questionInput.value = '';
        handleInputChange();
    }
});

// 暴露全局函数（为了HTML中的onclick能够访问）
window.askQuestion = askQuestion;
window.clearChat = clearChat;

// 导出模块（如果使用模块系统）
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        askQuestion,
        clearChat,
        addMessage,
        setLoading
    };
}
