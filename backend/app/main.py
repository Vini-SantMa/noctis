from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session
import jwt
import random
from fastapi.middleware.cors import CORSMiddleware
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta

from . import models, schemas, security
from .database import engine, SessionLocal

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="NOCTIS API",
    description="Backend para o Game Tracker NOCTIS",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except Exception:
        raise credentials_exception
        
    user = db.query(models.User).filter(models.User.email == email).first()
    if user is None:
        raise credentials_exception
        
    return user

# Testse para um selecionador das platafomras

def get_plataforma_factory(plataforma: str):
    # retornar a fabrica correta, com base na string
   
    fabricas = { "steam": models.SteamFactory(), 
                 #"riot": models.RiotFactory(),
    }
    return fabricas.get(plataforma.lower())

def get_adapter_para_plataforma(plataforma: str, buscador_jogo, buscador_status):
    """
    Descobre qual é o tradutor (Adapter) correto para a plataforma solicitada.
    Se o usuário pedir Steam, devolve o SteamAdapter. Se pedir Riot, devolve RiotAdapter.
    """
    if plataforma.lower() == "steam":
        STEAM_API_KEY = "50A713B67631D0979739B7F996B831B6"
        return models.SteamAdapter(buscador_jogo, buscador_status, STEAM_API_KEY)
    
    # elif plataforma.lower() == "igdb": # A API do seu amigo entra aqui!
    #     return models.OutraApiAdapter(buscador_jogo, buscador_status)
    
    # elif plataforma.lower() == "riot": # A Riot que vamos criar entra aqui!
    #     return models.RiotAdapter(buscador_jogo, buscador_status, "CHAVE_DA_RIOT")
    
    raise ValueError(f"Adapter não configurado para a plataforma {plataforma}")

@app.get("/")
def root():
    return {"status": "online", "message": "Banco de dados e servidor online!"}

# ==========================================
# ROTA DE CADASTRO
# ==========================================
@app.post("/register", response_model=schemas.UserResponse)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Este e-mail já está em uso. Tente fazer login!")

    hashed_pwd = security.get_password_hash(user.password)

    new_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_pwd
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# ==========================================
# ROTA DE LOGIN
# ==========================================
@app.post("/login", response_model=schemas.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = security.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

# ==========================================
# ROTA PROTEGIDA (Perfil do Usuário Logado)
# ==========================================
@app.get("/users/me", response_model=schemas.UserResponse)
def read_users_me(current_user: models.User = Depends(get_current_user)):
    return current_user

# ==========================================
# ROTA PROTEGIDA (Atualizar Perfil)
# ==========================================
@app.put("/users/me", response_model=schemas.UserResponse)
def update_user_me(
    user_update: schemas.UserUpdate, 
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if user_update.username is not None:
        current_user.username = user_update.username
        
    if user_update.email is not None:
        email_existente = db.query(models.User).filter(models.User.email == user_update.email).first()
        if email_existente and email_existente.id != current_user.id:
            raise HTTPException(status_code=400, detail="Este e-mail já está em uso.")
        current_user.email = user_update.email
        
    if user_update.avatar is not None:
        current_user.avatar = user_update.avatar
        
    if user_update.password:
        current_user.hashed_password = security.get_password_hash(user_update.password)
        
    db.commit()
    db.refresh(current_user)
    return current_user

# ==========================================
# FUNÇÃO DE ENVIO DE E-MAIL
# ==========================================
def send_recovery_email(to_email: str, code: str):
    sender_email = "ryansilva132020@gmail.com"  
    sender_password = "ikyjrtgjimthpfzd" 

    msg = MIMEMultipart()
    msg['From'] = f"NOCTIS <{sender_email}>"
    msg['To'] = to_email
    msg['Subject'] = "NOCTIS - Código de Recuperação de Senha"

    body = f"""
Olá, Explorador(a)!
    
Você solicitou a redefinição de senha da sua conta no universo NOCTIS.
    
Seu código de verificação é: {code}
    
Este código expira em 15 minutos. Se você não solicitou isso, pode ignorar este e-mail.
"""
    
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        print(f"E-mail enviado com sucesso para {to_email}")
        return True
    except Exception as e:
        print(f"Erro ao enviar o e-mail: {e}")
        return False

# ==========================================
# ROTAS DE RECUPERAÇÃO DE SENHA
# ==========================================

@app.post("/password-recovery/request")
def request_password_recovery(recovery: schemas.PasswordRecoveryRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == recovery.email).first()
    
    if not user:
        return {"message": "Se o email estiver cadastrado, um código foi enviado."}

    db.query(models.RecoveryCode).filter(models.RecoveryCode.email == recovery.email).delete()

    code = str(random.randint(100000, 999999))
    expiration_time = datetime.utcnow() + timedelta(minutes=15)

    new_recovery = models.RecoveryCode(
        email=recovery.email,
        code=code,
        expires_at=expiration_time.isoformat()
    )
    db.add(new_recovery)
    db.commit()

    email_enviado = send_recovery_email(to_email=recovery.email, code=code)

    if not email_enviado:
        db.delete(new_recovery)
        db.commit()
        raise HTTPException(status_code=500, detail="Erro no servidor de e-mail. Tente novamente mais tarde.")

    return {"message": "Código de recuperação gerado."}

@app.post("/password-recovery/reset")
def reset_password(reset_data: schemas.PasswordReset, db: Session = Depends(get_db)):
    recovery_entry = db.query(models.RecoveryCode).filter(
        models.RecoveryCode.email == reset_data.email,
        models.RecoveryCode.code == reset_data.code
    ).first()
    
    if not recovery_entry:
        raise HTTPException(status_code=400, detail="Código inválido.")

    expires_at = datetime.fromisoformat(recovery_entry.expires_at)
    if datetime.utcnow() > expires_at:
        db.delete(recovery_entry)
        db.commit()
        raise HTTPException(status_code=400, detail="Este código expirou. Solicite um novo.")

    user = db.query(models.User).filter(models.User.email == reset_data.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")

    user.hashed_password = security.get_password_hash(reset_data.new_password)
    
    db.delete(recovery_entry)
    db.commit()

    return {"message": "Senha redefinida com sucesso!"}

# ==========================================
# ROTAS DA BIBLIOTECA (UserGame)
# ==========================================
# Possibilidade do bastract factory

@app.post("/importar/{plataforma}")
def importar_jogo_externo(
    plataforma: str, game_id_externo: str,
    player_id_externo: str, db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
): 
    # Solicita a fabrica certa (qual plataforma está trabalhando)
    fabrica = get_plataforma_factory(plataforma)
    if not fabrica:
        raise HTTPException(status_code = 400, detail = f"Plataforma ainda não suportada")
    
    # criação das ferramentas de busca
    buscador_jogo = fabrica.criar_buscador_jogos()
    buscador_status = fabrica.criar_buscador_status()
    
    try:
        adapter = get_adapter_para_plataforma(plataforma, buscador_jogo, buscador_status)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    #CUIDADO PRA NAO DEIXAR EXPOSTA
    
   
    dados_formatados = adapter.formatar_para_banco(game_id_externo, player_id_externo)
    
    # > Salvar no banco de dados > verificacao do jogo n biblioteca
    jogo_existente = db.query(models.UserGame).filter(
        models.UserGame.user_id == current_user.id,
        #models.UserGame.game_id == game_id_externo
        models.UserGame.game_id == dados_formatados["game_id"]
    ).first()
    
    if jogo_existente:
        # para jogos que o player ja tem, attualizar horas
        jogo_existente.horas_jogadas = dados_formatados["horas_jogadas"]
        jogo_existente.conquistas = dados_formatados["conquistas"]
        jogo_existente.capa = dados_formatados["capa"]
        db.commit()
        db.refresh(jogo_existente)
        resultado = jogo_existente
        msg = f"jogo atualizado com dados via {plataforma.capitalize()}!"
    else:
        #Caso o player nao tenha o jogo
        novo_jogo = models.UserGame( user_id = current_user.id, **dados_formatados)
        db.add(novo_jogo)
        db.commit()
        db.refresh(novo_jogo)
        resultado = novo_jogo
        msg = f"Jogo importado e adicionado em sua biblioteca via {plataforma.capitalize()}!"
    return{
        "mensagem": msg,
        "dados_salvos": resultado
    }
    
    """ #execucao das buscas, conforme os contratos ja definidos
    dados_do_jogo = buscador_jogo.buscar_detalhes_jogo(game_id_externo)
    estatisticas = buscador_status.buscar_status_jogador(player_id_externo) #adicao do argumento na funcao de busca de detalhes e status
    
     #Logica para salvar no banco de dados (ADICIONAAAAR)
     
    return { "mensagem": f"Importacao de {plataforma.capitalize()} concluida",
           "dados_jogo": dados_do_jogo, "estatisticas_jogador": estatisticas }
    """
@app.post("/sync/steam")
def sincronizar_biblioteca_steam_em_massa(
    player_id_externo: str, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    import requests
    import json
    
    STEAM_API_KEY = "50A713B67631D0979739B7F996B831B6"
    url = f"http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={STEAM_API_KEY}&steamid={player_id_externo}&include_appinfo=1&format=json"
    
    try:
        resposta = requests.get(url).json()
        
        # === BLINDAGEM NÍVEL DEUS (Contra qualquer formato da Steam) ===
        jogos = []
        if isinstance(resposta, dict):
            response_data = resposta.get("response", {})
            if isinstance(response_data, dict):
                jogos = response_data.get("games", [])
            elif isinstance(response_data, list):
                jogos = response_data
        elif isinstance(resposta, list):
            jogos = resposta
            
        # Garante que só vamos ler se for uma lista de dicionários válidos
        if isinstance(jogos, list):
            jogos = [j for j in jogos if isinstance(j, dict)]
        else:
            jogos = []
        # ===============================================================
        
        if not jogos:
            return {
                "mensagem": "Nenhum jogo encontrado. Verifique se o perfil da Steam está definido como Público!",
                "jogos_adicionados": 0
            }
        
        jogos_adicionados = 0
        jogos_atualizados = 0
        
        for jogo in jogos:
            appid = str(jogo.get("appid", ""))
            if not appid:
                continue # Pula se a Valve mandar lixo sem ID
                
            game_id_formatado = f"steam-{appid}"
            nome = jogo.get("name", "Jogo Steam")
            playtime_forever = jogo.get("playtime_forever", 0)
            
            horas = round(playtime_forever / 60.0, 1)
            capa = f"https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/{appid}/library_600x900.jpg"
            
            status_calculado = "Quero Jogar"
            if horas > 0:
                status_calculado = "Jogando"
                
            dados_jogo_fake_rawg = {
                "id": game_id_formatado,
                "name": nome,
                "title": nome,
                "cover": capa,
                "background_image": capa,
                "description": "Jogo importado via sincronização em massa da Steam.",
                "description_raw": "Jogo importado via sincronização em massa da Steam.",
                "releaseYear": "Desconhecido",
                "developer": "Desconhecida",
                "genres": []
            }
            
            jogo_existente = db.query(models.UserGame).filter(
                models.UserGame.user_id == current_user.id,
                models.UserGame.game_id == game_id_formatado
            ).first()
            
            if jogo_existente:
                jogo_existente.horas_jogadas = horas
                jogo_existente.status_principal = status_calculado
                jogo_existente.capa = capa
                jogo_existente.dados_jogo = json.dumps(dados_jogo_fake_rawg)
                jogos_atualizados += 1
            else:
                novo_jogo = models.UserGame(
                    user_id=current_user.id,
                    game_id=game_id_formatado,
                    titulo=nome,
                    capa=capa,
                    dados_jogo=json.dumps(dados_jogo_fake_rawg),
                    status_principal=status_calculado,
                    horas_jogadas=horas,
                    favorito=False,
                    conquistas="{}"
                )
                db.add(novo_jogo)
                jogos_adicionados += 1
                
        db.commit()
        return {
            "mensagem": f"Sincronização completa! Adicionados: {jogos_adicionados} | Atualizados: {jogos_atualizados}",
            "total_jogos_processados": len(jogos)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Falha crítica na comunicação com a API da Valve: {str(e)}"
        )
            
            
    
@app.post("/biblioteca", response_model=schemas.UserGameResponse)
def adicionar_ou_atualizar_jogo(
    game_data: schemas.UserGameCreate, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_user)
):
    
    # APLICACAO DO STATE PRA VERIFICAR VALIDADE DE AVALIACAO
    
    from .state import ContextoAvaliacao #Regra com state
    #Validar o state
    if game_data.nota_geral is not None:
        contexto = ContextoAvaliacao(game_data.status_principal)
        resultado = contexto.tentar_avaliar(game_data.nota_geral)
        
        if not resultado["sucesso"]:
            raise HTTPException(status_code=400, detail = resultado["erro"])
        
        
    jogo_existente = db.query(models.UserGame).filter(
        models.UserGame.user_id == current_user.id,
        models.UserGame.game_id == game_data.game_id
    ).first()
# Codigo decidindo na hora, o que salvar
    if jogo_existente:
        jogo_existente.status_principal = game_data.status_principal
        if game_data.titulo: jogo_existente.titulo = game_data.titulo
        if game_data.capa: jogo_existente.capa = game_data.capa
        if game_data.dados_jogo: jogo_existente.dados_jogo = game_data.dados_jogo 
        jogo_existente.favorito = game_data.favorito
        jogo_existente.horas_jogadas = game_data.horas_jogadas
        jogo_existente.nota_geral = game_data.nota_geral
        jogo_existente.comentario = game_data.comentario
        jogo_existente.criterios = game_data.criterios
        jogo_existente.conquistas = game_data.conquistas
        jogo_existente.conquistas_personalizadas = game_data.conquistas_personalizadas
        
        db.commit()
        db.refresh(jogo_existente)
        return jogo_existente
    else: # Varios campos preeenchidos manualmente
        novo_jogo = models.UserGame(
            user_id=current_user.id,
            game_id=game_data.game_id,
            titulo=game_data.titulo,
            capa=game_data.capa,
            dados_jogo=game_data.dados_jogo,
            status_principal=game_data.status_principal,
            favorito=game_data.favorito,
            horas_jogadas=game_data.horas_jogadas,
            nota_geral=game_data.nota_geral,
            comentario=game_data.comentario,
            criterios=game_data.criterios,
            conquistas=game_data.conquistas,
            conquistas_personalizadas=game_data.conquistas_personalizadas
        )
        db.add(novo_jogo)
        db.commit()
        db.refresh(novo_jogo)
        return novo_jogo

@app.get("/biblioteca", response_model=list[schemas.UserGameResponse])
def listar_minha_biblioteca(
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_user)
):
    meus_jogos = db.query(models.UserGame).filter(models.UserGame.user_id == current_user.id).all()
    return meus_jogos

@app.delete("/biblioteca/{game_id}")
def remover_da_biblioteca(
    game_id: str, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_user)
):
    jogo_na_biblioteca = db.query(models.UserGame).filter(
        models.UserGame.user_id == current_user.id,
        models.UserGame.game_id == game_id
    ).first()

    if not jogo_na_biblioteca:
        raise HTTPException(
            status_code=404, 
            detail="Este jogo não está na sua biblioteca."
        )

    db.delete(jogo_na_biblioteca)
    db.commit()
    return {"message": "Jogo removido da galáxia com sucesso!"}

# ==========================================
# ROTAS DE LISTAS PERSONALIZADAS
# ==========================================

@app.get("/listas", response_model=list[schemas.ListaResponse])
def get_listas(user = Depends(get_current_user), db: Session = Depends(get_db)):
    listas = db.query(models.Lista).filter(models.Lista.user_id == user.id).all()
    return listas

@app.post("/listas")
def save_lista(lista_data: schemas.ListaCreate, user = Depends(get_current_user), db: Session = Depends(get_db)):
    lista_existente = db.query(models.Lista).filter(
        models.Lista.list_id == lista_data.list_id, 
        models.Lista.user_id == user.id
    ).first()
    
    if lista_existente:
        lista_existente.nome = lista_data.nome
        lista_existente.descricao = lista_data.descricao
        lista_existente.jogos = lista_data.jogos
    else:
        nova_lista = models.Lista(
            user_id=user.id,
            list_id=lista_data.list_id,
            nome=lista_data.nome,
            descricao=lista_data.descricao,
            jogos=lista_data.jogos,
            criado_em=lista_data.criado_em
        )
        db.add(nova_lista)
    
    db.commit()
    return {"message": "Lista salva com sucesso!"}

@app.delete("/listas/{list_id}")
def delete_lista(list_id: str, user = Depends(get_current_user), db: Session = Depends(get_db)):
    lista = db.query(models.Lista).filter(
        models.Lista.list_id == list_id, 
        models.Lista.user_id == user.id
    ).first()
    
    if lista:
        db.delete(lista)
        db.commit()
        return {"message": "Lista deletada com sucesso!"}
    
    raise HTTPException(status_code=404, detail="Lista não encontrada")
