# Cinema Accessibility Database Viewer

A desktop GUI tool built with **Python + Tkinter + MySQL** to explore movie theaters in **Austin** and **San Antonio**, focusing on **accessibility features**.

The app provides:
- Theater accessibility info (wheelchair seating, caption devices, audio description)
- Showtimes with captions or audio description
- Movie posters and nearby road-view images

The application connects to a MySQL database named **`cinema`** and loads images from local asset folders.

---

## 1. Requirements

### 1.1 Software
- Python 3.9+ (Windows 64-bit recommended)
- MySQL Server 8.x
- MySQL Workbench or MySQL CLI client

### 1.2 Python Packages
Install all dependencies:

```bash
pip install mysql-connector-python pillow tkinterweb
```

| Package | Purpose |
|--------|---------|
| mysql-connector-python | MySQL connectivity |
| Pillow | Image loading / processing |
| tkinterweb | Rendering web content within Tkinter |

---

## 2. Database Setup

### 2.1 Create the Database Schema
1. Open **MySQL Workbench**
2. Create a schema (e.g., `cinema`)
3. Select the schema:

```sql
USE cinema;
```

### 2.2 Import SQL Dump Files
1. Download `.sql` files from the `database/` directory  
2. Open MySQL Workbench  
3. Select the **cinema** schema  
4. Execute each SQL file to create tables and insert data  

---

## 3. Configure the Python App

1. Open the config script (`config.py`)
2. Set your MySQL connection info:

```python
DB_CONFIG = {
    "host": "localhost",
    "user": "your_username",
    "password": "your_password",
    "database": "your_schema_name",
}
```

3. Check image directories:
- `assets/posters/` — movie posters  
- `assets/roadviews/` — road-view images  

4. Run the application:

```bash
python app.py
```

---

## 4. Notes
- Covers theaters in **Austin** and **San Antonio**  
- Ensure **MySQL Server is running** before starting the app  
- Image files must exist in their respective asset folders  
