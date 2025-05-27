import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

def coletar_token():
    """
    Função para logar na HiPlatform, acessar a página de relatórios e capturar o token dt.admin.token.
    Retorna o token como string.
    """
    # Carregar as variáveis de ambiente para usuário e senha
    email = os.getenv("EMAIL")
    senha = os.getenv("SENHA")
    
    if not email or not senha:
        print("❌ Usuário ou senha não fornecidos.")
        return None

    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-blink-features=AutomationControlled')  # Diminui chance de bloqueio
    
    # Modo Headless: Se necessário, descomente a linha abaixo
    # options.add_argument('--headless')  # Navegador invisível

    # Inicializa o driver
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

        # 6. Esperar até que a URL contenha "callback_horus" (indica que o processo de redirecionamento aconteceu)
        wait.until(EC.url_contains("callback_horus"))
        print("✅ Página de redirecionamento carregada!")

        # 7. Esperar a URL de redirecionamento se estabilizar
        wait.until(EC.url_contains("main.html"))  # Aguarda a URL final
        print("✅ Página final carregada!")

        # 8. Aguardar até que o localStorage tenha o token
        print("🔄 Verificando localStorage para token...")
        token = None
        for _ in range(30):  # Tentar 30 vezes, aguardando até 30 segundos
            token = driver.execute_script("return window.localStorage.getItem('dt.admin.token');")
            if token:
                break
            time.sleep(1)  # Aguarda 1 segundo entre as tentativas

        if token:
            print(f"✅ TOKEN CAPTURADO COM SUCESSO: {token}")
        else:
            print("❌ Token não encontrado após tentativas!")

        return token

    except Exception as e:
        print(f"⚠️ Erro durante o processo: {e}")
        return None

    finally:
        print("🌐 Navegador mantido aberto para análise")
        input("Pressione Enter para fechar o navegador...")  # Aguarda interação para fechar o navegador
        driver.quit()  # Fecha o navegador quando o usuário pressionar Enter


def salvar_token(token, arquivo="capturar-token/token.txt"):
    """
    Função para salvar o token em um arquivo de texto
    """
    if token:
        # Cria a pasta capturar-token se não existir
        if not os.path.exists("capturar-token"):
            os.makedirs("capturar-token")
        
        # Salva o token no arquivo capturar-token/token.txt
        with open(arquivo, "w") as f:
            f.write(token)
        print(f"📄 Token salvo em '{arquivo}'!")
        
        # Verifique o conteúdo gravado no arquivo para confirmar
        with open(arquivo, "r") as f:
            saved_token = f.read().strip()
            print(f"✅ Token gravado corretamente: {saved_token}")
    else:
        print("❌ Não foi possível salvar o token.")


# =========================================
# EXEMPLO DE USO:

if __name__ == "__main__":
    # Certifique-se de que as variáveis de ambiente EMAIL e SENHA estejam configuradas corretamente.
    token = coletar_token()

    # Salvar o token no arquivo de texto
    salvar_token(token)
