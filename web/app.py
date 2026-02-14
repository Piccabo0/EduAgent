from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import os
import sys
import json
import logging
from datetime import datetime
from dotenv import load_dotenv
import uuid

# 加载环境变量
load_dotenv()
HF_TOKEN = os.getenv("HF_TOKEN")
if HF_TOKEN:
    os.environ["HF_TOKEN"] = HF_TOKEN
else:
    print("⚠ Warning: HF_TOKEN not found in environment variables")

# 添加src目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from chunking import split_into_chunks
    from indexing import VectorIndexer
    from retrieval import Retriever
    from reranking import Reranker
    from generation import ResponseGenerator
except ImportError as e:
    print(f"Warning: Could not import EduAgent modules: {e}")
    print("Running in demo mode...")

app = Flask(__name__, 
           static_folder='.',
           static_url_path='',
           template_folder='.')
CORS(app)

# 初始化临时文件夹
try:
    # 创建 temp 文件夹
    workspace_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    TEMP_DIR = os.path.join(workspace_root, 'temp')
    os.makedirs(TEMP_DIR, exist_ok=True)
    print(f"✓ Temp directory created/verified: {TEMP_DIR}")
        
except Exception as e:
    print(f"⚠ Warning: Error during initialization: {e}")
    TEMP_DIR = None

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ===== 会话存储管理器 =====
class ConversationManager:
    """管理对话的存储和检索"""
    
    @staticmethod
    def _get_session_filename(session_id):
        """生成会话文件名"""
        return f"Session_{session_id}.json"
    
    @staticmethod
    def _get_session_filepath(session_id):
        """获取会话文件完整路径"""
        return os.path.join(TEMP_DIR, ConversationManager._get_session_filename(session_id))
    
    @staticmethod
    def save_conversation(session_id, conversation_data):
        """保存对话到本地文件"""
        try:
            filepath = ConversationManager._get_session_filepath(session_id)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(conversation_data, f, ensure_ascii=False, indent=2)
            logger.info(f"✓ Conversation saved to: {filepath}")
            return True
        except Exception as e:
            logger.error(f"Failed to save conversation: {e}")
            return False
    
    @staticmethod
    def load_conversation(session_id):
        """加载对话（从本地文件）"""
        # 从本地文件读取
        try:
            filepath = ConversationManager._get_session_filepath(session_id)
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                logger.info(f"Loaded conversation from file: {session_id}")
                return data
        except Exception as e:
            logger.error(f"Failed to load conversation: {e}")
        
        return None
    
    @staticmethod
    def list_conversations():
        """列出所有本地对话"""
        try:
            conversations = []
            if os.path.exists(TEMP_DIR):
                for filename in os.listdir(TEMP_DIR):
                    if filename.startswith('Session_') and filename.endswith('.json'):
                        filepath = os.path.join(TEMP_DIR, filename)
                        try:
                            with open(filepath, 'r', encoding='utf-8') as f:
                                data = json.load(f)
                                conversations.append({
                                    '_id': data.get('_id', filename.replace('Session_', '').replace('.json', '')),
                                    'title': data.get('title', '未命名对话'),
                                    'created_at': data.get('created_at'),
                                    'updated_at': data.get('updated_at'),
                                    'message_count': len(data.get('messages', []))
                                })
                        except Exception as e:
                            logger.warning(f"Failed to load conversation file {filename}: {e}")
            
            # 按更新时间排序
            conversations.sort(key=lambda x: x.get('updated_at', ''), reverse=True)
            return conversations
        except Exception as e:
            logger.error(f"Failed to list conversations: {e}")
            return []
    
    @staticmethod
    def delete_conversation(session_id):
        """删除对话"""
        try:
            # 删除本地文件
            filepath = ConversationManager._get_session_filepath(session_id)
            if os.path.exists(filepath):
                os.remove(filepath)
                logger.info(f"Deleted conversation file: {session_id}")
            
            return True
        except Exception as e:
            logger.error(f"Failed to delete conversation: {e}")
            return False

# 全局变量存储EduAgent组件
edu_agent = None
initialized = False

class EduAgentDemo:
    """演示模式的EduAgent"""
    
    def __init__(self):
        self.demo_responses = {
            "摩擦力": "滑动摩擦力是物体相对滑动时产生的阻碍相对运动的力。它的大小与接触面间的正压力成正比，方向与物体相对运动方向相反。\\n\\n**计算公式：** f = μN\\n其中：\\n- f 是滑动摩擦力\\n- μ 是滑动摩擦系数\\n- N 是正压力",
            
            "牛顿第一定律": "牛顿第一定律，也称为**惯性定律**，表述为：任何物体在没有外力作用或合外力为零的情况下，都会保持静止状态或匀速直线运动状态。\\n\\n**要点：**\\n1. 物体具有保持原有运动状态的性质，这种性质称为惯性\\n2. 力不是维持物体运动的原因，而是改变物体运动状态的原因",
            
            "加速度": "物体的加速度可以通过以下公式计算：\\n\\n**基本公式：**\\na = (v₂ - v₁) / t\\n\\n其中：\\n- a 是加速度（m/s²）\\n- v₁ 是初始速度（m/s）\\n- v₂ 是末速度（m/s）\\n- t 是时间间隔（s）",
            
            "动能势能": "**动能**和**势能**是机械能的两种基本形式：\\n\\n**动能（Kinetic Energy）：**\\n- 定义：物体由于运动而具有的能量\\n- 公式：Ek = ½mv²\\n\\n**势能（Potential Energy）：**\\n- 定义：物体由于位置或状态而具有的能量\\n- 重力势能：Ep = mgh"
        }
    
    def answer_question(self, question):
        """演示模式回答问题"""
        for keyword, response in self.demo_responses.items():
            if keyword in question:
                return response
        
        return f"感谢您的提问：\"{question}\"。这是一个很好的学习问题。在实际部署中，EduAgent会通过RAG技术从知识库中检索相关信息并生成准确的答案。目前演示模式下，请尝试询问关于摩擦力、牛顿第一定律、加速度或动能势能的问题。"

class EduAgentWrapper:
    """EduAgent包装器"""
    
    def __init__(self):
        self.retriever = None
        self.reranker = None
        self.generator = None
        self._initialize()
    
    def _initialize(self):
        """初始化EduAgent组件"""
        try:
            logger.info("初始化EduAgent组件...")
            
            # 设置路径
            current_dir = os.path.dirname(os.path.abspath(__file__))
            src_dir = os.path.join(os.path.dirname(current_dir), 'src')
            data_dir = os.path.join(os.path.dirname(current_dir), 'data')
            doc_file = os.path.join(data_dir, 'doc.md')
            
            # 检查文档文件是否存在
            if not os.path.exists(doc_file):
                raise FileNotFoundError(f"Document file not found: {doc_file}")
            
            # 1. 分片
            chunks = split_into_chunks(doc_file)
            logger.info(f"文档分片完成，共 {len(chunks)} 个片段")
            
            # 2. 索引
            indexer = VectorIndexer()
            indexer.build_index(chunks)
            logger.info("向量索引构建完成")
            
            # 3. 初始化组件
            self.retriever = Retriever(indexer)
            self.reranker = Reranker()
            self.generator = ResponseGenerator()
            
            logger.info("EduAgent初始化成功")
            
        except Exception as e:
            logger.error(f"EduAgent初始化失败: {e}")
            raise
    
    def answer_question(self, question, top_k_retrieve=5, top_k_rerank=3):
        """回答问题"""
        try:
            # 召回
            retrieved_chunks = self.retriever.retrieve(question, top_k=top_k_retrieve)
            logger.info(f"检索到 {len(retrieved_chunks)} 个相关片段")
            
            # 重排
            reranked_chunks = self.reranker.rerank(question, retrieved_chunks, top_k=top_k_rerank)
            logger.info(f"重排后保留 {len(reranked_chunks)} 个片段")
            
            # 生成回答
            if reranked_chunks:
                answer = self.generator.generate(question, reranked_chunks[0])
            else:
                answer = "抱歉，没有找到相关信息来回答您的问题。"
            
            return answer
            
        except Exception as e:
            logger.error(f"回答问题时出错: {e}")
            return f"处理问题时出现错误: {str(e)}"

def initialize_edu_agent():
    """初始化EduAgent"""
    global edu_agent, initialized
    
    if initialized:
        return
    
    try:
        # 尝试初始化真正的EduAgent
        edu_agent = EduAgentWrapper()
        logger.info("EduAgent初始化成功")
    except Exception as e:
        logger.warning(f"无法初始化EduAgent，使用演示模式: {e}")
        edu_agent = EduAgentDemo()
    
    initialized = True

@app.route('/')
def index():
    """主页"""
    return render_template('index.html')

@app.route('/api/ask', methods=['POST'])
def ask_question():
    """处理问题API"""
    try:
        data = request.get_json()
        
        if not data or 'question' not in data:
            return jsonify({
                'success': False,
                'error': '缺少问题参数'
            }), 400
        
        question = data['question'].strip()
        
        if not question:
            return jsonify({
                'success': False,
                'error': '问题不能为空'
            }), 400
        
        # 确保EduAgent已初始化
        if not initialized:
            initialize_edu_agent()
        
        # 获取回答
        answer = edu_agent.answer_question(question)
        
        # 返回结果
        response = {
            'success': True,
            'answer': answer,
            'timestamp': datetime.now().isoformat(),
            'question': question
        }
        
        logger.info(f"问题: {question[:50]}... | 回答长度: {len(answer)}")
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"处理问题API时出错: {e}")
        return jsonify({
            'success': False,
            'error': f'服务器内部错误: {str(e)}'
        }), 500

@app.route('/api/status')
def get_status():
    """获取系统状态"""
    try:
        status = {
            'system_status': 'online',
            'initialized': initialized,
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0'
        }
        
        if initialized and isinstance(edu_agent, EduAgentWrapper):
            status['mode'] = 'production'
            status['knowledge_base'] = 'loaded'
        else:
            status['mode'] = 'demo'
            status['knowledge_base'] = 'demo_data'
        
        return jsonify(status)
        
    except Exception as e:
        logger.error(f"获取状态时出错: {e}")
        return jsonify({
            'system_status': 'error',
            'error': str(e)
        }), 500

@app.route('/api/health')
def health_check():
    """健康检查"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/conversations', methods=['GET'])
def get_conversations():
    """获取所有对话列表"""
    try:
        conversations = ConversationManager.list_conversations()
        return jsonify({'conversations': conversations}), 200
    except Exception as e:
        logger.error(f"获取对话列表出错: {e}")
        return jsonify({'conversations': []}), 200

@app.route('/api/conversations/<conversation_id>', methods=['GET'])
def get_conversation(conversation_id):
    """获取指定对话的详细信息"""
    try:
        conversation = ConversationManager.load_conversation(conversation_id)
        
        if not conversation:
            return jsonify({'error': '对话不存在'}), 404
        
        return jsonify(conversation), 200
    except Exception as e:
        logger.error(f"获取对话出错: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/conversations', methods=['POST'])
def create_conversation():
    """创建新对话"""
    try:
        data = request.json or {}
        session_id = str(uuid.uuid4())
        conversation = {
            '_id': session_id,
            'title': data.get('title', f'新对话 {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'),
            'messages': data.get('messages', []),
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        # 保存对话
        ConversationManager.save_conversation(session_id, conversation)
        
        return jsonify(conversation), 201
    except Exception as e:
        logger.error(f"创建对话出错: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/conversations/<conversation_id>', methods=['PUT'])
def update_conversation(conversation_id):
    """更新对话（添加消息或更新内容）"""
    try:
        data = request.json or {}
        
        # 加载现有对话
        conversation = ConversationManager.load_conversation(conversation_id)
        
        if not conversation:
            return jsonify({'error': '对话不存在'}), 404
        
        # 更新字段
        if 'messages' in data:
            conversation['messages'] = data['messages']
        if 'title' in data:
            conversation['title'] = data['title']
        
        conversation['updated_at'] = datetime.now().isoformat()
        
        # 保存更新
        ConversationManager.save_conversation(conversation_id, conversation)
        
        return jsonify({'success': True}), 200
    except Exception as e:
        logger.error(f"更新对话出错: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/conversations/<conversation_id>', methods=['DELETE'])
def delete_conversation(conversation_id):
    """删除对话"""
    try:
        success = ConversationManager.delete_conversation(conversation_id)
        
        if not success:
            return jsonify({'error': '对话不存在'}), 404
        
        return jsonify({'success': True}), 200
    except Exception as e:
        logger.error(f"删除对话出错: {e}")
        return jsonify({'error': str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': '页面未找到'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"内部服务器错误: {error}")
    return jsonify({
        'success': False,
        'error': '服务器内部错误'
    }), 500

if __name__ == '__main__':
    print("=" * 60)
    print("EduAgent Web Server Starting...")
    print("=" * 60)
    
    # 初始化EduAgent
    try:
        initialize_edu_agent()
        print(f"✓ EduAgent initialized successfully")
    except Exception as e:
        print(f"⚠ EduAgent initialization failed, using demo mode: {e}")
    
    print("\nServer will be available at:")
    print("  Local:   http://localhost:5000")
    print("  Network: http://0.0.0.0:5000")
    print("\nPress Ctrl+C to stop the server")
    print("=" * 60)
    
    # 启动服务器
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        threaded=True
    )
