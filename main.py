from flask import Flask, request, jsonify
from flask_cors import CORS
from models import db, Meme, Plantilla, Usuario

app = Flask(__name__)
port = 5000
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:postgres@localhost:5432/intro'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
CORS(app)
CORS(app, supports_credentials=True, methods=["GET", "POST", "PUT", "DELETE"])


@app.route('/')
def hello_world():
    return 'Hello world!'

@app.route('/memes/', methods=['GET'])
def todos_los_memes():
    try:
        memes = Meme.query.all()
        memes_data = []
        for meme in memes:
            meme_data = {
                'id': meme.meme_id,
                'imagen': meme.imagen,
                'fecha': meme.fecha.strftime('%Y-%m-%d %H:%M:%S'),
                'usuario_id': meme.usuario_id,
                'plantilla_id': meme.plantilla_id
            }
            memes_data.append(meme_data)
        return jsonify(memes_data)
    except Exception as error:
        print(f"Error al obtener memes: {str(error)}")
        return jsonify({'message': 'No se han encontrado los memes.'}), 500
    

@app.route('/plantillas/', methods=['GET'])
def obtener_plantillas():
    try:
        plantillas = Plantilla.query.all()  # Asume que Plantilla es tu modelo de datos para las plantillas de memes
        plantillas_data = []
        
        for plantilla in plantillas:
            plantilla_data = {
                'id': plantilla.plantilla_id,
                'nombre': plantilla.nombre_plantilla,
                'imagen': plantilla.imagen,
                'usuario_id': plantilla.usuario_id
            }
            plantillas_data.append(plantilla_data)

        return jsonify(plantillas_data), 200

    except Exception as error:
        print(f"Error al obtener plantillas de memes: {str(error)}")
        return jsonify({'message': 'Error interno al obtener las plantillas de memes'}), 500


@app.route('/memes/<int:meme_id>', methods=['GET'])
def obtener_id_meme(meme_id):
    try:
        meme = Meme.query.get(meme_id)
        if meme is None:
            return jsonify({'message': 'El meme con el ID especificado no se encontró'}), 404

        meme_data = {
            'id': meme.meme_id,
            'imagen': meme.imagen,
            'fecha': meme.fecha.strftime('%Y-%m-%d %H:%M:%S'),
            'usuario_id': meme.usuario_id,
            'plantilla_id': meme.plantilla_id
        }
        return jsonify(meme_data), 200
    except Exception as error:
        print(f"Error al obtener id del meme: {str(error)}")
        return jsonify({'message': 'Error interno al obtener el meme'}), 500


@app.route('/memes/', methods=['POST'])
def crear_memes():
    try:
        data = request.json
        imagen = data.get('imagen')
        nombre_usuario = data.get('nombre_usuario')
        correo_electronico = data.get('correo_electronico')  # Corregido: coincidir con el nombre del atributo en el modelo
        contraseña = data.get('contraseña')
        plantilla_id = data.get('plantilla_id')
        nombre_plantilla = data.get('nombre_plantilla')

        # Verificar si el usuario ya existe o crear uno nuevo
        usuario = Usuario.query.filter_by(nombre_usuario=nombre_usuario).first()
        if not usuario:
            usuario = Usuario(nombre_usuario=nombre_usuario, correo_electronico=correo_electronico, contraseña=contraseña)
            db.session.add(usuario)
            db.session.commit()

        # Verificar si la plantilla existe
        plantilla = Plantilla.query.get(plantilla_id)
        if not plantilla:
            plantilla = Plantilla(imagen=imagen, nombre_plantilla=nombre_plantilla, usuario_id=usuario.usuario_id)
            db.session.add(plantilla)
            db.session.commit()

        # Crear un nuevo meme
        nuevo_meme = Meme(imagen=imagen, usuario_id=usuario.usuario_id, plantilla_id=plantilla.plantilla_id)
        db.session.add(nuevo_meme)
        db.session.commit()

        # Preparar la respuesta JSON
        respuesta_nuevo_meme = {
            'meme_id': nuevo_meme.meme_id,
            'imagen': nuevo_meme.imagen,
            'usuario_id': nuevo_meme.usuario_id,
            'plantilla_id': nuevo_meme.plantilla_id
        }

        return jsonify(respuesta_nuevo_meme), 201

    except Exception as error:
        print(f"Error al crear el meme: {str(error)}")
        return jsonify({'message': 'No se ha podido crear el meme.'}), 500


    
@app.route('/memes/<int:meme_id>', methods=['PUT'])
def editar_meme(meme_id):
    try:
        data = request.json

        # Buscar el meme en la base de datos por su ID
        meme = Meme.query.get(meme_id)

        if meme:
            # Actualizar los campos del meme según los datos proporcionados
            if 'imagen' in data:
                meme.imagen = data['imagen'][:300]  # Ajustar la longitud si es necesario
            if 'usuario_id' in data:
                meme.usuario_id = data['usuario_id']

            # Verificar y actualizar el plantilla_id si existe
            if 'plantilla_id' in data:
                plantilla_id = data['plantilla_id']
                plantilla = Plantilla.query.get(plantilla_id)
                if plantilla:
                    meme.plantilla_id = plantilla_id
                else:
                    return jsonify({'message': f'Plantilla con ID {plantilla_id} no encontrada'}), 404

            # Guardar los cambios en la base de datos
            db.session.commit()

            # Preparar la respuesta JSON con los datos actualizados
            meme_actualizado = {
                'meme_id': meme.meme_id,
                'imagen': meme.imagen,
                'fecha': meme.fecha.strftime('%Y-%m-%d %H:%M:%S'),
                'usuario_id': meme.usuario_id,
                'plantilla_id': meme.plantilla_id
            }

            return jsonify(meme_actualizado), 200
        else:
            return jsonify({'message': 'Meme no encontrado'}), 404

    except ValueError as verificacion:
        db.session.rollback()
        return jsonify({'message': str(verificacion)}), 400  # Bad Request
    except Exception as error:
        db.session.rollback()
        print(f"Error al editar el meme: {str(error)}")
        return jsonify({'message': 'No se ha podido editar el meme.'}), 500
    

@app.route('/memes/<int:meme_id>', methods=['DELETE'])
def eliminar_meme(meme_id):
    try:
        meme = Meme.query.get(meme_id)
        if meme is None:
            return jsonify({'message': 'El meme con el ID especificado no se encontró'}), 404

        db.session.delete(meme)
        db.session.commit()

        return jsonify({'message': 'Meme eliminado exitosamente'}), 200
    except Exception as error:
        print(f"Error al eliminar el meme: {str(error)}")
        db.session.rollback()
        return jsonify({'message': 'No se pudo eliminar el meme'}), 500


if __name__ == '__main__':
    print('Init server....')
    db.init_app(app)

    with app.app_context():
        db.create_all()

    app.run(host='0.0.0.0', debug=True, port=port)
    print('Started...')
