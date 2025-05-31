
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

TEMPO_MAX_CARREGAMENTO = 120
TEMPO_VERIFICAR_TOKEN = 30
TEMPO_ENTRE_TENTATIVAS = 1

def coletar_token(email, senha):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--window-size=1920,1080')

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        wait = WebDriverWait(driver, 40)
        driver.get("https://horus.hiplatform.com/")

        try:
            continuar_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@value='Continuar']")))
            continuar_btn.click()
            time.sleep(3)
        except:
            pass

        email_input = wait.until(EC.presence_of_element_located((By.ID, "login_login")))
        email_input.clear()
        email_input.send_keys(email)

        senha_input = wait.until(EC.presence_of_element_located((By.ID, "login_password")))
        senha_input.clear()
        senha_input.send_keys(senha)

        time.sleep(2)

        entrar_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@value='Entrar' and not(@disabled)]")))
        entrar_btn.click()

        wait.until(EC.url_contains("/products"))
        time.sleep(3)

        relatorio_url = "https://www5.directtalk.com.br/static/beta/admin/main.html#!/relatorios/hsmReports?depto=-1"
        driver.get(relatorio_url)

        relatorio_carregado = False
        inicio = time.time()

        while time.time() - inicio < TEMPO_MAX_CARREGAMENTO:
            time.sleep(5)
            if "hsmReports" in driver.current_url:
                if driver.execute_script("return document.readyState") == "complete":
                    relatorio_carregado = True
                    break

        if not relatorio_carregado:
            return None

        final_url = "https://www5.directtalk.com.br/static/beta/admin/main.html#!/home/index?depto=-1"
        driver.get(final_url)
        wait.until(lambda d: d.execute_script("return document.readyState") == "complete")

        token = None
        inicio = time.time()
        while time.time() - inicio < TEMPO_VERIFICAR_TOKEN:
            token = driver.execute_script("return window.localStorage.getItem('dt.admin.token');")
            if token:
                break
            time.sleep(TEMPO_ENTRE_TENTATIVAS)

        return token

    finally:
        driver.quit()

if __name__ == "__main__":
    email = "wisner.silva@queimadiaria.com.br"
    senha = "Wisner432"

    token = coletar_token(email, senha)
    if token:
        with open("token.txt", "w") as f:
            f.write(token)
        print("Token salvo!")
    else:
        print("Token não foi encontrado.")
