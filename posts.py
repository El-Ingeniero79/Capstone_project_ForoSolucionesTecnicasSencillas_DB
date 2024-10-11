from flask import Blueprint, request, jsonify
from models import db, Post
from flask_jwt_extended import jwt_required, get_jwt_identity
import logging

logger = logging.getLogger(__name__)

posts_bp = Blueprint('posts', __name__)

# Obtener todos los posts
@posts_bp.route('/posts', methods=['GET'])
def get_posts():
    try:
        
        order = request.args.get('order', 'desc')

        # Ordenar los posts según el parámetro 'order'
        if order == 'asc':
            posts = Post.query.order_by(Post.created_at.asc()).all()
        else:
            posts = Post.query.order_by(Post.created_at.desc()).all()

        return jsonify([post.serialize() for post in posts]), 200
    except Exception as e:
        logger.error(f"Error al obtener los posts: {e}")
        return jsonify({'message': 'Error interno del servidor al obtener posts'}), 500


@posts_bp.route('/posts/<int:id>', methods=['GET'])
def get_post(id):
    try:
        post = Post.query.get(id)
        if post:
            return jsonify(post.serialize()), 200
        return jsonify({'message': 'Post no encontrado'}), 404
    except Exception as e:
        logger.error(f"Error al obtener el post: {e}")
        return jsonify({'message': 'Error interno del servidor al obtener el post'}), 500


# Crear un post (registrado)
@posts_bp.route('/posts', methods=['POST'])
@jwt_required()
def create_post():
    data = request.get_json()

    # Log para verificar los datos recibidos
    logger.info(f"Datos recibidos: {data}")

    if not data or not data.get('title') or not data.get('content'):
        logger.error("Faltan campos 'title' o 'content' en la solicitud de creación de post")
        return jsonify({'message': "Faltan campos 'title' o 'content'"}), 400

    restricted = data.get('restricted', False)  

    try:
        post = Post(
            title=data['title'],
            content=data['content'],
            restricted=restricted,
            user_id=get_jwt_identity() 
        )

        db.session.add(post)
        db.session.commit()

        logger.info(f"Post creado exitosamente por el usuario ID {post.user_id}")
        return jsonify(post.serialize()), 201

    except Exception as e:
        logger.error(f"Error al crear el post: {e}")
        db.session.rollback()
        return jsonify({'message': f'Error interno: {str(e)}'}), 500


# Editar un post (solo el autor puede editar)
@posts_bp.route('/posts/<int:id>', methods=['PUT'])
@jwt_required()
def update_post(id):
    post = Post.query.get(id)
    current_user_id = get_jwt_identity()

    if not post:
        return jsonify({'message': 'Post no encontrado'}), 404

    if post.user_id != current_user_id:
        return jsonify({'message': 'No tienes permiso para editar este post'}), 403

    data = request.get_json()

    if not data or not data.get('content'):
        return jsonify({'message': "El campo 'content' es obligatorio"}), 400

    try:
        post.content = data['content']
        db.session.commit()
        return jsonify(post.serialize()), 200

    except Exception as e:
        logger.error(f"Error al actualizar el post: {e}")
        db.session.rollback()
        return jsonify({'message': f'Error interno: {str(e)}'}), 500


# Eliminar un post (solo el autor puede eliminar)
@posts_bp.route('/posts/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_post(id):
    post = Post.query.get(id)
    current_user_id = get_jwt_identity()

    if not post:
        return jsonify({'message': 'Post no encontrado'}), 404

    if post.user_id != current_user_id:
        return jsonify({'message': 'No tienes permiso para eliminar este post'}), 403

    try:
        db.session.delete(post)
        db.session.commit()
        return jsonify({'message': 'Post eliminado con éxito'}), 200

    except Exception as e:
        logger.error(f"Error al eliminar el post: {e}")
        db.session.rollback()
        return jsonify({'message': f'Error interno: {str(e)}'}), 500
