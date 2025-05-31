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
# FUNÇÃO BÁSICA DE COLETA DE TOKEN
# ===============================
def coletar_token(email, senha):
    # Configurações mínimas do Chrome em headless
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    # Inicializa o driver
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

    try:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Iniciando login...")
        driver.get("https://horus.hiplatform.com/")
        wait = WebDriverWait(driver, 30)

        # Clica em "Continuar" se aparecer
        try:
            btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@value='Continuar']")))
            btn.click()
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Botão CONTINUAR clicado")
            time.sleep(2)
        except:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Botão CONTINUAR não apareceu, seguindo login")

        # Preenche email e senha
        inp = wait.until(EC.presence_of_element_located((By.ID, "login_login")))
        inp.clear()
        inp.send_keys(email)
        pwd = wait.until(EC.presence_of_element_located((By.ID, "login_password")))
        pwd.clear()
        pwd.send_keys(senha)
        time.sleep(1)

        # Clica em Entrar
        enter_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@value='Entrar' and not(@disabled)]")))
        enter_btn.click()
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Botão ENTRAR clicado")

        # Aguarda /products carregar
        wait.until(EC.url_contains("/products"))
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Página de produtos carregada")
        time.sleep(2)

        # Navega para página de relatórios
        driver.get(RELATORIO_URL)
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Acessando relatório")

        # Espera até relatório carregar (máx 60s)
        inicio = time.time()
        while time.time() - inicio < 60:
            if "hsmReports" in driver.current_url and driver.execute_script("return document.readyState") == "complete":
                break
            time.sleep(2)
        else:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Tempo limite ao carregar relatório")
            return None

        # Captura token
        token = driver.execute_script("return window.localStorage.getItem('dt.admin.token');")
        if token:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] TOKEN: {token}")
            return token
        else:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Token não encontrado")
            return None

    finally:
        driver.quit()
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Navegador fechado")

# ===============================
# EXECUÇÃO
# ===============================
if __name__ == "__main__":
    token = coletar_token(EMAIL, SENHA)
    if not token:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Falha ao coletar token")
