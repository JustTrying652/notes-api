from flask import Blueprint, request, jsonify
from app import db
from app.models.note import Note
from flask_jwt_extended import jwt_required, get_jwt_identity

notes_bp = Blueprint("notes", __name__)


@notes_bp.route("/", methods=["GET"])
@jwt_required()
def get_notes():
    user_id = get_jwt_identity()
    
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 5, type=int)
    search = request.args.get("search", "", type=str)
    
    query = Note.query.filter_by(user_id=user_id)
    
    if search:
        query = query.filter(
            Note.title.ilike(f"%{search}%") | 
            Note.content.ilike(f"%{search}%")
        )
    
    pagination = query.paginate(
        page=page, per_page=per_page, error_out=False
    )

    return jsonify({
        "notes": [{
            "id": note.id,
            "title": note.title,
            "content": note.content,
            "created_at": note.created_at.isoformat(),
            "updated_at": note.updated_at.isoformat()
        } for note in pagination.items],
        "total": pagination.total,
        "pages": pagination.pages,
        "current_page": pagination.page,
        "per_page": pagination.per_page
    }), 200


@notes_bp.route("/", methods=["POST"])
@jwt_required()
def create_note():
    user_id = get_jwt_identity()
    data = request.get_json()

    title = data.get("title")
    content = data.get("content")

    if not title or not content:
        return jsonify({"error": "Title and content are required"}), 400

    note = Note(title=title, content=content, user_id=user_id)
    db.session.add(note)
    db.session.commit()

    return jsonify({"message": "Note created", "id": note.id}), 201


@notes_bp.route("/<int:note_id>", methods=["GET"])
@jwt_required()
def get_note(note_id):
    user_id = get_jwt_identity()
    note = Note.query.filter_by(id=note_id, user_id=user_id).first()

    if not note:
        return jsonify({"error": "Note not found"}), 404

    return jsonify({
        "id": note.id,
        "title": note.title,
        "content": note.content,
        "created_at": note.created_at.isoformat(),
        "updated_at": note.updated_at.isoformat()
    }), 200


@notes_bp.route("/<int:note_id>", methods=["PUT"])
@jwt_required()
def update_note(note_id):
    user_id = get_jwt_identity()
    note = Note.query.filter_by(id=note_id, user_id=user_id).first()

    if not note:
        return jsonify({"error": "Note not found"}), 404

    data = request.get_json()
    note.title = data.get("title", note.title)
    note.content = data.get("content", note.content)

    db.session.commit()

    return jsonify({"message": "Note updated"}), 200


@notes_bp.route("/<int:note_id>", methods=["DELETE"])
@jwt_required()
def delete_note(note_id):
    user_id = get_jwt_identity()
    note = Note.query.filter_by(id=note_id, user_id=user_id).first()

    if not note:
        return jsonify({"error": "Note not found"}), 404

    db.session.delete(note)
    db.session.commit()

    return jsonify({"message": "Note deleted"}), 200