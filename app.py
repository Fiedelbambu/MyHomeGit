from flask import Flask, render_template, redirect, url_for, request
import subprocess, os, shutil, time
from datetime import datetime

app = Flask(__name__)

REPOS_BASE = "/home/fiede"
REPOS_PATH = os.path.join(REPOS_BASE, "git-repos")
TRASH_PATH = os.path.join(REPOS_PATH, "git-trash")


TEMP_WORKDIR = "/tmp/gitweb"
if not os.path.exists(TEMP_WORKDIR):
    os.makedirs(TEMP_WORKDIR)


if not os.path.exists(TRASH_PATH):
    os.makedirs(TRASH_PATH)

def get_projects():
    return sorted([d for d in os.listdir(REPOS_PATH) if d.endswith('.git') and os.path.isdir(os.path.join(REPOS_PATH, d))])

def clean_trash():
    now = time.time()
    for entry in os.listdir(TRASH_PATH):
        path = os.path.join(TRASH_PATH, entry)
        if os.path.isdir(path):
            stat = os.stat(path)
            if now - stat.st_mtime > 30 * 86400:
                shutil.rmtree(path, ignore_errors=True)

def checkout_project_to_temp(project):
    repo_path = os.path.join(REPOS_PATH, project)
    worktree_path = os.path.join(TEMP_WORKDIR, project.replace('.git', ''))

    # Wenn Ordner schon da ist: löschen
    if os.path.exists(worktree_path):
        shutil.rmtree(worktree_path)
    os.makedirs(worktree_path)

    try:
        # Aktuellen Branch ermitteln
        result = subprocess.run(
            ["git", "--git-dir", repo_path, "symbolic-ref", "--short", "HEAD"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        current_branch = result.stdout.decode("utf-8").strip()

        # Checkout in Worktree
        subprocess.run(
            ["git", f"--git-dir={repo_path}", f"--work-tree={worktree_path}", "checkout", current_branch, "--", "."],
            check=True
        )
        return worktree_path
    except Exception as e:
        return f"❌ Fehler beim Checkout: {e}"



@app.route("/")
def home():
    clean_trash()
    projects = get_projects()
    if projects:
        return redirect(url_for('git_log', project=projects[0]))
    else:
        return "Keine Projekte gefunden."

@app.route("/log/<project>")
def git_log(project):
    projects = get_projects()
    repo_path = os.path.join(REPOS_PATH, project)
    git_log_output = subprocess.getoutput(
        f"git --git-dir={repo_path} log --all --pretty=format:'%H%x1f%an%x1f%ar%x1f%d%x1f%s' --name-only"
    )

    commits = []
    commit_lines = git_log_output.strip().split('\n')
    for line in commit_lines:
        if line.strip() == '':
            continue
        if '\x1f' in line:
            parts = line.split('\x1f')
            commits.append({
                'hash': parts[0],
                'author': parts[1],
                'date': parts[2],
                'ref': parts[3],
                'message': parts[4],
                'files': []
            })
        else:
            if commits:
                commits[-1]['files'].append(line.strip())

    return render_template("index.html", projects=projects, project=project, commits=commits)

@app.route("/log/<project>/<commit_hash>")
def commit_details(project, commit_hash):
    repo_path = os.path.join(REPOS_PATH, project)
    try:
        line_limit = int(request.args.get("limit", 300))
        text_only = request.args.get("textOnly", "false") == "true"
        hide_binary = request.args.get("hideBinary", "false") == "true"

        diff = subprocess.check_output(
            ["git", "--git-dir", repo_path, "show", commit_hash, "--no-color"],
            stderr=subprocess.DEVNULL,
            timeout=5
        ).decode("utf-8", errors="replace")

        if hide_binary and "Binary files" in diff:
            return "⚠️ Binärdateien wurden geändert. Kein Text-Diff verfügbar."

        if text_only and not any(file.endswith((
            '.txt', '.md', '.py', '.cs', '.cpp', '.h', '.html', '.xml')) for file in diff.splitlines()):
            return "⚠️ Keine unterstützten Textdateien im Diff."

        lines = diff.splitlines()
        if len(lines) > line_limit:
            return f"⚠️ Diff zu lang: {len(lines)} Zeilen. Anzeige auf {line_limit} Zeilen begrenzt."

        diff = diff.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        return diff

    except subprocess.TimeoutExpired:
        return "⏱️ Diff konnte nicht geladen werden (Timeout)."

    except Exception as e:
        return f"❌ Fehler beim Laden des Diffs: {e}"

@app.route("/create-repo", methods=["POST"])
def create_repo():
    name = request.form.get("repo_name", "").strip()

    if not name or '/' in name or '..' in name or not name.isalnum():
        return "❌ Ungültiger Repository-Name."

    repo_path = os.path.join(REPOS_PATH, f"{name}.git")
    if os.path.exists(repo_path):
        return "⚠️ Repository existiert bereits."

    try:
        os.makedirs(repo_path)
        subprocess.run(["git", "init", "--bare"], cwd=repo_path, check=True)
        return redirect(url_for('git_log', project=f"{name}.git"))
    except Exception as e:
        return f"❌ Fehler beim Erstellen: {e}"

@app.route("/delete/<project>", methods=['POST'])
def delete_project(project):
    repo_path = os.path.join(REPOS_PATH, project)
    trash_path = os.path.join(TRASH_PATH, f"{project}_{int(time.time())}")

    if os.path.isdir(repo_path):
        try:
            shutil.move(repo_path, trash_path)
            return redirect(url_for('home'))
        except Exception as e:
            return f"❌ Fehler beim Verschieben in den Papierkorb: {e}"
    return "❌ Projektverzeichnis nicht gefunden."

@app.route("/restore/<project>", methods=["POST"])
def restore_project(project):
    matches = [d for d in os.listdir(TRASH_PATH) if d.startswith(project)]
    if not matches:
        return f"❌ Kein Backup für {project} im Papierkorb gefunden.", 404
    matches.sort(reverse=True)
    last_deleted = matches[0]
    src = os.path.join(TRASH_PATH, last_deleted)
    dest = os.path.join(REPOS_PATH, project)
    try:
        shutil.move(src, dest)
        return redirect(url_for('home'))
    except Exception as e:
        return f"❌ Fehler bei der Wiederherstellung: {e}", 500

@app.route("/trash")
def trash_view():
    trash_projects = [
        d for d in os.listdir(TRASH_PATH)
        if os.path.isdir(os.path.join(TRASH_PATH, d))
    ]
    return render_template("index.html", trash_projects=trash_projects, projects=get_projects())


@app.route("/browse/<project>")
@app.route("/browse/<project>/")
@app.route("/browse/<project>/<path:subpath>")
def browse_project(project, subpath=""):
    from pathlib import Path

    projects = get_projects()  # ← für die Sidebar

    worktree = checkout_project_to_temp(project)
    if isinstance(worktree, str) and worktree.startswith("❌"):
        return worktree

    abs_path = os.path.join(worktree, subpath)
    if not os.path.exists(abs_path):
        return "❌ Pfad nicht gefunden."

    # Wenn eine Datei angeklickt wurde
    if os.path.isfile(abs_path):
        try:
            with open(abs_path, "r", encoding="utf-8") as f:
                content = f.read()
        except:
            content = "⚠️ Datei kann nicht angezeigt werden (evtl. Binärformat)."
        return render_template(
            "file_viewer.html",
            project=project,
            filepath=subpath,
            content=content,
            projects=projects  # ← wichtig für Sidebar
        )

    # Wenn ein Ordner angezeigt wird
    entries = []
    for entry in sorted(os.listdir(abs_path)):
        full_path = os.path.join(abs_path, entry)
        is_dir = os.path.isdir(full_path)
        entries.append((entry, is_dir))

    return render_template(
        "file_browser.html",
        project=project,
        entries=entries,
        current_path=subpath,
        projects=projects  # ← wichtig für Sidebar
    )

from flask import send_file

@app.route("/download/<project>/<path:subpath>")
def download_file(project, subpath):
    worktree = checkout_project_to_temp(project)
    if isinstance(worktree, str) and worktree.startswith("❌"):
        return worktree

    abs_path = os.path.join(worktree, subpath)
    if not os.path.isfile(abs_path):
        return "❌ Datei nicht gefunden.", 404

    return send_file(abs_path, as_attachment=True)





if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
