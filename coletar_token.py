from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

# ===============================
# CONFIGURAÇÕES
# ===============================
TEMPO_MAX_CARREGAMENTO = 120  # Tempo máx. para carregamento (segundos)
TEMPO_VERIFICAR_TOKEN = 30    # Tempo tentando capturar o token
TEMPO_ENTRE_TENTATIVAS = 1    # Intervalo entre tentativas de leitura

# ===============================
# COLETAR TOKEN
# ===============================
def coletar_token(email, senha):
    """
    Loga na HiPlatform, acessa relatórios e captura token do localStorage.
    """
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
        print("🚀 Acessando página de login...")
        driver.get("https://horus.hiplatform.com/")

        # Etapa 1: Clicar em "Continuar" se existir
        try:
            continuar_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@value='Continuar']")))
            continuar_btn.click()
            print("✅ Botão CONTINUAR clicado!")
            time.sleep(3)
        except:
            pass

        # Etapa 2: Login
        email_input = wait.until(EC.presence_of_element_located((By.ID, "login_login")))
        email_input.clear()
        email_input.send_keys(email)

        senha_input = wait.until(EC.presence_of_element_located((By.ID, "login_password")))
        senha_input.clear()
        senha_input.send_keys(senha)

        time.sleep(2)

        entrar_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@value='Entrar' and not(@disabled)]")))
        entrar_btn.click()
        print("✅ Botão ENTRAR clicado!")

        # Etapa 3: Esperar redirecionamento
        wait.until(EC.url_contains("/products"))
        print("✅ Página de produtos carregada!")
        time.sleep(3)

        # Etapa 4: Navegar para a página de relatório
        relatorio_url = "https://www5.directtalk.com.br/static/beta/admin/main.html#!/relatorios/hsmReports?depto=-1"
        driver.get(relatorio_url)
        print("🚀 Acessando página de relatórios...")

        relatorio_carregado = False
        inicio = time.time()

        while time.time() - inicio < TEMPO_MAX_CARREGAMENTO:
            time.sleep(5)
            current_url = driver.current_url
            if "hsmReports" in current_url:
                estado = driver.execute_script("return document.readyState")
                if estado == "complete":
                    relatorio_carregado = True
                    break

        if not relatorio_carregado:
            print("⚠️ Página de relatório não carregou.")
            return None

        # Etapa 5: Forçar ir para home/index para garantir token injetado
        final_url = "https://www5.directtalk.com.br/static/beta/admin/main.html#!/home/index?depto=-1"
        driver.get(final_url)
        print("🚀 Acessando página final (home/index)...")
        wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
        print("✅ Página carregada com sucesso!")

        # Etapa 6: Capturar token do localStorage
        token = None
        inicio = time.time()
        while time.time() - inicio < TEMPO_VERIFICAR_TOKEN:
            token = driver.execute_script("return window.localStorage.getItem('dt.admin.token');")
            if token:
                break
            time.sleep(TEMPO_ENTRE_TENTATIVAS)

        if token:
            print("✅ TOKEN CAPTURADO COM SUCESSO!")
            print("🔐 DT-Fenix-Token:", token)
            return token
        else:
            print("❌ Token não encontrado no localStorage.")
            return None

    finally:
        driver.quit()
        print("🛑 Navegador encerrado.")

# ===============================
# EXECUÇÃO DE TESTE LOCAL
# ===============================
if __name__ == "__main__":
    email = "wisner.silva@queimadiaria.com.br"
    senha = "Wisner432"

    token = coletar_token(email, senha)

    if token:
        with open("token.txt", "w") as f:
            f.write(token)
        print("📄 Token salvo em 'token.txt'!")
    else:
        print("❌ Não foi possível capturar o token.")
