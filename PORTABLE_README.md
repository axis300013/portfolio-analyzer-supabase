# 📦 Portfolio Analyzer - Portable Package

## 🚀 Quick Start

### **On This Computer:**
Just double-click: **`START_PORTABLE.bat`**

### **On Another Computer:**

1. **Copy these files/folders:**
   ```
   Portfolio Analyzer/
   ├── START_PORTABLE.bat      ← Double-click to run
   ├── .env                     ← Your Supabase connection
   ├── .env.example             ← Template (reference)
   ├── backend/                 ← API server
   ├── ui/                      ← Streamlit interface
   └── PORTABLE_README.md       ← This file
   ```

2. **Install Python 3.13** (if not already installed):
   - Download from: https://www.python.org/downloads/
   - ✅ Check "Add Python to PATH" during installation

3. **Install Dependencies** (first time only):
   ```cmd
   cd backend
   pip install -r requirements.txt
   
   cd ../ui
   pip install -r requirements.txt
   ```

4. **Create your .env file:**
   - Copy `.env.example` to `.env`
   - Add your Supabase connection string:
     ```
     DATABASE_URL=postgresql://postgres:PASSWORD@db.xxx.supabase.co:5432/postgres
     ```

5. **Run:**
   - Double-click `START_PORTABLE.bat`
   - Browser opens automatically

---

## ✨ What's Included

### **START_PORTABLE.bat**
- One-click launcher
- Tests connection before starting
- Opens minimized terminals for API and UI
- Launches browser automatically

### **Backend** (FastAPI)
- REST API on port 8000
- Connects to Supabase database
- Handles all data operations

### **UI** (Streamlit)
- Web interface on port 8501
- Portfolio tracking
- Wealth management
- Analytical reports

### **Database** (Supabase Cloud)
- Free PostgreSQL database
- 500MB storage
- Automatic daily backups
- Access from anywhere

---

## 🌍 Access From Multiple Devices

### **Same Network (Home/Office):**
1. Find your computer's IP address:
   ```cmd
   ipconfig
   ```
   (Look for "IPv4 Address" like 192.168.1.100)

2. On other device, open browser:
   ```
   http://192.168.1.100:8501
   ```

### **Different Network (Internet):**
Your data is already in the cloud (Supabase)! Just:
1. Copy the portable folder to new device
2. Run `START_PORTABLE.bat`
3. Same data, different location!

---

## 📋 Requirements

- **Python**: 3.13 or later
- **Internet**: Required (for Supabase connection)
- **RAM**: 512MB minimum
- **Disk**: 500MB for installation

---

## 🔒 Security Notes

### **Protect Your .env File:**
- Contains your database password
- Never share publicly
- Add to .gitignore if using Git
- Keep backup in secure location

### **Supabase Connection:**
- SSL encrypted by default
- Connection pooling enabled
- Password protected

---

## 🛠️ Troubleshooting

### **"Python not found"**
- Install Python from python.org
- Ensure "Add to PATH" was checked
- Restart terminal/computer

### **"Cannot connect to Supabase"**
- Check internet connection
- Verify DATABASE_URL in .env
- Ensure Supabase project is active
- Test: https://supabase.com/dashboard

### **"Port already in use"**
- Close other instances of the app
- Check ports 8000 and 8501
- Restart computer if needed

### **"Module not found"**
- Run in each folder:
  ```cmd
  pip install -r requirements.txt
  ```

---

## 📊 File Structure

```
Portfolio Analyzer/
│
├── START_PORTABLE.bat          ← Main launcher
├── .env                         ← Your configuration (SECRET!)
├── .env.example                 ← Template
├── PORTABLE_README.md           ← This file
│
├── backend/                     ← API Server
│   ├── app/
│   │   ├── main.py             ← FastAPI app
│   │   ├── config.py           ← Reads .env
│   │   ├── db.py               ← Database connection
│   │   ├── models.py           ← Data models
│   │   └── ...
│   └── requirements.txt         ← Python dependencies
│
└── ui/                          ← Streamlit Interface
    ├── streamlit_app_wealth.py  ← Main UI
    └── requirements.txt         ← UI dependencies
```

---

## 💾 Backup Strategy

### **Database Backups:**
Supabase automatically backs up daily (kept 7 days on free tier)

### **Manual Backup:**
```cmd
python -c "from backup_supabase import backup_database; backup_database()"
```

### **Configuration Backup:**
Copy `.env` to secure location (USB drive, password manager)

---

## 🚀 Next Steps

1. **Set up on second computer** - Copy folder, run START_PORTABLE.bat
2. **Create desktop shortcut** - Right-click START_PORTABLE.bat → Send to → Desktop
3. **Schedule backups** - Use Windows Task Scheduler
4. **Share with family** - Give them separate portfolios

---

## 📞 Support

- **Setup Guide**: QUICK_START_SUPABASE.md
- **Detailed Guide**: SUPABASE_SETUP_GUIDE.md
- **Supabase Docs**: https://supabase.com/docs

---

## ✅ Quick Checklist

Before sharing with others:

- [ ] Python 3.13+ installed
- [ ] Dependencies installed (pip install -r requirements.txt)
- [ ] .env file created with Supabase connection
- [ ] Tested: START_PORTABLE.bat runs successfully
- [ ] Browser opens to http://localhost:8501
- [ ] Can see portfolio data

---

**Enjoy your portable, cloud-connected Portfolio Analyzer!** 💰✨
