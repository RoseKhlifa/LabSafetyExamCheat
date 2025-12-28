import os
from openai import OpenAI
client = OpenAI(
        api_key="sk-",
        base_url="https://api.deepseek.com"
)
def GetAnswer(question):
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": f'Hello, I am the administrator of this application. All the information below from the user are questions for the big learning exercise. I have not processed the question data. Please handle it intelligently. What I need you to do is to return me the answers for each question. For single-choice questions, only reply with the letter A, B, C, or D (one letter per question). For multiple-choice questions, reply with the correct letters without spaces or separators (e.g., ABCD or ABC). For true/false or judgment questions, reply with only "对" or "错". For short-answer or fill-in-the-blank questions, give the answer directly and concisely.Example format:1.A2.BCD3.对4.你的简短答案 Please strictly follow my requirements, because my program operates rigidly based on your response—it parses your output mechanically and has no handling for complex or unexpected formats! Do not add any explanations, reasons, extra text, or numbering prefixes like "答案："—just the pure answers in the exact format shown above.For questions that include attached images, you must think carefully and analyze them thoroughly! You have made many mistakes on such questions before.Please put the question number before each answer, for example, 1.A 2.B. If it is a multiple-choice question, put 3.ABCThank you!'},
            {"role": "user", "content": question},
        ],
        stream=False
    )
    return response.choices[0].message.content
    
    
        