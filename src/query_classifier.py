from typing import Literal
import os
from dotenv import load_dotenv
from openai import OpenAI


class QueryClassifier:
    """查询分类器，将用户问题分类为不同的教学类型"""
    
    def __init__(self, model_name: str = "deepseek-chat"):
        load_dotenv()
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            raise ValueError("DEEPSEEK_API_KEY not found in environment variables")
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com"
        )
        self.model_name = model_name
    
    def classify(self, query: str) -> Literal["concept", "calculation", "experiment", "other"]:
        """
        对用户查询进行分类
        
        Args:
            query: 用户输入的问题
            
        Returns:
            分类结果：
            - "concept": 概念诊断型
            - "calculation": 计算分析型  
            - "experiment": 实验应用型
            - "other": 其他类型（与中学物理摩擦力知识无关）
        """
        
        classification_prompt = f"""
        ## 任务说明
        请将下面的物理问题分类到以下四个类别之一，只需要返回类别名称：

        ### 分类标准：

        **概念诊断型 (concept)**：
        - 询问中学物理摩擦力相关概念的定义、特征、本质
        - 询问摩擦力物理现象的原理、机制
        - 包含摩擦力概念混淆或理解错误
        - 询问"什么是..."、"为什么..."、"原理是..."
        - 例子：什么是摩擦力？为什么会产生摩擦？静摩擦和滑动摩擦有什么区别？

        **计算分析型 (calculation)**：
        - 涉及摩擦力相关的具体数值计算
        - 求解摩擦力的大小、方向
        - 分析物体在摩擦作用下的运动状态
        - 包含"求"、"计算"、"多大"、"多少"等关键词
        - 给出具体的物理条件和参数
        - 例子：一个10kg的物体在水平面上滑动，摩擦系数是0.3，求摩擦力大小？

        **实验应用型 (experiment)**：
        - 询问摩擦力相关实验设计、实验步骤、实验现象
        - 询问摩擦力在生活中的应用实例
        - 询问如何验证摩擦力相关的物理规律
        - 包含"实验"、"如何测量"、"生活中"、"应用"等关键词
        - 例子：如何用实验测量摩擦系数？生活中摩擦力的应用有哪些？

        **其他类型 (other)**：
        - 与中学物理摩擦力知识无关的问题
        - 涉及其他物理知识（如电学、光学、热学等）
        - 非物理学科问题（如数学、化学、语文、历史等）
        - 日常生活问题、聊天内容
        - 例子：什么是电流？光的折射定律是什么？今天天气如何？你是谁？

        ### 待分类问题：
        {query}

        ### 输出要求：
        只返回以下四个词中的一个：concept、calculation、experiment、other
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that classifies physics questions. Return only one of: concept, calculation, experiment, other"},
                    {"role": "user", "content": classification_prompt}
                ],
                stream=False
            )
            
            result = response.choices[0].message.content.strip().lower()
            
            # 确保返回值是有效的分类
            if result in ["concept", "calculation", "experiment", "other"]:
                return result
            else:
                # 默认分类为其他类型
                return "other"
                
        except Exception as e:
            print(f"分类出错: {e}")
            # 出错时默认为其他类型
            return "other"
