from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

# Configurações de tempo
TEMPO_MAX_CARREGAMENTO = 120  # Tempo máximo para a página carregar (segundos)
TEMPO_VERIFICAR_TOKEN = 30    # Tempo total tentando ler o token (segundos)
TEMPO_ENTRE_TENTATIVAS = 1    # Intervalo entre tentativas de ler o token

def coletar_token(email, senha):
    """
    Função para logar na HiPlatform, acessar a página de destino e capturar o token dt.admin.token.
    Retorna o token como string ou None se não for encontrado.
    """
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Executa sem abrir o navegador (modo invisível)
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-blink-features=AutomationControlled')

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        print("🚀 Acessando página de login...")
        driver.get("https://horus.hiplatform.com/")
        wait = WebDriverWait(driver, 40)

        # 1. Clica no botão "Continuar"
        continuar_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@value='Continuar']")))
        continuar_btn.click()
        print("✅ Botão CONTINUAR clicado!")
        time.sleep(3)

        # 2. Preenche login e senha
        email_input = wait.until(EC.presence_of_element_located((By.ID, "login_login")))
        email_input.clear()
        email_input.send_keys(email)

        senha_input = wait.until(EC.presence_of_element_located((By.ID, "login_password")))
        senha_input.clear()
        senha_input.send_keys(senha)
        time.sleep(2)

        # 3. Clica no botão "Entrar"
        entrar_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@value='Entrar' and not(@disabled)]")))
        entrar_btn.click()
        print("✅ Botão ENTRAR clicado!")

        # 4. Espera o redirecionamento para /products
        wait.until(EC.url_contains("/products"))
        print("✅ Página de produtos carregada!")
        time.sleep(3)

        # 5. Navega para a página final que garante injeção do token
        final_url = "https://www5.directtalk.com.br/static/beta/admin/main.html#!/home/index?depto=-1"
        driver.get(final_url)
        print("🚀 Acessando página final (home/index)...")

        # 6. Aguarda carregamento completo da página
        print("⏳ Aguardando carregamento da página...")
        wait_final = WebDriverWait(driver, TEMPO_MAX_CARREGAMENTO)
        wait_final.until(lambda d: d.execute_script("return document.readyState") == "complete")
        print("✅ Página carregada com sucesso!")

        # 7. Tenta capturar o token do localStorage
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
