from flask import Flask, request, jsonify
from models import db, Meme, Plantilla, Usuario

app = Flask(__name__)
port = 5000
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:postgres@localhost:5432/intro'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

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

if __name__ == '__main__':
    print('Init server....')
    db.init_app(app)

    with app.app_context():
        db.create_all()

    app.run(host='0.0.0.0', debug=True, port=port)
    print('Started...')
