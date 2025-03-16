<h1>Petgoda_website</h1>
<hr>
<p>
  โครงงาน Petgoda เป็นแพลตฟอร์มจองโรงแรมสำหรับสัตว์เลี้ยงที่ช่วยให้เจ้าของสามารถหาที่พักที่เหมาะสมและปลอดภัยสำหรับสัตว์เลี้ยงของตน <br>
  มีเป้าหมายเพื่อเพิ่มความสะดวกสบายในการดูแลสัตว์เลี้ยงเมื่อต้องเดินทางหรือไม่สามารถดูแลเองได้
</p>
<p>Project วิชา CLIENT-SIDE WEB DEVELOPMENT (2/2024) รหัส 06016429 ITKMITL</p>

<h3>Pre Setup</h3>
<ul>
  <li>Python 3.x</li>
  <li>PostgreSQL (สำหรับการใช้งาน psycopg2)</li>
  <li>pip (สำหรับติดตั้ง dependencies)</li>
  <li>Node.js และ npm</li>
</ul>

<h3>Backend Dependencies</h3>
<p>ไฟล์ requirements.txt ประกอบด้วย</p>
<ul>
  <li>Django==5.1.4</li>
  <li>django-cors-headers==4.6.0</li>
  <li>djangorestframework==3.15.1</li>
  <li>djangorestframework-simplejwt==5.3.1</li>
  <li>python-dotenv==1.0.1</li>
  <li>psycopg2-binary==2.9.9</li>
  <li>pillow==11.1.0</li>
</ul>

<h3>How to Run Back-End</h3>
<h5>1. Create Django a virtual environment</h5>
(Windows)
```bash
cd backend<br>
pip install virtualenv<br>
py -m venv myvenv<br>
myvenv\Scripts\activate.bat<br>
```
(MacOS)
```bash
cd backend<br>
pip install virtualenv<br>
py -m venv myvenv<br>
source myvenv/bin/activate<br>
```
<h5>2. เข้าสู่โฟลเดอร์ backend แล้วรันคำสั่งต่อไปนี้เพื่อติดตั้ง Python dependencies ทั้งหมด:</h5>
```bash
cd petgodaWebsite
pip install -r requirements.txt<br>
หากลงแล้วเกิด Error ให้ลงตามลำดับดังนี้<br>
<ul>
<li>pip install django</li>
<li>pip install djangorestframework</li>
<li>pip install djangorestframework-simplejwt</li>
<li>pip install django-cors-headers</li>
<li>pip install dotenv</li>
<li>pip install psycopg2-binary</li>
<li>pip install pillow</li>
</ul>
```
<h5>3. สร้างไฟล์ .env ใน folder backend/petgodaWebsite/</h5>
<h5>4. Run the Backend (ต้องอยู่ใน Folder backend)</h5>
```bash
<ul>
  <li>cd backend</li>
  <li>myvenv\Scripts\activate.bat # ถ้ายังไม่ได้ activate</li>
  <li>python manage.py runserver</li>
</ul>
```
