import os
import sqlite3
from flask import Flask, current_app, has_app_context, jsonify, render_template, request, g


DEFAULT_DB_PATH = "todo.db"


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_mapping(
        DATABASE=os.path.join(app.root_path, DEFAULT_DB_PATH),
    )

    if test_config:
        app.config.update(test_config)

    os.makedirs(app.instance_path, exist_ok=True)

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/api/todos", methods=["GET"])
    def list_todos():
        status = request.args.get("status", "all")
        rows = query_todos(status)
        return jsonify(rows)

    @app.route("/api/todos", methods=["POST"])
    def create_todo():
        payload = request.get_json(silent=True) or {}
        title = (payload.get("title") or "").strip()
        description = (payload.get("description") or "").strip()
        tags = (payload.get("tags") or "").strip()
        if not title:
            return jsonify({"error": "Title is required."}), 400

        db = get_db()
        cursor = db.execute(
            """
            INSERT INTO todos (title, description, tags, done)
            VALUES (?, ?, ?, 0)
            """,
            (title, description, tags),
        )
        db.commit()
        todo_id = cursor.lastrowid
        row = get_todo(todo_id)
        return jsonify(row), 201

    @app.route("/api/todos/<int:todo_id>", methods=["PUT"])
    def update_todo(todo_id):
        payload = request.get_json(silent=True) or {}
        title = (payload.get("title") or "").strip()
        description = (payload.get("description") or "").strip()
        tags = (payload.get("tags") or "").strip()
        done = 1 if payload.get("done") else 0

        if not title:
            return jsonify({"error": "Title is required."}), 400
        if not get_todo(todo_id):
            return jsonify({"error": "Todo not found."}), 404

        db = get_db()
        db.execute(
            """
            UPDATE todos
            SET title = ?, description = ?, tags = ?, done = ?
            WHERE id = ?
            """,
            (title, description, tags, done, todo_id),
        )
        db.commit()
        return jsonify(get_todo(todo_id))

    @app.route("/api/todos/<int:todo_id>/toggle", methods=["PATCH"])
    def toggle_todo(todo_id):
        todo = get_todo(todo_id)
        if not todo:
            return jsonify({"error": "Todo not found."}), 404
        db = get_db()
        db.execute("UPDATE todos SET done = ? WHERE id = ?", (0 if todo["done"] else 1, todo_id))
        db.commit()
        return jsonify(get_todo(todo_id))

    @app.route("/api/todos/<int:todo_id>", methods=["DELETE"])
    def delete_todo(todo_id):
        if not get_todo(todo_id):
            return jsonify({"error": "Todo not found."}), 404
        db = get_db()
        db.execute("DELETE FROM todos WHERE id = ?", (todo_id,))
        db.commit()
        return "", 204

    @app.teardown_appcontext
    def close_db(_error=None):
        db = g.pop("db", None)
        if db is not None:
            db.close()

    with app.app_context():
        init_db()

    return app


def get_db():
    if "db" not in g:
        db_path = current_database_path()
        g.db = sqlite3.connect(db_path)
        g.db.row_factory = sqlite3.Row
    return g.db


def current_database_path():
    configured = current_app.config["DATABASE"] if has_app_context() else None
    if configured:
        return configured
    return DEFAULT_DB_PATH


def init_db():
    db = get_db()
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS todos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT DEFAULT '',
            tags TEXT DEFAULT '',
            done INTEGER NOT NULL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    db.commit()


def row_to_dict(row):
    return {
        "id": row["id"],
        "title": row["title"],
        "description": row["description"] or "",
        "tags": row["tags"] or "",
        "done": bool(row["done"]),
        "created_at": row["created_at"],
    }


def get_todo(todo_id):
    db = get_db()
    row = db.execute("SELECT * FROM todos WHERE id = ?", (todo_id,)).fetchone()
    return row_to_dict(row) if row else None


def query_todos(status):
    db = get_db()
    query = "SELECT * FROM todos"
    args = ()

    if status == "open":
        query += " WHERE done = 0"
    elif status == "done":
        query += " WHERE done = 1"
    elif status != "all":
        return []

    query += " ORDER BY created_at DESC, id DESC"
    rows = db.execute(query, args).fetchall()
    return [row_to_dict(row) for row in rows]


app = create_app()
