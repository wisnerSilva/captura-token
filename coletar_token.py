import os
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# ===============================
# VARIÁVEIS DE AMBIENTE
# ===============================
EMAIL = os.environ.get("EMAIL_HIPLAT")
SENHA = os.environ.get("SENHA_HIPLAT")
RELATORIO_URL = os.environ.get("RELATORIO_URL")

# ===============================
# FUNÇÃO DE COLETA DE TOKEN COM LOGS DETALHADOS E TRATAMENTO DE ERRO
# ===============================

def coletar_token(email, senha):
    timestamp = lambda: datetime.now().strftime('%H:%M:%S')
    print(f"[{timestamp()}] Iniciando função coletar_token")

    # Configurando opções do Chrome
    try:
        print(f"[{timestamp()}] Configurando ChromeOptions")
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-software-rasterizer')
        print(f"[{timestamp()}] ChromeOptions configuradas")
    except Exception as e:
        print(f"[{timestamp()}] Erro ao configurar ChromeOptions: {e}")
        return None

    # Inicializa o driver
    try:
        print(f"[{timestamp()}] Inicializando ChromeDriver")
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )
        print(f"[{timestamp()}] ChromeDriver iniciado com sucesso")
    except Exception as e:
        print(f"[{timestamp()}] ERRO ao iniciar ChromeDriver: {e.__class__.__name__}: {e}")
        return None

    try:
        # Acessar página de login
        print(f"[{timestamp()}] Acessando URL de login: https://horus.hiplatform.com/")
        driver.get("https://horus.hiplatform.com/")
        wait = WebDriverWait(driver, 30)
        print(f"[{timestamp()}] Página de login carregada, iniciando interação")

        # Clica em "Continuar" se aparecer
        try:
            print(f"[{timestamp()}] Verificando botão CONTINUAR")
            btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@value='Continuar']")))
            btn.click()
            print(f"[{timestamp()}] Botão CONTINUAR clicado")
            time.sleep(2)
        except Exception as e:
            print(f"[{timestamp()}] Botão CONTINUAR não apareceu ou erro: {e}, prosseguindo sem clicar")

        # Preenchendo credenciais
        try:
            print(f"[{timestamp()}] Buscando campo de e-mail")
            inp = wait.until(EC.presence_of_element_located((By.ID, "login_login")))
            inp.clear()
            inp.send_keys(email)
            print(f"[{timestamp()}] E-mail preenchido")
        except Exception as e:
            print(f"[{timestamp()}] Erro ao preencher e-mail: {e}")
            return None

        try:
            print(f"[{timestamp()}] Buscando campo de senha")
            pwd = wait.until(EC.presence_of_element_located((By.ID, "login_password")))
            pwd.clear()
            pwd.send_keys(senha)
            print(f"[{timestamp()}] Senha preenchida")
        except Exception as e:
            print(f"[{timestamp()}] Erro ao preencher senha: {e}")
            return None

        time.sleep(1)
        # Clica em Entrar
        try:
            print(f"[{timestamp()}] Verificando botão ENTRAR")
            enter_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@value='Entrar' and not(@disabled)]")))
            enter_btn.click()
            print(f"[{timestamp()}] Botão ENTRAR clicado")
        except Exception as e:
            print(f"[{timestamp()}] Erro ao clicar ENTRAR: {e}")
            return None

        # Aguarda URL /products
        try:
            print(f"[{timestamp()}] Aguardando redirecionamento para /products")
            wait.until(EC.url_contains("/products"))
            print(f"[{timestamp()}] Redirecionamento confirmado, página de produtos carregada")
        except Exception as e:
            print(f"[{timestamp()}] Timeout aguardando /products: {e}")
            return None

        time.sleep(2)
        # Navega para relatório
        try:
            print(f"[{timestamp()}] Navegando para URL do relatório: {RELATORIO_URL}")
            driver.get(RELATORIO_URL)
            print(f"[{timestamp()}] URL de relatório carregada (current_url: {driver.current_url})")
        except Exception as e:
            print(f"[{timestamp()}] Erro ao carregar relatório: {e}")
            return None

        # Espera carregamento completo do relatório (até 60s)
        print(f"[{timestamp()}] Iniciando loop de verificação do carregamento do relatório")
        inicio = time.time()
        carregado = False
        while time.time() - inicio < 60:
            current_url = driver.current_url
            try:
                ready_state = driver.execute_script("return document.readyState")
            except Exception as e:
                print(f"[{timestamp()}] Erro ao ler readyState: {e}")
                ready_state = ''
            print(f"[{timestamp()}] URL atual: {current_url}, readyState: {ready_state}")
            if "hsmReports" in current_url and ready_state == "complete":
                carregado = True
                print(f"[{timestamp()}] Relatório carregado totalmente")
                break
            time.sleep(2)
        if not carregado:
            print(f"[{timestamp()}] Tempo limite ao carregar relatório")
            return None

        # Captura token
        try:
            print(f"[{timestamp()}] Capturando token do localStorage")
            token = driver.execute_script("return window.localStorage.getItem('dt.admin.token');")
            if token:
                print(f"[{timestamp()}] TOKEN capturado: {token}")
                return token
            else:
                print(f"[{timestamp()}] Token não encontrado no localStorage")
                return None
        except Exception as e:
            print(f"[{timestamp()}] Erro ao capturar token: {e}")
            return None

    finally:
        print(f"[{timestamp()}] Fechando navegador")
        try:
            driver.quit()
        except Exception as e:
            print(f"[{timestamp()}] Erro ao fechar navegador: {e}")

# ===============================
# EXECUÇÃO
# ===============================
if __name__ == "__main__":
    print(f"[{timestamp()}] Iniciando execução principal")
    token = coletar_token(EMAIL, SENHA)
    if not token:
        print(f"[{timestamp()}] Falha ao coletar token")
