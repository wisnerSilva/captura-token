import os
import requests
from datetime import datetime, timezone
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
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

supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
headers = {"apikey": SUPABASE_SERVICE_KEY, "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}"}

# ===============================
# COLETA DE TOKEN VIA SELENIUM
# ===============================
def iniciar_driver():
    options = webdriver.ChromeOptions()
    # Rodar em headless com flags mínimas para CI
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    # Remove flags extras que podem causar conflitos
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    options.add_experimental_option('useAutomationExtension', False)

    # Inicializa o driver com versão compatível
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver


def fazer_login(driver, email, senha, timeout=20):
    wait = WebDriverWait(driver, timeout)
    driver.get("https://horus.hiplatform.com/")
    try:
        btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@value='Continuar']")))
        btn.click()
    except:
        pass
    email_inp = wait.until(EC.presence_of_element_located((By.ID, "login_login")))
    email_inp.clear(); email_inp.send_keys(email)
    pwd = wait.until(EC.presence_of_element_located((By.ID, "login_password")))
    pwd.clear(); pwd.send_keys(senha)
    submit = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@value='Entrar' and not(@disabled)]")))
    submit.click()
    wait.until(EC.url_contains("/products"))


def coletar_token(email, senha, url, max_wait=60):
    driver = iniciar_driver()
    try:
        fazer_login(driver, email, senha)
        driver.get(url)
        wait = WebDriverWait(driver, max_wait)
        token = wait.until(lambda d: d.execute_script(
            "return window.localStorage.getItem('dt.admin.token');"
        ))
        return token
    except Exception as e:
        print("Erro ao coletar token:", e)
        return None
    finally:
        driver.quit()

# ===============================
# SUPABASE STORAGE & TABELA
# ===============================
def criar_bucket_se_nao_existir():
    url = f"{SUPABASE_URL}/storage/v1/bucket"
    body = {"name": BUCKET_NAME, "public": False}
    r = requests.post(url, headers=headers, json=body)
    if r.status_code not in (200, 400):
        print(f"Aviso criar bucket: {r.status_code} - {r.text}")


def salvar_token_no_bucket(token):
    criar_bucket_se_nao_existir()
    ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    fn = f"{ts}.txt"
    url = f"{SUPABASE_URL}/storage/v1/object/{BUCKET_NAME}/{fn}"
    hdrs = headers.copy(); hdrs["Content-Type"] = "text/plain"
    requests.post(url, headers=hdrs, data=token.encode('utf-8'))


def salvar_token_na_tabela(token):
    ts = datetime.now(timezone.utc).isoformat()
    supabase.table(TABLE_NAME).insert({"token": token, "created_at": ts}).execute()


if __name__ == "__main__":
    token = coletar_token(EMAIL, SENHA, RELATORIO_URL)
    if token:
        salvar_token_no_bucket(token)
        salvar_token_na_tabela(token)
    else:
        print("Token não coletado.")
