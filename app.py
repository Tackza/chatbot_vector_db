import mysql.connector
from sentence_transformers import SentenceTransformer
import json
from flask import Flask, jsonify, request

app = Flask(__name__)


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
# text = "i love thailand"
# embedding = embedder.encode(text)


# products = [
#   {
#     "name": "16GB 2666MHz DDR4 CL16 DIMM (Kit of 2) FURY Beast RGB",
#     "price": 1570,
#     "brand": "Kingston"
#   },
#   {
#     "name": "16GB 2666MHz DDR4 CL16 DIMM (Kit of 2) FURY Beast Black",
#     "price": 1390,
#     "brand": "Kingston"
#   },
#   {
#     "name": "32GB 3200MHz DDR4 CL16 DIMM (Kit of 2) FURY Beast RGB",
#     "price": 2550,
#     "brand": "Kingston"
#   },
#   {
#     "name": "16GB 3200MT/s DDR4 CL16 DIMM (Kit of 2) FURY Beast RGB",
#     "price": 1880,
#     "brand": "Kingston"
#   },
#   {
#     "name": "32GB 3200MHz DDR4 CL16 DIMM (Kit of 2) FURY Beast RGB",
#     "price": 3070,
#     "brand": "Kingston"
#   },
#   {
#     "name": "16GB 3200MHz DDR4 CL16 DIMM (Kit of 2) FURY Beast Black",
#     "price": 1480,
#     "brand": "Kingston"
#   },
#   {
#     "name": "32GB 3200MT/s DDR4 CL18 DIMM (Kit of 2) FURY Renegade RGB",
#     "price": 3210,
#     "brand": "Kingston"
#   },
#   {
#     "name": "32GB 3200MHz DDR4 CL16 DIMM (Kit of 2) 1Gx8 FURY Renegade Black",
#     "price": 2770,
#     "brand": "Kingston"
#   },
#   {
#     "name": "16GB 3200MT/s DDR4 CL16 DIMM (Kit of 2) 1Gx8 FURY Renegade RGB",
#     "price": 2030,
#     "brand": "Kingston"
#   },
#   {
#     "name": "16GB 3200MT/s DDR4 CL16 DIMM (Kit of 2) 1Gx8 Fury Renegade Black",
#     "price": 1610,
#     "brand": "Kingston"
#   },
#   {
#     "name": "16GB 3600MHz DDR4 CL16 DIMM (Kit of 2) FURY Renegade Black",
#     "price": 2370,
#     "brand": "Kingston"
#   },
#   {
#     "name": "16GB 3600MT/s DDR4 CL17 DIMM (Kit of 2) FURY Beast RGB",
#     "price": 1860,
#     "brand": "Kingston"
#   },
#   {
#     "name": "32GB 3600MT/s DDR4 CL18 DIMM (Kit of 2) FURY Beast RGB",
#     "price": 2880,
#     "brand": "Kingston"
#   },
#   {
#     "name": "32GB 3600MHz DDR4 CL18 DIMM (Kit of 2) FURY Beast RGB",
#     "price": 3000,
#     "brand": "Kingston"
#   },
#   {
#     "name": "32GB (2x16GB) DDR4 3600MT/s CL18 FURY Beast Black",
#     "price": 2850,
#     "brand": "Kingston"
#   },
#   {
#     "name": "16GB 4800MT/s DDR5 CL38 DIMM (Kit of 2) FURY Beast RGB PnP",
#     "price": 2620,
#     "brand": "Kingston"
#   },
#   {
#     "name": "32GB 4800MT/s DDR5 CL38 DIMM (Kit of 2) FURY Beast RGB PnP",
#     "price": 4110,
#     "brand": "Kingston"
#   },
#   {
#     "name": "16GB 4800MT/s DDR5 CL38 DIMM (Kit of 2) FURY Beast Black PnP",
#     "price": 2160,
#     "brand": "Kingston"
#   },
#   {
#     "name": "32GB 4800MHz DDR5 CL38 DIMM (Kit of 2) FURY Beast Black",
#     "price": 3550,
#     "brand": "Kingston"
#   },
#   {
#     "name": "16GB 5200MT/s DDR5 CL40 DIMM (Kit of 2) FURY Beast RGB",
#     "price": 2490,
#     "brand": "Kingston"
#   },
#   {
#     "name": "32GB 5200MT/s DDR5 CL40 DIMM (Kit of 2) FURY Beast RGB",
#     "price": 4010,
#     "brand": "Kingston"
#   },
#   {
#     "name": "16GB 5200MT/s DDR5 CL40 DIMM (Kit of 2) FURY Beast Black",
#     "price": 2150,
#     "brand": "Kingston"
#   },
#   {
#     "name": "32GB 5200MHz DDR5 CL40 DIMM (Kit of 2) FURY Beast Black",
#     "price": 3670,
#     "brand": "Kingston"
#   },
#   {
#     "name": "32GB (2x16GB) DDR5 5200MT/s CL40 FURY Beast White RGB XMP",
#     "price": 3960,
#     "brand": "Kingston"
#   },
#   {
#     "name": "16GB 5600MT/s DDR5 CL36 DIMM (Kit of 2) FURY Beast RGB",
#     "price": 4110,
#     "brand": "Kingston"
#   },
#   {
#     "name": "16GB 5600MT/s DDR5 CL40 DIMM (Kit of 2) FURY Beast RGB",
#     "price": 2600,
#     "brand": "Kingston"
#   },
#   {
#     "name": "16GB 5600MHz DDR5 CL40 DIMM (Kit of 2) FURY Beast Black",
#     "price": 2240,
#     "brand": "Kingston"
#   },
#   {
#     "name": "32GB (2x16GB) DDR5 5600MHz CL40 FURY Beast Black",
#     "price": 3840,
#     "brand": "Kingston"
#   },
#   {
#     "name": "64GB 5600MT/s DDR5 CL40 DIMM (Kit of 2) FURY Beast RGB XMP",
#     "price": 7110,
#     "brand": "Kingston"
#   },
#   {
#     "name": "32GB (2x16GB) DDR5 5600MT/s CL40 FURY Beast White RGB XMP",
#     "price": 4130,
#     "brand": "Kingston"
#   },
#   {
#     "name": "32GB (2x16GB) DDR5 6000MT/s CL32 FURY Renegade Silver/White RGB XMP",
#     "price": 4680,
#     "brand": "Kingston"
#   },
#   {
#     "name": "32GB 6000MT/s DDR5 CLXX DIMM (Kit of 2) FURY Beast RGB",
#     "price": 4440,
#     "brand": "Kingston"
#   },
#   {
#     "name": "32GB 6000MT/s DDR5 CL36 DIMM (Kit of 2) FURY Beast Black EXPO",
#     "price": 4210,
#     "brand": "Kingston"
#   },
#   {
#     "name": "16GB 6000MT/s DDR5 CL40 DIMM (Kit of 2) FURY Beast RGB",
#     "price": 2760,
#     "brand": "Kingston"
#   },
#   {
#     "name": "32GB (2x16GB) DDR5 6000MT/s CL40 FURY Beast Black RGB",
#     "price": 4520,
#     "brand": "Kingston"
#   },
#   {
#     "name": "16GB 6000MHz DDR5 CL40 DIMM (Kit of 2) FURY Beast Black",
#     "price": 2430,
#     "brand": "Kingston"
#   },
#   {
#     "name": "32GB (2x16GB) DDR5 6000MHz CL40 FURY Beast Black",
#     "price": 4260,
#     "brand": "Kingston"
#   },
#   {
#     "name": "32GB (2x16GB) DDR5 6000MT/s CL38 FURY Impact Black XMP",
#     "price": 4240,
#     "brand": "Kingston"
#   },
#   {
#     "name": "32GB (2x16GB) DDR5 6400MT/s CL32 FURY Renegade RGB",
#     "price": 5220,
#     "brand": "Kingston"
#   },
#   {
#     "name": "48GB 6400MT/s DDR5 CL32 DIMM (Kit of 2) FURY Renegade RGB XMP",
#     "price": 7270,
#     "brand": "Kingston"
#   },
#   {
#     "name": "32GB 6400MT/s DDR5 CL32 DIMM (Kit of 2) FURY Renegade RGB White XMP",
#     "price": 5210,
#     "brand": "Kingston"
#   },
#   {
#     "name": "32GB (2x16GB) DDR5 7200MT/s CL38 FURY Renegade Black RGB",
#     "price": 6670,
#     "brand": "Kingston"
#   },
#   {
#     "name": "32GB DDR5 7200MT/s (Kit of 2) FURY Renegade White RGB",
#     "price": 6960,
#     "brand": "Kingston"
#   },
#   {
#     "name": "32GB 8000MT/s DDR5 CL38 DIMM (Kit of 2) FURY Renegade RGB XMP",
#     "price": 8770,
#     "brand": "Kingston"
#   }
# ]

# def add_document_data(connect , name , price , brand=None):
#    cur = connect.cursor()
    
#     # จัดการกรณีที่ brand อาจเป็น None
#    if brand is None:
#         product_price = name + " ราคา " + str(price)
#    else:
#         product_price = name + " ราคา " + str(price) + " แบรนด์ " + str(brand)
    
#    embedding = embedder.encode(product_price).tolist()
    
#     # ถ้าคุณต้องการเพิ่ม brand ลงในฐานข้อมูลด้วย
#    cur.execute("INSERT INTO documents (product_name, price, brand, embedding) VALUES (%s, %s, %s, %s)", 
#                 (name, price, brand, json.dumps(embedding)))
    
#    connect.commit()
#    cur.close()

# for product in products:
#     brand = product.get("brand", None)
#     add_document_data(connection , product["name"] , product["price"] , brand)

def query_db(connect , query):
    # สร้าง embedding vector
    query_embedding = embedder.encode(query).tolist()
    # แปลง list เป็น string ในรูปแบบที่ MySQL เข้าใจได้
    vector_str = str(query_embedding).replace(' ', '')
    
    
    # ใช้ parameter binding แทนการแทรก string ตรงๆ
    cur = connect.cursor()
    
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
    
    
    return result
  
# results = query_db(connection, "intel core i9 ราคาถูกที่สุด")
# print("\nรูปแบบข้อมูลดิบ:")
# print(results)


def generate_response(connection, query):
    retrived_results = query_db(connection, query)
    
    # Check if we got any relevant results
    if not retrived_results:
        return "ขออภัย ฉันไม่มีข้อมูลเกี่ยวกับเรื่องนี้ในฐานข้อมูลของเรา โปรดระบุรุ่นหรือชื่อสินค้าให้ชัดเจนยิ่งขึ้น"
    
    context = "\n".join([
        f"ชื่อสินค้า: {row[0]}, ราคา: {row[1]} บาท, แบรนด์: {row[2]}" for row in retrived_results
    ])
    print(f"\nContext:\n{context}")
    
    prompt = f""" Answer the question based on the following context:\n{context}\n\nQuestion: {query}\nAnswer:"""
    
    # Add instruction to handle irrelevant questions
    system_prompt = """
    คุณคือผู้ช่วยที่มีความรู้เกี่ยวกับสินค้าและราคาของสินค้าในร้านค้าออนไลน์ ไม่ตอบคำถามเกินไปจากข้อมูลที่มีในฐานข้อมูลของเรา
    """
    
    response = ollama.chat(model="llama3.2"  , messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt}
    ])
    
    return response['message']['content']
  

answer = generate_response(connection, "ขอราคา intel core i5 ที่มีในร้านทั้งหมด")
print("\nคำตอบจากโมเดล:")
print(answer)

@app.route('/')
def index():
    return jsonify({"message": "ยินดีต้อนรับสู่ API ของเรา!"})



