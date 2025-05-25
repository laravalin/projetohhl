from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from datetime import date
from app import app, db
from app.models import Produto, Marca, Origem,Configuracoes, User


def get_or_create_marca(nome):
    marca = Marca.query.filter_by(nome_marca=nome).first()
    if not marca:
        marca = Marca(nome_marca=nome, nota_marca_avg=0.0, marcacol="")
        db.session.add(marca)
        db.session.commit()
    return marca

def get_or_create_origem():
    origem = Origem.query.filter_by(nome_site="Mercado Livre").first()
    if not origem:
        origem = Origem(nome_site="Mercado Livre", url_site=URL)
        db.session.add(origem)
        db.session.commit()
    return origem


def obter_url_scraping(user_id):
    config = Configuracoes.query.filter_by(user_id=user_id, chave_configuracao='site_scraping').first()
    return config.valor_configuracao if config else None

def scrape():
    # Configura o Selenium com Chrome em modo headless (sem abrir janela)

    url = obter_url_scraping()
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(url)

    cards = driver.find_elements(By.CLASS_NAME, "ui-search-result")
    origem = get_or_create_origem()

    for card in cards[:10]:  # limita pra 10 produtos
        try:
            nome = card.find_element(By.CLASS_NAME, "ui-search-item__title").text
            preco = card.find_element(By.CLASS_NAME, "price-tag-fraction").text
            preco = float(preco.replace('.', '').replace(',', '.'))

            marca = get_or_create_marca("Apple")  # fixo por simplicidade

            produto = Produto(
                nome_produto=nome,
                valor_produto=preco,
                id_marca=marca.id,
                id_origem=origem.id,
                nota_produto_avg=0.0,
                data_produto=date.today(),
                produtocol=""
            )
            db.session.add(produto)
        except Exception as e:
            print(f"Erro ao processar produto: {e}")

    db.session.commit()
    driver.quit()
    print("Scraping finalizado.")

if __name__ == "__main__":
    with app.app_context():
        scrape()
