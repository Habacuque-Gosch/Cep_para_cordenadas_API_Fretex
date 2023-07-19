from flask import Flask, render_template, request, flash
import requests
from geopy.distance import geodesic
from geopy.geocoders import Nominatim
import pycep_correios
import folium
from folium.plugins import LocateControl



#COLETA DE CORDENADAS DE COLETA PARA O MAPA
class Colet:
    def __init__(self, coleta):
        self.coleta = coleta

#COLETA DE CORDENADAS DE ENTREGA PARA O MAPA
class Entreg:
    def __init__(self, entrega):
        self.entrega = entrega

class InfoColeta_entrega:
     def __init__(self, cep_entrega, rua_entrega, bairro_entrega, cidade_entrega, estado_entrega, casa_entrega, cep_coleta, rua_coleta, bairro_coleta, cidade_coleta, estado_coleta, casa_coleta, veiculo, distancia, total):
        self.cep_entrega = cep_entrega
        self.rua_entrega = rua_entrega
        self.bairro_entrega = bairro_entrega
        self.cidade_entrega = cidade_entrega
        self.estado_entrega = estado_entrega
        self.casa_entrega = casa_entrega
        self.cep_coleta = cep_coleta
        self.rua_coleta = rua_coleta
        self.bairro_coleta = bairro_coleta
        self.cidade_coleta = cidade_coleta
        self.estado_coleta = estado_coleta
        self.casa_coleta = casa_coleta
        self.veiculo = veiculo
        self.distancia = distancia
        self.total = total


app = Flask(__name__)

app.secret_key = "API Fretex"

@app.route('/', methods=['POST', 'GET'])
def cotacao():
    return render_template('cotacao.html')

@app.route('/calcula', methods=['POST', 'GET'])
def calcula():
    info_cep_coleta = InfoColeta_entrega
    info_cep_coleta.cep_coleta = request.form['cep']

    if len(InfoColeta_entrega.cep_coleta) != 8:
        flash("Cep Inválido")
        return render_template('cotacao.html')
    else:
        dados_de_busca = requests.get('https://viacep.com.br/ws/{}/json/'.format(InfoColeta_entrega.cep_coleta))
        address_data = dados_de_busca.json()

    if 'erro' not in address_data:
        #ENDEREÇO DE COLETA
        info_rua_coleta = InfoColeta_entrega
        info_rua_coleta.rua_entrega = (address_data['logradouro'])
        info_bairro_coleta = InfoColeta_entrega
        info_bairro_coleta.bairro_entrega = (address_data['bairro'])
        info_cidade_coleta = InfoColeta_entrega
        info_cidade_coleta.cidade_entrega = (address_data['localidade'])
        info_estado_coleta = InfoColeta_entrega
        info_estado_coleta.estado_entrega = (address_data['uf'])
        info_casa_coleta = InfoColeta_entrega
        info_casa_coleta.casa_entrega = request.form['numero']
    else:
        flash("Endereço de entrega não encontrado")
        return render_template('cotacao.html')

    if len(InfoColeta_entrega.casa_entrega) < 1:
        flash("Preencha o número da casa de coleta")
        return render_template('cotacao.html')

    #PEGANDO O CEP DE ENTREGA INSERIDO
    info_cep_entrega = InfoColeta_entrega
    info_cep_entrega.cep_entrega = request.form['cep1']
    if len(InfoColeta_entrega.cep_entrega) != 8:
        return render_template('cotacao.html')
    else:
        dados_de_entrega = requests.get('https://viacep.com.br/ws/{}/json/'.format(InfoColeta_entrega.cep_entrega))
        address_data = dados_de_entrega.json()

    if 'erro' not in address_data:
        #ENDEREÇO  DE ENTREGA
        info_rua_entrega = InfoColeta_entrega
        info_rua_entrega.rua_coleta = (address_data['logradouro'])
        info_bairro_entrega = InfoColeta_entrega
        info_bairro_entrega.bairro_coleta = (address_data['bairro'])
        info_cidade_entrega = InfoColeta_entrega
        info_cidade_entrega.cidade_coleta =  (address_data['localidade'])
        info_estado_entrega = InfoColeta_entrega
        info_estado_entrega.estado_coleta = (address_data['uf'])
        info_casa_entrega = InfoColeta_entrega
        info_casa_entrega.casa_coleta = request.form['numero1']
    else:
        flash("Endereço de coleta não encontrado")
        return render_template('cotacao.html')
    
    if len(InfoColeta_entrega.casa_coleta) < 1:
        flash("Preencha o número da casa de entrega")
        return render_template('cotacao.html')

    #COMPARAÇÃO DE ENDEREÇO
    if InfoColeta_entrega.cep_coleta == InfoColeta_entrega.cep_entrega:
        flash("o endereço de coleta não pode ser o mesmo de entrega")
        return render_template('cotacao.html')
    
    if InfoColeta_entrega.cep_entrega == "":
        flash('Digite o cep de coleta')
        return render_template('cotacao.html')

    if InfoColeta_entrega.cep_coleta == "":
        flash('Digite o cep de entrega')
        return render_template('cotacao.html')

    #CONVERTENDO CEP EM CORDENADAS
    CEP_STRING_COLETA = str(InfoColeta_entrega.cep_coleta)
    CEP_STRING_ENTREGA = str(InfoColeta_entrega.cep_entrega)

    endereco_coleta = pycep_correios.get_address_from_cep(CEP_STRING_COLETA)
    endereco_entrega = pycep_correios.get_address_from_cep(CEP_STRING_ENTREGA)

    geolocator = Nominatim(user_agent="test_app")
    location = geolocator.geocode(endereco_coleta['logradouro'] + ", " + endereco_coleta['bairro'])
    location2 = geolocator.geocode(endereco_entrega['logradouro'] + ", " + endereco_entrega['bairro'])

    
    #LATIDUDE E LOGITUDE COLETA
    lat_coleta, long_coleta = location.latitude, location.longitude
    #COORDENADAS DA COLETA
    coord_coleta = lat_coleta, long_coleta

    #LATIDUDE E LOGITUDE ENTREGA
    lat_entrega, long_entrega = location2.latitude, location2.longitude
    #CORDENADAS DA ENTREGA
    coord_entrega = lat_entrega, long_entrega

    colet = Colet
    colet.coleta = coord_entrega
    entreg = Entreg
    entreg.entrega = coord_coleta

    #DISTÂNCIA
    distancia_real = geodesic(coord_coleta, coord_entrega).km
    distancia = distancia_real

    if distancia_real <= 1:
        distancia = distancia * 0.15 + distancia
        distancia = round(distancia,3)

    if distancia_real >= 1:
        distancia = distancia
        distancia = round(distancia,2)

    if distancia_real >= 3:
        distancia = distancia * .3 + distancia
        distancia = round(distancia,2)

    if distancia_real >= 5:
        distancia = distancia * 0.25 + distancia 
        distancia = round(distancia,2)

    if distancia_real >= 10:
        distancia = distancia - 0.25 * distancia
        distancia = round(distancia,2)

    if distancia_real >= 100:
        distancia = distancia * .2 + distancia
        distancia = round(distancia,2)

    if distancia_real >= 200:
        distancia = distancia * .2 + distancia
        distancia = round(distancia,2)

    #ITENS A ENTREGAR
    itens = request.form['itens']

    #TABELA PREÇO POR VEÍCULO
    moto = round(1.30 * distancia, 2)
    carro =  round(2.20 * distancia, 2)
    caminhao = round(6 * distancia, 2)

    #TIPO DE VEICULO SELECIONADO
    tipo_veiculo = request.form['veiculo']

    if tipo_veiculo == "":
        flash("Selecione um veículo")
        return render_template('cotacao.html')
    #DECISÃO DO TIPO DE VEICULO
    if tipo_veiculo == "moto":
        valor_corrida = moto 
    
    if tipo_veiculo == "carro":
        valor_corrida = carro

    if tipo_veiculo == "caminhao":
        valor_corrida = caminhao

    #TIPO DE FRETE
    tipo_frete = request.form['servicos']
    if tipo_frete == "":
        flash("Selecione o tipo de carga")
        return render_template('cotacao.html')

    #DECISAO DO TIPO DE SERVIÇO
    if tipo_frete == "transporte":
        valor_corrida = round(valor_corrida  + 6, 2) 

    if tipo_frete == "mudanca1":
        valor_corrida = round(valor_corrida  + 150, 2) 

    if tipo_frete == "mudanca2":
        valor_corrida = round(valor_corrida  + 200, 2)

    if tipo_frete == "mudanca3":
        valor_corrida = round(valor_corrida  + 300, 2)

    #PORCENTAGEM CLIENTE
    if valor_corrida <= 299:
        valor_corrida = round(valor_corrida + 0.04 * valor_corrida, 2)
    if valor_corrida >= 300:
        valor_corrida = round(valor_corrida + 0.06 * valor_corrida, 2)

    #Dados Gerais
    veiculo = InfoColeta_entrega
    veiculo.veiculo = tipo_veiculo

    distancia_total = InfoColeta_entrega
    distancia_total.distancia = distancia

    valor_total = InfoColeta_entrega
    valor_total.total = valor_corrida

    return render_template('solicitacao.html', distancia_total = distancia, veiculo= tipo_veiculo, valor_total= InfoColeta_entrega.total, itens_entrega= itens, rua= InfoColeta_entrega.rua_entrega, bairro= InfoColeta_entrega.bairro_entrega, casa_coleta= InfoColeta_entrega.casa_entrega , cidade= InfoColeta_entrega.cidade_entrega, estado= InfoColeta_entrega.estado_entrega, rua_entrega= InfoColeta_entrega.rua_coleta, bairro_entrega= InfoColeta_entrega.bairro_coleta, cidade_entrega= InfoColeta_entrega.cidade_coleta, estado_entrega= InfoColeta_entrega.estado_coleta, casa_entrega= InfoColeta_entrega.casa_coleta)


@app.route('/map')
def map():
    ponto_de_partida= Colet.coleta
    map = folium.Map(
        location=ponto_de_partida,
        zoom_start= 12,
        control_scale = True
        
    )
    
    ponto_de_entrega = Entreg.entrega
    folium.Marker(
        location=ponto_de_partida,
        popup="<i>Aguarde o motorista no local</i>",
        icon= folium.Icon(icon="glyphicon glyphicon-user", prefix="glyphicon", icon_color="white", color="green"),
        tooltip="Coleta"
    ).add_to(map)

    folium.Marker(
        location=ponto_de_entrega,
        popup= f'Total: {InfoColeta_entrega.total} R$',
        tooltip="Entrega",
        icon= folium.Icon(color="red" ,icon_color="red" ,prefix="fa", icon='circle')
        
    ).add_to(map)
    cordenadas = [Colet.coleta,
                 Entreg.entrega]
    
    for i in range(len(cordenadas)-1):
        ponto_inicial = cordenadas[i]
        ponto_final = cordenadas[i+1]
        folium.PolyLine(locations = [ponto_inicial, ponto_final]).add_to(map)
    #LOCALIZAÇÃO EM TEMPO REAL
    LocateControl(auto_start= True,KeepCurrentZoomLevel = True).add_to(map)

    return map._repr_html_()


@app.route('/enviar', methods=['GET', 'POST'])
def enviar():
    endereco_info_coleta = InfoColeta_entrega.cep_coleta, InfoColeta_entrega.rua_coleta, InfoColeta_entrega.casa_coleta, InfoColeta_entrega.bairro_coleta, InfoColeta_entrega.cidade_coleta, InfoColeta_entrega.estado_coleta 

    #COLETA
    endereco_info_entrega = InfoColeta_entrega.cep_entrega, InfoColeta_entrega.rua_entrega, InfoColeta_entrega.casa_entrega, InfoColeta_entrega.bairro_entrega, InfoColeta_entrega.cidade_entrega, InfoColeta_entrega.estado_entrega

    #DADOS GERAIS
    Dados_Gerais = InfoColeta_entrega.veiculo, str(InfoColeta_entrega.distancia) + " KM", str(InfoColeta_entrega.total) + " R$"

    coleta = str(endereco_info_coleta)
    entrega = str(endereco_info_entrega)
    Dados = str(Dados_Gerais)
    
    import mysql.connector
    
    host='127.0.0.1:3306'
    database='u908688183_ordem'
    user='u908688183_fretex'
    password='Fretex2023'

    # # host='containers-us-west-131.railway.app'
    # # database='railway'
    # # user='root'
    # # password='lrrVCjNyG0aeSwl35DUQ'

    # host='127.0.0.1'
    # database='Servicos'
    # user='root'
    # password='Fretex2023'

    conexao = mysql.connector.connect(
        host=host,
        database=database, 
        user=user,
        password=password,
    )

    cursor = conexao.cursor()
    
    comando = f'INSERT INTO ordem (Endereco_Coleta, Endereco_Entrega, Dados_Gerais) VALUES ("{coleta}", "{entrega}", "{Dados}")'
    cursor.execute(comando)
    conexao.commit()
    cursor.close()
    conexao.close()
    
    return render_template('confirmado.html')

if __name__ == "__main__":
    app.run(debug=True)