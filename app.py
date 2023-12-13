from sqlalchemy.exc import IntegrityError
from flask_openapi3 import OpenAPI
from flask_cors import CORS
from flask_openapi3 import Info, Tag
from flask import redirect, jsonify, request, send_from_directory
from model import Session, Viagem
from werkzeug.utils import secure_filename
from werkzeug.exceptions import NotFound
from PIL import Image
from logger import logger
from schemas import *
import io
import uuid
import os

UPLOAD_FOLDER = "temp_data/temp_images"
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

info = Info(title="Minha Querida API de Viagens", version="1.0.0")
app = OpenAPI(__name__, info=info)
CORS(app)
# Definindo tags
viagem_tag = Tag(name="Viagem", description="Cadastro e listagem de viagens")

# Rota das imagens
@app.route('/static/images/<filename>')
def enviar_imagem(filename):
    return send_from_directory('temp_data/temp_images', filename)

# Validando o formato das imagens
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Rota das imagens
def image_name_modify(filename):
    # Gere um nome único para a imagem usando UUID
    unique_filename = str(uuid.uuid4()) + os.path.splitext(filename)[-1]
    return unique_filename 

# Armazenando as imagens local
def upload_local_images(fotos):
    filesnames_fotos = []

    for i, foto in enumerate(fotos):
        print(f"Tamanho da Foto {i + 1}: {len(foto.read())} bytes")

        if not allowed_file(foto.filename):
            error_msg = "Fotos com formatos incompatíveis"
            logger.warning(f"Erro ao deletar viagem #'{filename}', {error_msg}")
            return {"mesage": error_msg}, 400
        
        filename = secure_filename(foto.filename)
        filename_foto = image_name_modify(filename)

        foto.seek(0)

        image_data = foto.read()
        image = Image.open(io.BytesIO(image_data))

        local_path = os.path.join(UPLOAD_FOLDER, filename_foto)
        image.save(local_path)

        filesnames_fotos.append(filename_foto)

    return filesnames_fotos

@app.get('/')
def home():
    return redirect('/openapi')

@app.post('/viagem', tags=[viagem_tag],
          responses={"200": ViagemViewSchema, "409": ErrorSchema, "400": ErrorSchema})
def adicionar_viagem(form: ViagemSchema):
    """Adiciona uma nova viagem à base de dados

    Retorna uma representação da viagem adicionada.
    """
    # Url da Raiz da API
    api_url = request.url_root

     # Executa a função de upload das imagens
    local_urls = upload_local_images(form.fotos)

    # Adiciona a URL da API 
    urls_with_api = [f"{api_url}static/images/{url}" for url in local_urls]
    session = Session()
    viagem = Viagem(
        destino=form.destino,
        detalhes=form.detalhes,
        rating=form.rating,
        fotos=','.join(urls_with_api)
        )
    logger.debug(f"Adicionando produto de nome: '{form.destino}'")
    try:
        # Adicionando viagem   
        session.add(viagem)
        session.commit()

        logger.debug(f"Adicionada viagem para o destino: '{viagem.destino}'")
        return apresenta_viagem(viagem), 200
    
    except IntegrityError as e:
        session.rollback()
        error_msg = f"Erro de validação: {e}"
        logger.warning(f"Erro ao adicionar viagem para '{form.destino}', {error_msg}")
        return {"message": error_msg, "details": str(e)}, 409
    
    except Exception as e:
        error_msg = "Não foi possível salvar a nova viagem :/"
        logger.warning(f"Erro ao adicionar viagem para '{form.destino}', {error_msg}")
        return {"message": error_msg}, 400

@app.get('/viagens', tags=[viagem_tag],
         responses={"200": ViagemListaViewSchema, "404": ErrorSchema})
def obter_viagens():
    """Obtém a lista de todas as viagens cadastradas na base

    Retorna uma lista de representações de viagens.
    """
    logger.debug("Coletando lista de viagens")
    session = Session()
    viagens = session.query(Viagem).all()
    if not viagens:
        error_msg = "Nenhuma viagem encontrada na base :/"
      #  logger.warning(f"Erro ao buscar lista de viagens. {error_msg}")
        return {"message": error_msg}, 404
    else:
      #  logger.debug("Retornando lista de viagens")
        return apresenta_lista_viagem(viagens), 200

@app.put('/viagem', tags=[viagem_tag],
         responses={"200": {}, "404": {"description": "Viagem não encontrada"}, "400": {"description": "Erro durante a atualização"}})
def atualizar_viagem(form: ViagemUpdateSchema):
    """Atualiza uma viagem a partir do id informado

    Retorna uma mensagem de confirmação.
    """
     
    viagem_id = form.id
    session = Session()

    # Obter a viagem existente pelo ID
    viagem = session.query(Viagem).filter(Viagem.id == viagem_id).first()

    if not viagem:
        raise NotFound("Viagem não encontrada")
    
    try:
        # Lógica para atualizar fotos apenas se houver fotos novas
        if form.fotos:
            fotos = form.fotos
            local_urls = upload_local_images(fotos)
            urls_with_api = [f"{request.url_root}static/images/{url}" for url in local_urls]
            viagem.fotos = ','.join(urls_with_api)

        # Atualiza os campos da viagem
        if form.destino is not None:
            viagem.destino = form.destino
        if form.detalhes is not None:
            viagem.detalhes = form.detalhes
        if form.rating is not None:
            viagem.rating = form.rating

        # Efetiva a atualização na base de dados
        session.commit()

        logger.debug(f"Viagem atualizada para o destino: '{viagem.destino}'")
        return jsonify({"message": "Viagem atualizada com sucesso"}), 200
    
    except IntegrityError as e:
        session.rollback()
        error_msg = f"Erro de validação: {e}"
        logger.warning(f"Erro ao atualizar viagem para '{form.destino}', {error_msg}")
        return jsonify({"message": error_msg, "details": str(e)}), 409
    
    except Exception as e:
        error_msg = "Não foi possível atualizar a viagem :/"
        logger.warning(f"Erro ao atualizar viagem para '{viagem.destino}', {error_msg}")
        return jsonify({"message": error_msg}), 400

@app.delete('/viagem', tags=[viagem_tag],
            responses={"200": ViagemViewSchema, "404": ErrorSchema})
def del_viagem(form: ViagemDelSchema):
    """Deleta um Viagem a partir do id informado

    Retorna uma mensagem de confirmação da remoção.
    """
    viagem_id = form.id
    
    logger.debug(f"Deletando dados da viagem #{viagem_id}")
    session = Session()

    if viagem_id:
        count = session.query(Viagem).filter(Viagem.id == viagem_id).delete()
    else:
        error_msg = "Viagem não encontrada na base de dados :/"
        logger.warning(f"Erro ao deletar viagem #'{viagem_id}', {error_msg}")
        return {"message": error_msg}, 422
    logger.debug(f"Viagem a ser excluída #{viagem_id}")
    session.commit()
    if count:
        logger.debug(f"Viagem deletada #{viagem_id}")
        return {"id": viagem_id}
    else: 
        error_msg = "Viagem não encontrada na base de dados :/"
        logger.warning(f"Erro ao deletar viagem #'{viagem_id}', {error_msg}")
        return {"message": error_msg}, 400
