from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from datetime import date
from app import app, db
from app.models import Produto, Marca, Origem, Configuracoes, User
import time

def get_or_create_marca(nome):
    marca = Marca.query.filter_by(nome_marca=nome).first()
    if not marca:
        marca = Marca(nome_marca=nome, nota_marca_avg=0.0, marcacol="")
        db.session.add(marca)
        db.session.commit()
    return marca

def get_or_create_origem(url):
    origem = Origem.query.filter_by(nome_site="Mercado Livre").first()
    if not origem:
        origem = Origem(nome_site="Mercado Livre", url_site=url)
        db.session.add(origem)
        db.session.commit()
    return origem

def obter_url_scraping(user_id):
    config = Configuracoes.query.filter_by(user_id=user_id, chave_configuracao='site_scraping').first()
    return config.valor_configuracao if config else None

def extrair_caracteristicas(driver):
    specs = {}
    try:
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "table.andes-table"))
        )
        linhas = driver.find_elements(By.CSS_SELECTOR, "table.andes-table tbody tr")
        for linha in linhas:
            try:
                chave = linha.find_element(By.TAG_NAME, "th").text.strip()
                valor = linha.find_element(By.TAG_NAME, "td").text.strip()
                specs[chave] = valor
            except:
                continue
    except Exception as e:
        print(f"[ERRO] Falha ao extrair tabela: {e}")
    return specs

def scrape(user_id):
    url = obter_url_scraping(user_id)

    if not url:
        print(f"[ERRO] Usuário {user_id} não tem site_scraping configurado.")
        return

    print(f"[INFO] Scraping iniciado com URL: {url}")

    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        driver.get(url)
        time.sleep(3)

        cards = driver.find_elements(By.CSS_SELECTOR, "li.ui-search-layout__item")

        print(f"[DEBUG] Total de produtos encontrados: {len(cards)}")
        if not cards:
            print("[AVISO] Nenhum produto foi encontrado. Verifique o seletor ou a página.")
            return

        origem = get_or_create_origem(url)

        for card in cards[:5]:
            try:
                nome = card.find_element(By.CSS_SELECTOR, "a.poly-component__title").text.strip()
                link = card.find_element(By.CSS_SELECTOR, "a.poly-component__title").get_attribute("href")
                preco_str = card.find_element(By.CSS_SELECTOR, "span.andes-money-amount__fraction").text.strip()
                preco = float(preco_str.replace('.', '').replace(',', '.'))

                # Nota média da avaliação
                try:
                    nota_str = card.find_element(By.CSS_SELECTOR, "span.poly-reviews__rating").text.strip()
                    nota = float(nota_str.replace(',', '.'))
                except:
                    nota = 0.0

                # Número total de avaliações
                try:
                    avaliacoes_str = card.find_element(By.CSS_SELECTOR, "span.poly-reviews__total").text.strip()
                    quantidade_avaliacoes = int(avaliacoes_str.strip("()").replace(".", ""))
                except:
                    quantidade_avaliacoes = 0

                # Acessa a página do produto para mais dados
                driver.execute_script("window.open(arguments[0]);", link)
                driver.switch_to.window(driver.window_handles[1])
                time.sleep(2)

                # Clica para expandir as características, se o botão existir
                try:
                    btn_mais = WebDriverWait(driver, 3).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-testid="action-collapsible-target"]'))
                    )
                    btn_mais.click()
                    time.sleep(1)
                except:
                    print("[INFO] Botão de características extras não encontrado ou já expandido.")

                caracteristicas = extrair_caracteristicas(driver)
                descricao = " | ".join([f"{k}: {v}" for k, v in caracteristicas.items()])
                marca_nome = caracteristicas.get("Marca", caracteristicas.get("marca", "Desconhecida"))

                if marca_nome.lower() == "distribuidor autorizado":
                    print(f"[AVISO] Marca incorreta detectada para {nome}. Corrigindo para 'Desconhecida'.")
                    marca_nome = "Desconhecida"

                driver.close()
                driver.switch_to.window(driver.window_handles[0])

                marca = get_or_create_marca(marca_nome)

                produto = Produto(
                    nome_produto=nome,
                    valor_produto=preco,
                    id_marca=marca.id,
                    id_origem=origem.id,
                    nota_produto_avg=nota,
                    data_produto=date.today(),
                    produtocol=f"{quantidade_avaliacoes} avaliações | {descricao}"
                )
                db.session.add(produto)

                print(f"[OK] Produto salvo: {nome} - R$ {preco} | Nota: {nota} ({quantidade_avaliacoes} avaliações)")

            except Exception as e:
                print(f"[ERRO] Falha ao processar item: {e}")

        db.session.commit()
        print("✅ Scraping finalizado e dados salvos no banco.")

    finally:
        driver.quit()

# if __name__ == "__main__":
#     with app.app_context():
#         user = User.query.filter_by(email="henrique@teste.com").first()
#         if user:
#             scrape(user.id)
#         else:
#             print("Nenhum usuário encontrado no banco.")