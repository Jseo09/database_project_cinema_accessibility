# database_project_cinema_accessibility
Cinema Accessibility Database Viewer

This project is a desktop GUI tool (Python + Tkinter + MySQL) that lets users explore movie theaters in Austin and San Antonio, with a focus on accessibility:

Which theaters have wheelchair seating, caption devices, and audio description

Which showtimes are captioned or audio described

Visual context via movie posters and road-view images near each theater

The app connects to a MySQL database called cinema and uses local image folders for posters and road-view screenshots.

2. Requirements
**Software**
- Python 3.9+ (Windows, 64-bit recommended)
- MySQL Server 8.x
- MySQL client (MySQL Workbench or command-line client)
**Python packages**
Install these in your environment:
- mysql-connector-python
- Pillow
- tkinterweb
```pip install mysql-connector-python pillow tkinterweb```

3. Database Setup
3.1 Create The Database
1. Start SQL WorkBench
2. Create a new schema
3. Select the schema using the command ```USE [schema name]```
3.2 Import the SQL file
1. Download the database dump files inside database/ directories
2. Open MySQL workbench
3. connect to local mySQL instance
4. Select the schema
5. Run those downloaded sql files to create appropriate databases

   
4. Configure the Python App
