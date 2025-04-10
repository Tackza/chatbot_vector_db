import mysql.connector
from sentence_transformers import SentenceTransformer
from google import genai
from google.genai import types
from flask import Flask, jsonify, request
import requests
import json

app = Flask(__name__)

# LINE Messaging API Token
LINE_CHANNEL_ACCESS_TOKEN = "HqR5KgtSFnpkKMS+HPaTINdo/gzFW/0h/i4RLzMRlHN2vEQbmIwDTXnFSqD+0ZJNVbLLBwoAxx5JbvRjNG6GqtvntWwu784PrqiHfsXsCwPD/m9oIBAlZZ7dWKY73d417JSw46DdG9toEc3EuZX1DwdB04t89/1O/w1cDnyilFU="
LINE_API_URL = "https://api.line.me/v2/bot/message/reply"
LINE_LOADING_URL = "https://api.line.me/v2/bot/chat/loading/start"

connection = mysql.connector.connect(
  host = "gateway01.ap-southeast-1.prod.aws.tidbcloud.com",
  port = 4000,
  user = "2d1BmeMeYLLXjyZ.root",
  password = "frbr9qv0ECdnhonm",
  database = "chatbot_vector",
  # ssl_ca = "/etc/ssl/cert.pem",
  # ssl_verify_cert = True,
  # ssl_verify_identity = True
)

embedder = SentenceTransformer("all-MiniLM-L6-v2")

client = genai.Client(api_key="AIzaSyCmcfFFTxxGEHcZWfP8MD9cKx3PYxVjxgw") 

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

def generate_response(results_text, user_message,reply_token):
    # สร้าง context จากผลลัพธ์ที่ได้
  context = "\n".join([
        f"ชื่อสินค้า: {row[0]}, ราคา: {row[1]} บาท, แบรนด์: {row[2]}" for row in results_text
    ])
  print(f"\nContext:\n{context}")
  prompt = f""" Answer the question based on the following context:\n{context}\n\nQuestion: {user_message}\nAnswer:"""
    
    # Add instruction to handle irrelevant questions
  system_prompt = """
    คุณคือผู้ช่วยที่มีความรู้เกี่ยวกับสินค้าและราคาของสินค้าในร้านค้าออนไลน์ ไม่ตอบคำถามเกินไปจากข้อมูลที่มีในฐานข้อมูลของเรา
    """
  response = client.models.generate_content(
      model="gemini-2.0-flash",
      contents=prompt,
      config=types.GenerateContentConfig(
          max_output_tokens=500,
          temperature=0.1,
          system_instruction=system_prompt,
          )
      )
  print(f"Response: {response.text}")
  
  send_reply(reply_token,response.text)

def query_db(user_message,reply_token):
    # สร้าง embedding vector
    query_embedding = embedder.encode(user_message).tolist()
    print(f"Query embedding: {query_embedding}")
    # แปลง list เป็น string ในรูปแบบที่ MySQL เข้าใจได้
    vector_str = str(query_embedding).replace(' ', '')
    
    print(f"Vector string: {vector_str}")
    
    
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
    print("ผลลัพธ์จากการ query:")
    for i, row  in enumerate(result, 1 ):
       print(f"รายการที่ {i}: ชื่อสินค้า = {row[0]}, ราคา = {row[1]} บาท, แบรนด์ = {row[2]} , ความคล้าย = {row[3]}")
    
    
    return generate_response(result,user_message,reply_token)
  
  



  
  
  
# results = query_db(connection, "intel core i5 ราคาถูกที่สุด")
# print("\nรูปแบบข้อมูลดิบ:")
# print(results)


@app.route('/')
def index():
    return jsonify({"message": "ยินดีต้อนรับสู่ API ของเรา!"})
  
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    print(f"Received data: {data}")
    
    try:
      for event in data['events']:
        if event['type'] == 'message':
          reply_token = event['replyToken']
          user_message = event['message']['text']
          
          print(f"User message: {user_message}")
          print(f"Reply token: {reply_token}")
          
          # เรียกใช้ฟังก์ชัน generate_response
          generate_reponse = query_db(user_message,reply_token)
          
          # print(f"generate_reponse message: {generate_reponse}")
          
          # send_reply(reply_token, generate_reponse)
          
          return  jsonify({"status": "success", "message": "Reply sent successfully!"}), 200
          
        
    except KeyError as e:
      return jsonify({"status": "error", "message": str(e)}), 400  