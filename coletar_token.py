from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

def coletar_token(email, senha):
    """
    Função para logar na HiPlatform, acessar a página de relatórios e capturar o token dt.admin.token.
    Retorna o token como string.
    """
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Navegador invisível
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-blink-features=AutomationControlled')  # Diminui chance de bloqueio

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        print("🚀 Acessando página de login...")
        driver.get("https://horus.hiplatform.com/")
        wait = WebDriverWait(driver, 40)

        # 1. Clica no botão "Continuar"
        continuar_btn = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//input[@value='Continuar']"))
        )
        continuar_btn.click()
        print("✅ Botão CONTINUAR clicado!")
        time.sleep(5)

        # 2. Preenche login
        email_input = wait.until(EC.presence_of_element_located((By.ID, "login_login")))
        email_input.clear()
        email_input.send_keys(email)

        senha_input = wait.until(EC.presence_of_element_located((By.ID, "login_password")))
        senha_input.clear()
        senha_input.send_keys(senha)

        time.sleep(3)

        # 3. Clica no botão "Entrar"
        entrar_btn = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//input[@value='Entrar' and not(@disabled)]"))
        )
        entrar_btn.click()
        print("✅ Botão ENTRAR clicado!")

        # 4. Esperar /products carregar
        wait.until(EC.url_contains("/products"))
        print("✅ Página de produtos carregada!")

        time.sleep(5)

        # 5. Forçar navegação para a página de relatórios
        relatorio_url = "https://www5.directtalk.com.br/static/beta/admin/main.html#!/relatorios/hsmReports?depto=-1"
        driver.get(relatorio_url)
        print("🚀 Acessando página de relatórios...")

        # 6. Monitorar carregamento real da página até 2 minutos
        relatorio_carregado = False
        tempo_inicio = time.time()

        while time.time() - tempo_inicio < 120:  # 2 minutos (120 segundos)
            time.sleep(5)  # Tenta a cada 5 segundos
            current_url = driver.current_url
            if "hsmReports" in current_url:
                print(f"🔄 Verificando se relatório carregou... ({round(time.time() - tempo_inicio)}s)")
                # Tenta achar algum elemento que só existe no relatório
                try:
                    driver.execute_script("return document.readyState") == "complete"
                    relatorio_carregado = True
                    break
                except:
                    pass

        if not relatorio_carregado:
            print("⚠️ Atenção: Página de relatórios não carregou em 2 minutos.")
            return None

        # 7. Captura o token
        time.sleep(5)  # Um tempo extra para garantir injeção do localStorage
        token = driver.execute_script("return window.localStorage.getItem('dt.admin.token');")

        if token:
            print("✅ TOKEN CAPTURADO COM SUCESSO!")
            print("DT-Fenix-Token " + token)
            return token
        else:
            print("❌ Token não encontrado depois de carregar o relatório.")
            return None

    finally:
        driver.quit()

# =========================================
# EXEMPLO DE USO:

if __name__ == "__main__":
    email = "wisner.silva@queimadiaria.com.br"
    senha = "Wisner432"

    token = coletar_token(email, senha)

    if token:
        # (opcional) Salvar token no arquivo
        with open("token.txt", "w") as f:
            f.write(token)
        print("📄 Token salvo em 'token.txt'!")
    else:
        print("❌ Não foi possível capturar o token.")
