# Git Web Viewer

Git Web Viewer is a user-friendly web interface designed to manage local Git repositories, view commit logs, and conveniently create, delete, and restore repositories through a web interface.

## 🚀 Features
- View detailed Git commit logs
- Create new Git repositories directly from the web interface
- Manage a trash bin for deleted repositories
- Restore deleted repositories
- Filter options for commit details (text files, binary files, line limits)
- Responsive and intuitive UI with sidebar and simple controls

## 🛠️ Technical Setup
- **Frontend:** HTML/CSS with minimalist, modern design
- **Backend:** Flask (Python) for managing Git operations
- **Data Management:** Local file structure for Git repositories and trash bin

## ⚙️ Installation and Setup

### Prerequisites
- Raspberry Pi or Linux server with Ubuntu
- Git
- Python 3 with Virtual Environment and Flask

### Setup Steps

1. **Install Git and set up the repository:**
   ```bash
   sudo apt update
   sudo apt install git
   mkdir -p ~/git-repos/your_repo.git
   cd ~/git-repos/your_repo.git
   git init --bare
   ```

2. **Create local Git repository (on Windows):**
   ```powershell
   mkdir D:\your_project
   cd D:\your_project
   git init
   git remote add origin ssh://user@your_server/home/user/git-repos/your_repo.git
   git push -u origin master
   ```

3. **Set up SSH-Key (optional, recommended):**
   ```powershell
   ssh-keygen -t ed25519
   ssh-copy-id user@your_server
   ```

4. **Install and start the web interface:**
   ```bash
   mkdir ~/git-web
   cd ~/git-web
   python3 -m venv venv
   source venv/bin/activate
   pip install flask
   ```
   Copy the `app.py` content into the directory and start the server:
   ```bash
   python app.py
   ```

   Open in your browser: `http://your_server:5000`

## 🔄 Typical Workflow
```bash
git add .
git commit -m "Description of your changes"
git push origin master
```

## 📁 Project Structure
```
git-web-viewer/
├── static/
│   ├── style.css
│   └── script.js
├── templates/
│   ├── index.html
│   ├── repo_view.html
│   └── trash_view.html
└── app.py
```

## 📜 License
This project is open source and freely available under the terms of the MIT license.

---

We welcome your contributions and issues!

