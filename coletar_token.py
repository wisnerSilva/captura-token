import os
import time
import requests
from datetime import datetime, timezone
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from supabase import create_client, Client

# ===============================
# CONFIGURAÇÃO VIA VARIÁVEIS DE AMBIENTE
# ===============================
EMAIL = os.environ.get("EMAIL_HIPLAT")
SENHA = os.environ.get("SENHA_HIPLAT")
RELATORIO_URL = os.environ.get("RELATORIO_URL")
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_KEY")
TABLE_NAME = os.environ.get("SUPABASE_TABLE_NAME")
BUCKET_NAME = os.environ.get("SUPABASE_BUCKET")

# Inicializa cliente Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
headers = {"apikey": SUPABASE_SERVICE_KEY, "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}"}

# ===============================
# FUNÇÃO PARA COLETAR TOKEN VIA SELENIUM
# ===============================
def coletar_token(email, senha):
    """
    Loga na HiPlatform, navega até a página de relatórios e retorna o token armazenado em localStorage.
    """
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-blink-features=AutomationControlled')

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

    try:
        print("🚀 Acessando página de login...")
        driver.get("https://horus.hiplatform.com/")
        wait = WebDriverWait(driver, 40)

        # Clica em "Continuar"
        try:
            btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@value='Continuar']")))
            btn.click()
            print("✅ CONTINUAR clicado")
            time.sleep(5)
        except:
            pass

        # Preenche credenciais e entra
        inp = wait.until(EC.presence_of_element_located((By.ID, "login_login")))
        inp.clear(); inp.send_keys(email)
        pwd = wait.until(EC.presence_of_element_located((By.ID, "login_password")))
        pwd.clear(); pwd.send_keys(senha)
        time.sleep(3)
        enter_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@value='Entrar' and not(@disabled)]")))
        enter_btn.click()
        print("✅ ENTRAR clicado")

        # Aguarda página de produtos
        wait.until(EC.url_contains("/products"))
        print("✅ Página de produtos carregada")
        time.sleep(5)

        # Navega para relatório
        driver.get(RELATORIO_URL)
        print("🚀 Acessando página de relatórios...")

        # Espera até 2 minutos pelo carregamento completo
        inicio = time.time()
        while time.time() - inicio < 120:
            time.sleep(5)
            if "hsmReports" in driver.current_url:
                ready = driver.execute_script("return document.readyState")
                if ready == "complete":
                    break
        else:
            print("⚠️ Relatório não carregou em 2 minutos")
            return None

        # Captura token do localStorage
        time.sleep(5)
        token = driver.execute_script("return window.localStorage.getItem('dt.admin.token');")
        if token:
            print("✅ TOKEN CAPTURADO")
            return token
        else:
            print("❌ Token não encontrado")
            return None
    finally:
        driver.quit()
        print("🌐 Navegador fechado")

# ===============================
# FUNÇÕES SUPABASE
# ===============================
def criar_bucket():
    url = f"{SUPABASE_URL}/storage/v1/bucket"
    body = {"name": BUCKET_NAME, "public": False}
    r = requests.post(url, headers=headers, json=body)
    if r.status_code not in (200, 400):
        print(f"Erro ao criar bucket: {r.status_code}")


def salvar_no_bucket(token):
    criar_bucket()
    ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    fn = f"{ts}.txt"
    url = f"{SUPABASE_URL}/storage/v1/object/{BUCKET_NAME}/{fn}"
    hdrs = headers.copy(); hdrs["Content-Type"] = "text/plain"
    requests.post(url, headers=hdrs, data=token.encode('utf-8'))
    print(f"✅ Token salvo no bucket: {fn}")


def salvar_na_tabela(token):
    ts = datetime.now(timezone.utc).isoformat()
    supabase.table(TABLE_NAME).insert({"token": token, "created_at": ts}).execute()
    print("✅ Token salvo na tabela")

# ===============================
# FLUXO PRINCIPAL
# ===============================
if __name__ == "__main__":
    token = coletar_token(EMAIL, SENHA)
    if token:
        salvar_no_bucket(token)
        salvar_na_tabela(token)
    else:
        print("❌ Falha ao coletar token.")
