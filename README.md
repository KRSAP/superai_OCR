# Thai Election Vote Extractor

โปรเจกต์นี้ใช้ Gemini Vision สำหรับอ่านข้อความจากภาพเอกสารเลือกตั้งไทย แล้วดึงจำนวนคะแนนเสียงของพรรคการเมืองออกมาเป็นไฟล์ส่งออก `.csv`

โค้ดถูกแยกเป็นหลายส่วนเพื่อให้ดูแลและแก้ไขง่าย:
- `main.py` จุดเริ่มรันโปรแกรม
- `config.py` เก็บค่าตั้งต้นของระบบ
- `storage.py` จัดการอ่าน/เขียนไฟล์ CSV และ progress
- `page_loader.py` หาไฟล์ภาพของแต่ละเอกสาร
- `llm.py` เรียกโมเดลและ parse JSON
- `vote_extract.py` รวม logic การดึงคะแนนและจับคู่ชื่อพรรค
- `prompt.py` เก็บ prompt ที่ใช้ส่งให้โมเดล

---

## โครงสร้างไฟล์

```text
project/
├─ main.py
├─ config.py
├─ storage.py
├─ page_loader.py
├─ llm.py
├─ vote_extract.py
├─ prompt.py
├─ requirements.txt
├─ data/
│  ├─ submission_template.csv
│  └─ images/
│     ├─ constituency_1.png
│     ├─ constituency_1_page2.png
│     ├─ party_list_3.png
│     └─ ...
└─ output/
   ├─ progress.json
   └─ submission.csv
```
# การติดตั้ง package
pip install -r requirements.txt

# การตั้งค่า API Key
```text
Windows CMD
set API_KEY=your_api_key
python app.py

Windows PowerShell
$env:API_KEY="your_api_key"
python app.py
```
# รูปแบบข้อมูลที่ต้องมี
1) ไฟล์ template

ต้องมีไฟล์:
data/submission_template.csv

โดยควรมีคอลัมน์อย่างน้อย:
id
doc_id
party_name
row_num

ตัวอย่าง:
id,doc_id,party_name,row_num

1,constituency_1,พรรคตัวอย่าง,1

2,constituency_1,พรรคทดสอบ,2

3,party_list_2,พรรคสมมติ,1


2) โฟลเดอร์ภาพ

ต้องมีโฟลเดอร์:

data/images/

ตั้งชื่อไฟล์ภาพตาม doc_id

ตัวอย่าง:

constituency_1.png

constituency_1_page2.png

party_list_2.png
