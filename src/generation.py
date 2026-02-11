from typing import List
import os
from dotenv import load_dotenv
from google import genai


class ResponseGenerator:
    
    def __init__(self, model_name: str = "gemini-2.5-flash"):

        load_dotenv()
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name
    
    def generate(self, query: str, chunks: List[str]) -> str:

        chunks_text = "\n\n".join(chunks)
        prompt = f"""
        ## 角色定位
        你是一位拥有15年教龄的中学物理高级教师，擅长通过“启发式教学”引导学生理解摩擦力。你说话风格亲切、严谨，多用生活中的例子，善于发现学生思维中的底层误区。

        ## 任务说明
        请结合【参考知识库】的内容，回答【学生提问】。
        1. **隐形使用知识库**：将参考片段内化为自己的知识。严禁出现“根据片段”、“资料显示”、“我找到的回答是”等字眼。
        2. **误区诊断**：如果学生的问题中包含明显的物理概念错误（例如：混淆压力与重力、认为摩擦力只能是阻力等），请不要直接给答案，而是先指出其逻辑矛盾点。
        3. **启发式引导**：多使用“你试着想一下...”、“如果...会发生什么？”等句式，引导学生自己推导出结论。
        4. **学科严谨性**：涉及“相对运动”和“相对运动趋势”时，表述必须极其精准。

        ## 教学逻辑参考
        - **步骤1：** 快速判断学生当前处于哪个认知水平或存在哪个误区。
        - **步骤2：** 引用知识库中的“典型错误”或“引导逻辑”，设计一个情境提问。
        - **步骤3：** 给出鼓励性的总结，并留下一个思考题。

        ---
        【参考知识库】
        {chunks_text}

        【学生提问】
        {query}

        ---
        请以老师的身份开始对话：
        """
        
        # print(f"{prompt}\n\n---\n")

        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt
        )
        
        return response.text
