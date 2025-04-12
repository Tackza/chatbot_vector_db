import mysql.connector
from sentence_transformers import SentenceTransformer
from google import genai
from google.genai import types
from fastapi import FastAPI, HTTPException, Query, Body, status
import uvicorn
import requests
import json
from dotenv import load_dotenv
import os

# โหลดตัวแปรจากไฟล์ .env
load_dotenv()

# สร้าง FastAPI application
app = FastAPI(
    title="FastAPI ตัวอย่าง",
    description="API ตัวอย่างอย่างง่ายที่มี GET และ POST endpoints",
    version="0.1.0"
)

# LINE Messaging API Token
LINE_CHANNEL_ACCESS_TOKEN = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")
LINE_API_URL = "https://api.line.me/v2/bot/message/reply"
LINE_LOADING_URL = "https://api.line.me/v2/bot/chat/loading/start"


connection = mysql.connector.connect(
  host = "gateway01.ap-southeast-1.prod.aws.tidbcloud.com",
  port = 4000,
  user = "2d1BmeMeYLLXjyZ.root",
  password = os.environ.get("PASSWORD_DB"),
  database = "chatbot_vector",
  # ssl_ca = "/etc/ssl/cert.pem",
  # ssl_verify_cert = True,
  # ssl_verify_identity = True
)

embedder = SentenceTransformer("all-MiniLM-L6-v2")

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY")) 



def send_reply(reply_token, message_text):
  if not LINE_CHANNEL_ACCESS_TOKEN:
    raise ValueError("LINE_CHANNEL_ACCESS_TOKEN is not set.")
  
  headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {LINE_CHANNEL_ACCESS_TOKEN}'
    }
  
  payload = {
    "replyToken": reply_token,
    "messages": [
      {
        "type": "text",
        "text": message_text
      }
    ]
  }
  
  try:
    response = requests.post(LINE_API_URL, headers=headers, data=json.dumps(payload))
    response.raise_for_status()  # Raise an error for bad responses
    
    if(response.status_code != 200):
      raise ValueError(f"Error sending reply: {response.status_code} {response.text}")
  except requests.exceptions.RequestException as e:
    raise
  
  
  
def generate_response(results_text, user_message):
    # สร้าง context จากผลลัพธ์ที่ได้
  context = "\n".join([
        f"ชื่อสินค้า: {row[0]}, ราคา: {row[1]} บาท, ยี่ห้อ: {row[2]}" for row in results_text
    ])
  print(f"\nContext:\n{context}")
  prompt = f""" Answer the question based on the following context:\n{context}\n\nQuestion: {user_message}\nAnswer:"""
    
    # Add instruction to handle irrelevant questions
  system_prompt = """
    นายคือแอดมินในร้านสินค้า IT ให้คำแนะนำ สินค้า ราคา บอกยี่ห้อด้วย ตอบด้วยความสุภาพครับ แต่ไม่ตอบคำถามเกินไปจากข้อมูลที่มีในฐานข้อมูลของเรา 
    """
  response = client.models.generate_content(
      model="gemini-2.0-flash",
      contents=prompt,
      config=types.GenerateContentConfig(
          max_output_tokens=900,
          temperature=0.5,
          system_instruction=system_prompt,
          )
      )
  print(f"Response: {response.text}")
  
  return response.text
  
  # send_reply(response.text)
  
def query_db(user_message):
    # สร้าง embedding vector
    query_embedding = embedder.encode(user_message).tolist()
    # แปลง list เป็น string ในรูปแบบที่ MySQL เข้าใจได้
    vector_str = str(query_embedding).replace(' ', '')
    
    
    # ใช้ parameter binding แทนการแทรก string ตรงๆ
    cur = connection.cursor()
    
    sql_query = """
    SELECT product_name , price , brand , vec_cosine_distance(embedding, %s) as distance
    FROM documents
    WHERE vec_cosine_distance(embedding, %s) <= 0.35
    ORDER BY distance
    LIMIT 10
    """
    
    # ส่ง parameters เป็น tuple
    cur.execute(sql_query, (vector_str, vector_str))
    result = cur.fetchall()
    cur.close()
    
     # แสดงผลลัพธ์ออกมา
    # print("ผลลัพธ์จากการ query:")
    # for i, row  in enumerate(result, 1 ):
    #    print(f"รายการที่ {i}: ชื่อสินค้า = {row[0]}, ราคา = {row[1]} บาท, แบรนด์ = {row[2]} , ความคล้าย = {row[3]}")
    
    
    return generate_response(result,user_message)
  


# GET endpoint สำหรับหน้าหลัก
@app.get("/")
def read_root():
    return {"message": "ยินดีต้อนรับสู่ FastAPI API ตัวอย่าง"}
  
@app.post("/webhook")
def webhook(payload: dict = Body(...)):
    # ตรวจสอบว่า payload มีข้อมูลที่จำเป็นหรือไม่
    if "events" not in payload:
        raise HTTPException(status_code=400, detail="Invalid payload")

    for event in payload["events"]:
        if event["type"] == "message" and event["message"]["type"] == "text":
            user_message = event["message"]["text"]
            reply_token = event["replyToken"]
            print(f"Received message: {user_message}")
            print(f"Reply token: {reply_token}")

            # เรียกใช้ฟังก์ชัน query_db เพื่อค้นหาข้อมูล
            response_text = query_db(user_message)
            
            print(f"Response text: {response_text}")

            # # ส่งข้อความตอบกลับไปยัง LINE
            send_reply(reply_token, response_text)

    return {"status": "success"}
  

if __name__ == "__main__":
    uvicorn.run("demo2:app", host="127.0.0.1", port=5005, reload=True)