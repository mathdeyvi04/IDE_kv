import tkinter
from tkinter import *
from tkinter import messagebox
from tkinter import ttk
import os
import shutil as st

# Tamanho manipulador de Arquivos
comprimento = 350
altura = 430


################################################

def criando_janela(titulo, comp, alt):
    app = Tk()
    app.title(titulo)
    app.geometry(f'{comp}x{alt}')
    return app


def obtendo_texto_anterior(arquivo_base):
    try:
        p = open(arquivo_base, "r", encoding="utf-8")
        linhas = list(p.readlines())
        p.close()

        return linhas
    except:
        return messagebox.showerror("ERROR", f'Não foi possível abrir {arquivo_base}')


def importando_config():
    try:
        linhas = list(obtendo_texto_anterior(r'padroes.txt'))
    except Exception as e:
        print(e)
        return messagebox.showerror("ERROR", 'Não foi possível abrir configurações')

    index = 0

    for linha in linhas:
        # Separando
        linha = list(linha.split('='))
        linha[2] = linha[2].replace('\n', '')

        linhas[index] = linha

        index += 1

    return linhas


def criando_globais(informacoes: list) -> list:
    sanhas = []

    try:
        ja_iniciei_tag = False
        for tipo, titulo, dado in informacoes:

            if 'Apa' in titulo:
                if 'True' == dado:
                    sanhas.append(True)
                elif 'False' == dado:
                    sanhas.append(False)
                else:
                    sanhas.append(True)
                    messagebox.showwarning('Cuidado',
                                           'Um erro na variável global de "Apagamento Instantâneo" foi verificado, e considerou-se como True')

            if 'Mod' in titulo:
                if 'True' == dado:
                    sanhas.append(True)
                elif 'False' == dado:
                    sanhas.append(False)
                else:
                    sanhas.append(False)
                    messagebox.showwarning('Cuidado',
                                           'Um erro na variável global de "Modo Escuro" foi verificado, e considerou-se como False')

            elif tipo == 'Cor':
                if not ja_iniciei_tag:
                    sanhas.append(
                        # Colocando o primeiro, o qual conhecemos meu mito
                        {"MD": dado}
                    )
                    ja_iniciei_tag = True
                else:
                    sanhas[-1][titulo[-1]] = dado

            else:
                # MUITO BIZARRO, presta atenção nisso cara
                if 'Apa' not in titulo:
                    sanhas.append(int(dado))
    except:
        messagebox.showerror("Socorro!", 'Falha ao criar variáveis globais')

    return sanhas


# Importando nossas variáveis globais
comp, alt, escuro, ident_tab, apag_inst, tags = criando_globais(importando_config())


def apagando_espacos_inuteis(tras, local):
    if apag_inst:
        def alterando_index(para_tras, posicao):
            if posicao.endswith('.0'):
                return posicao

            incremento = -1 if para_tras else 1

            posicao = posicao.split('.')

            return ".".join([posicao[0], str(int(posicao[1]) + incremento)])

        # tras = True, estamos apertando backspace e indo para tras
        # tras = False, estamos apertando delete e indo para frente
        index_cursor = local.index("insert")

        index = index_cursor
        # Consertando valores
        if tras:
            index = alterando_index(tras, index)
            # Agora, ele consegue ler o que acabou de ser apagado
        else:
            pass
            # O sistema lê o elemento da frente do cursor

        carac_apagado_pelo_usuario = local.get(index)

        if carac_apagado_pelo_usuario == " ":
            # Quer dizer que talvez iremos apagar vários espaços.

            while True:
                # Então devemos ver o próximo caractere
                index = alterando_index(tras, index)
                prox_carac = local.get(index)

                if prox_carac == " ":

                    local.delete(index)
                    # Note que cada vez que apagamos um elemento,
                    # Os elementos de trás não tem o indice modificado, mas o da frente sim.

                    if not tras:
                        index = alterando_index(True, index)
                else:
                    # Achamos algo que não é um espaço
                    break

                if prox_carac == '\n' or index.endswith('.0'):
                    break


def suplementando(event, local, mestre):
    coisa_digitada = event.keysym

    # Devemos verificar a quantidade de espaços e apagar cada um deles.
    if coisa_digitada == 'Delete':
        apagando_espacos_inuteis(False, local)
    elif coisa_digitada == 'BackSpace':
        apagando_espacos_inuteis(True, local)
    elif coisa_digitada in ['Return', 'space']:

        """Note que há uma primeira chamada, onde varremos tudo que foi escrito.
        Mas nestas chamadas, varremos apenas uma linha papai."""
        hierarquizando(local)

        # Note que não vamos querer receber uma sugestão dps de darmos
        # espaço ou pulo para a próxima linha.


def hierarquizando(local, primeira_vez=False):
    def buscando(string: str) -> list:
        if string == '':
            # Vai tentar pelo menos restringir o custo de ter uma linha vazia
            return []
        else:
            string = string.replace('"', "'")

        interv = []

        index = 0
        begin = 0
        achei_classe = False
        achei_string = False
        string = list(string)
        for carac in string:
            if carac == 'M':
                achei_classe = True
                begin = index

            if carac == "'":
                if achei_string:
                    # Se for verdadeiro, achamos o final de uma string
                    interv.append([
                        begin,
                        index + 1,
                        "'"
                    ])
                else:
                    # Se for falso, achamos o começo de uma string.
                    begin = index
                    achei_string = True

            if carac == ':':
                # Se tivermos uma classe, estamos terminando de vê-la
                if achei_classe:
                    achei_classe = False
                    interv.append([
                        begin,
                        index,
                        'MD'
                    ])

                if len(interv) == 0 or interv[-1][-1] not in ['MD', "'"]:
                    # Podemos continuar
                    # Se não temos uma classe, temos um parâmetro!
                    interv.append(
                        descobrindo_index_parametro(index, string)
                    )

            index += 1

        return interv

    def descobrindo_index_parametro(index_finalizador: int, conjunto: list) -> list[int, int, str]:
        # Devemos varrer a linha para trás até terminar o parâmetro.

        i = index_finalizador - 1
        while True:
            carac = conjunto[i]

            if not (carac.isalpha() or carac == '_'):
                # Chegamos ao final
                return [
                    i,
                    index_finalizador,
                    ":"
                ]

            i += -1

    def base_index(index1: int, index2: int) -> str:
        return f'{index1}.{index2}'

    def buscar_cursor() -> tuple[str, str]:
        cursor = local.index("insert")
        # Vamos retornar os indexs para a linha que acabamos de escrever
        return ".".join([cursor.split(".")[0], '0']), cursor

    inicio, fim = ('1.0', 'end') if primeira_vez else buscar_cursor()

    texto_completo = local.get(inicio, fim).split("\n")

    index_linha = int(inicio.split(".")[0])
    for linha in texto_completo:

        intervalos = buscando(linha)

        for index_inicial, index_final, chave in intervalos:
            local.tag_add(chave,
                          base_index(index_linha, index_inicial),
                          base_index(index_linha, index_final)
                          )

        index_linha += 1


def consertando_tab(event, local):
    local.insert("insert", " " * ident_tab)
    # Esse break impede que o tab normal seja executado
    return "break"


def construindo_tags(local, tags_existentes):
    # Aqui, vamos construir as tags e os nomes que queremos que sejam buscados.

    for chave in tags_existentes.keys():
        local.tag_config(chave, foreground=tags_existentes[chave])


def preenchendo(local, linhas_passadas):
    # Vamos alterar cores aqui meu parceiro
    for frase in linhas_passadas:
        # Note que aqui já vamos ter as Sanhas a serem verificados
        local.insert('end', frase)

    local.insert("end", '\n\n')


def executando_decisao(escolha, ambiente_, caminho, tipo, entidade, mestre):
    # Vamos colocar subcoisas aqui e dps sanhar
    entidade_total = os.path.join(caminho.get(), entidade)

    if escolha == "Excluir":
        # Apenas para termos uma forma de atualizar ou não o treeview
        fiz_alguma_coisa = True

        # Se for um arquivo, é simples
        if tipo == "Arq":
            os.remove(entidade_total)
        else:
            # Temos uma pasta
            # Daí, devemos ter a opção de apagar ela vazia ou não

            coisas_dentro = os.listdir(entidade_total)

            if len(coisas_dentro) == 0:
                os.rmdir(entidade_total)
            else:
                # Há coisas e devemos avisar o cara
                if messagebox.askokcancel("Eita!", "Há coisas nessa pasta, certifique-se que deseja apagá-las"):
                    st.rmtree(entidade_total)
                else:
                    fiz_alguma_coisa = False

        if fiz_alguma_coisa:
            # Como fiz alguma alteração, devemos mostrar tudo de novo no treeview
            # Como não mudamos o ambiente em que está ocorrendo, basta usarmos isso
            mostrando_arquivos(ambiente_, caminho, mestre)

    elif escolha == "Abrir":
        # Vamos abrir o arquivo .kv em outra janela
        # Aqui vamos apresentar nossa IDLE de fato.
        from construtor import construtor
        construtor(entidade)
    else:
        # Só resta a opção de ambientar
        # Vamos montar abrir tudo de novo
        # print(f'A entidade que tenho: {os.path.basename(entidade)}')
        # print(f'Vou verificar em  {caminho.get()}')
        ambiente_.set(os.path.basename(entidade))
        caminho.set(entidade_total)
        mostrando_arquivos(ambiente_, caminho, mestre)


def obtendo_decisao(ambiente_, caminho, tipo_entidade, entidade, mestre):
    jan = criando_janela('Escolha', 200, 150)

    Label(jan, text="Selecione a opção desejada: ", bg='#dde').place(x=10, y=10)

    variavel = IntVar(jan)
    variavel.set(-1)

    def apresentar_opcoes(opcoes):
        index = 0
        for opcao in opcoes:
            Radiobutton(jan, text=opcao, bg="#dde", variable=variavel, value=index).place(x=10, y=40 + index * 30)
            index += 1

    possiveis_escolhas = ["Excluir", "Abrir"]
    # Vamos decidir o sanha
    if tipo_entidade == 'Pasta':
        possiveis_escolhas.remove("Abrir")
        possiveis_escolhas.append("Ambientar")
        apresentar_opcoes(possiveis_escolhas)
    else:
        # Como é um arquivo, podemos apagá-lo ou abri-lo.
        # Sendo assim, devemos escolher.
        apresentar_opcoes(possiveis_escolhas)

    def retornar():

        resultado = variavel.get()

        if possiveis_escolhas[resultado] == "Excluir":
            if messagebox.askokcancel("Eita!", "Deseja mesmo excluir?"):
                pass
            else:
                return jan.destroy()

        if resultado == -1:
            # Nada foi decidido,
            messagebox.showwarning("Eita!", "Decida Algo!")
        else:
            jan.destroy()

            # Vamos firmar nossa decisão aqui
            executando_decisao(
                possiveis_escolhas[resultado],
                ambiente_,
                caminho,
                tipo_entidade,
                entidade,
                mestre
            )

    Button(jan, text='Decidir', command=retornar).place(x=80, y=110)

    jan.mainloop()


def mostrando_arquivos(ambiente_, longo_caminho_, mestre):
    # print(f'Vou apresentar arquivos que estão em {longo_caminho_.get()}')
    # A partir do ambiente, vamos construir o TreeView responsável
    # por mostrar todos os arquivos .kv da pasta
    colunas = ["Tipo", "Sanhas"]
    tamanhos = [5, 210]
    tv = ttk.Treeview(mestre, show='headings', columns=colunas)

    index = 0
    for col in colunas:
        tv.heading(col, anchor='center', text=col)
        tv.column(col, anchor="center", minwidth=tamanhos[index], width=tamanhos[index])
        index += 1

    tv.place(x=10, y=60, width=comprimento - 20, height=200)

    # print(f'Vou procurar em {longo_caminho_.get()}')
    entidades = []
    for entidade in os.listdir(longo_caminho_.get()):
        # Esse join que eu coloquei resolveu um problema muito foda
        eh_pasta = os.path.isdir(os.path.join(longo_caminho_.get(), entidade))
        eh_arquivokv = str(entidade).endswith('.kv')
        # print(f'Estou vendo {entidade} e notei que é pasta {eh_pasta} e que é arquivo {eh_arquivokv}')

        if eh_pasta or eh_arquivokv:
            if entidade != '__pycache__':
                entidades.append([
                    "Arq" if eh_arquivokv else "Pasta",
                    entidade
                ])

    # Vamos ordenar isso do jeito que quisermos, já que não importa,
    # Vamos colocar as pastas primeiro
    entidades.sort(key=lambda sublista: 1 if sublista[0] == 'Pasta' else 0, reverse=True)

    # Colocando
    for sublista1 in entidades:
        tv.insert("", 'end', values=sublista1)

    # Agora, vamos criar o sistema de dois cliques
    def clicado(event):
        item_selecionado = tv.selection()
        # noinspection PyTypeChecker
        infor = tv.item(item_selecionado)["values"]

        obtendo_decisao(ambiente_, longo_caminho_, infor[0], infor[1], mestre)

    tv.bind("<Double-1>", clicado)


def alterando_ambiente(ambiente_, longo_, mestre):
    # Vamos ter que obter a pasta que o usuário disser.
    # Para isso, precisamos criar uma forma de obter o caminho
    # da pasta que ele deseja verificar.
    # Bizarro, consegui fazer mesmo
    from tkinter import filedialog

    selecionado = filedialog.askdirectory()

    if selecionado:
        longo_.set(selecionado)
        ambiente_.set(os.path.basename(selecionado))
        mostrando_arquivos(ambiente_, longo_, mestre)

    else:
        messagebox.showerror("ERROR", "Selecione uma pasta!")


def informador(mestre, texto, posx, posy):
    def mensagem():
        return messagebox.showinfo('Sanha Resolvido',
                                   texto)

    Button(mestre, text='i', command=mensagem).place(x=posx, y=posy, height=20)


def alterando(arquivo, mestre, titulo, local):
    # Vamos construir uma nova janela, mostrando dados importantes do Sanhudo
    sanha_x, sanha_y = 660, 300
    jan = criando_janela('Configurador',
                         sanha_x,
                         sanha_y)

    # Importando Dados.
    dados = importando_config()

    tipos = ['Screen', 'Texto', 'Cor']

    # Vamos criar nossos labelsframe
    frames = []
    for tipo in tipos:
        # Assim, não vamos precisar varrer tantas vezes
        frames.append(
            LabelFrame(jan, text=tipo, bg='#dde', relief='solid', borderwidth=2)
        )

    def obtendo_frame_especifico(tipo_dado):
        i = 0
        for frame1 in frames:
            if frame1['text'] == tipo_dado:
                return i

            i += 1

    def modificador(mestre1, nome, informacao, posy):

        base = Entry(mestre1)
        base.insert(0, informacao)
        base.place(x=140, y=posy, width=50)

        return base

    # Vamos guardar as posições em relação à y dos últimos caras colocados em cada frame
    posicoes = [
        10,
        10,
        10
    ]
    variaveis = []
    for tipo, titulo, info in dados:
        # Frame da informação
        index_frame = obtendo_frame_especifico(tipo)
        frame_da_info = frames[index_frame]

        Label(frame_da_info, text=titulo, bg='#dde').place(x=5, y=posicoes[index_frame])

        # Devemos disponilizar os Sanhas que poderão mudar as variáveis
        variaveis.append(
            modificador(frame_da_info, titulo, info, posicoes[index_frame])
        )

        if 'Apaga.' in titulo:
            informador(frame_da_info,
                       "Apagador Instantâneo de Espaços faz com que todos os espaços seguintes sejam apagados. Só pode ser True ou False.",
                       120, posicoes[index_frame])

        posicoes[index_frame] += 30
    # Posicionando
    maior = 0
    pos = [10, 230, 450]
    i2 = 0
    for frame in frames:
        height_especifico = posicoes[i2] + 30
        frame.place(x=pos[i2], y=10, width=200, height=height_especifico)
        i2 += 1
        if height_especifico > maior:
            maior = height_especifico

    jan.geometry(f"{660}x{maior + 100}")

    def finalizar():
        # Toda vez que fizemos modificações nos dados do frame, vamos fazer
        # modificações nos dados também, por que é ele que vamos salvar

        # Fazendo as modificações
        index = 0
        for sublista in dados:
            if sublista[-1] != variaveis[index].get():
                # Então há modificação
                dados[index][-1] = variaveis[index].get()

            index += 1

        # Salvando
        primeiro = True
        with open(r'../../../Aprendendo/AprendendoKivyMD/BuildWithPython/padroes.txt', 'w', encoding='utf-8') as base:
            for lista_dados in dados:
                if primeiro:
                    base.write(f'{"=".join(lista_dados)}')
                    primeiro = False
                else:
                    base.write(f'\n{"=".join(lista_dados)}')

        # Devemos nos destruir e inicializar o construtor de novo
        jan.destroy()
        mestre.destroy()

        global comp, alt, escuro, ident_tab, apag_inst, tags
        # Com isso, fazemos as modificações necessárias
        comp, alt, escuro, ident_tab, apag_inst, tags = criando_globais(importando_config())

        from construtor import construtor
        construtor(arquivo)

        """
        Cara, não dá. Simplesmente não é possível fazer alterações seguidas no construtor
        e esperar que se atualize toda vez que ele reinicie. Acho que tem haver com o fato
        que o backend fica rodando apesar que o front tenha se apagado. Não consegui...
        """

    btn = Button(jan, text='Finalizar', command=finalizar, bg="#bbfacc")
    btn.place(x=10, y=jan.winfo_reqheight())

    jan.mainloop()


def apresentando_ajuda(tela: tkinter.Tk, btn: tkinter.Button, local: tkinter.Text):
    # Devemos aumentar o tamanho da tela esporaticamente.
    # Vamos deixar o movimento suave
    if tela.winfo_height() != alt:
        tela.geometry(f'{comp}x{alt}')
        tela.update()
        btn.configure(bg='#94f7f4')

        tela.winfo_children()[-1].destroy()
    else:
        btn.configure(bg="#fa9e9b")

        componentes = {"AnchorLayout": 'https://kivymd.readthedocs.io/en/1.1.1/components/anchorlayout/',
                       "Backdrop": 'https://kivymd.readthedocs.io/en/1.1.1/components/backdrop/',
                       "Banner": 'https://kivymd.readthedocs.io/en/1.1.1/components/banner/',
                       "BottomNavigation": 'https://kivymd.readthedocs.io/en/1.1.1/components/bottomnavigation/',
                       "BottomSheet": 'https://kivymd.readthedocs.io/en/1.1.1/components/bottomsheet/',
                       "BoxLayout": 'https://kivymd.readthedocs.io/en/1.1.1/components/boxlayout/',
                       "Button": 'https://kivymd.readthedocs.io/en/1.1.1/components/button/',
                       "Card": 'https://kivymd.readthedocs.io/en/1.1.1/components/card/',
                       "Carousel": 'https://kivymd.readthedocs.io/en/1.1.1/components/carousel/',
                       "Chip": 'https://kivymd.readthedocs.io/en/1.1.1/components/chip/',
                       "CircularLayout": 'https://kivymd.readthedocs.io/en/1.1.1/components/circularlayout/',
                       "ColorPicker": 'https://kivymd.readthedocs.io/en/1.1.1/components/colorpicker/',
                       "DataTables": 'https://kivymd.readthedocs.io/en/1.1.1/components/datatables/',
                       "DatePicker": 'https://kivymd.readthedocs.io/en/1.1.1/components/datepicker/',
                       "Dialog": 'https://kivymd.readthedocs.io/en/1.1.1/components/dialog/',
                       "DropdownItem": 'https://kivymd.readthedocs.io/en/1.1.1/components/dropdownitem/',
                       "ExpansionPanel": 'https://kivymd.readthedocs.io/en/1.1.1/components/expansionpanel/',
                       "FileManager": 'https://kivymd.readthedocs.io/en/1.1.1/components/filemanager/',
                       "FitImage": 'https://kivymd.readthedocs.io/en/1.1.1/components/fitimage/',
                       "FloatLayout": 'https://kivymd.readthedocs.io/en/1.1.1/components/floatlayout/',
                       "GridLayout": 'https://kivymd.readthedocs.io/en/1.1.1/components/gridlayout/',
                       "Hero": 'https://kivymd.readthedocs.io/en/1.1.1/components/hero/',
                       "ImageList": 'https://kivymd.readthedocs.io/en/1.1.1/components/imagelist/',
                       "Label": 'https://kivymd.readthedocs.io/en/1.1.1/components/label/',
                       "List": 'https://kivymd.readthedocs.io/en/1.1.1/components/list/',
                       "Menu": 'https://kivymd.readthedocs.io/en/1.1.1/components/menu/',
                       "NavigationDrawer": 'https://kivymd.readthedocs.io/en/1.1.1/components/navigationdrawer/',
                       "NavigationRail": 'https://kivymd.readthedocs.io/en/1.1.1/components/navigationrail/',
                       "ProgressBar": 'https://kivymd.readthedocs.io/en/1.1.1/components/progressbar/',
                       "RecycleGridLayout": 'https://kivymd.readthedocs.io/en/1.1.1/components/recyclegridlayout/',
                       "RecycleView": 'https://kivymd.readthedocs.io/en/1.1.1/components/recycleview/',
                       "RefreshLayout": 'https://kivymd.readthedocs.io/en/1.1.1/components/refreshlayout/',
                       "RelativeLayout": 'https://kivymd.readthedocs.io/en/1.1.1/components/relativelayout/',
                       "ResponsiveLayout": 'https://kivymd.readthedocs.io/en/1.1.1/components/responsivelayout/',
                       "Screen": 'https://kivymd.readthedocs.io/en/1.1.1/components/screen/',
                       "ScreenManager": 'https://kivymd.readthedocs.io/en/1.1.1/components/screenmanager/',
                       "ScrollView": 'https://kivymd.readthedocs.io/en/1.1.1/components/scrollview/',
                       "SegmentedControl": 'https://kivymd.readthedocs.io/en/1.1.1/components/segmentedcontrol/',
                       "Selection": 'https://kivymd.readthedocs.io/en/1.1.1/components/selection/',
                       "SelectionControls": 'https://kivymd.readthedocs.io/en/1.1.1/components/selectioncontrols/',
                       "Slider": 'https://kivymd.readthedocs.io/en/1.1.1/components/slider/',
                       "SliverAppbar": 'https://kivymd.readthedocs.io/en/1.1.1/components/sliverappbar/',
                       "Snackbar": 'https://kivymd.readthedocs.io/en/1.1.1/components/snackbar/',
                       "Spinner": 'https://kivymd.readthedocs.io/en/1.1.1/components/spinner/',
                       "StackLayout": 'https://kivymd.readthedocs.io/en/1.1.1/components/stacklayout/',
                       "Swiper": 'https://kivymd.readthedocs.io/en/1.1.1/components/swiper/',
                       "Tabs": 'https://kivymd.readthedocs.io/en/1.1.1/components/tabs/',
                       "TapTargetView": 'https://kivymd.readthedocs.io/en/1.1.1/components/taptargetview/',
                       "TextField": 'https://kivymd.readthedocs.io/en/1.1.1/components/textfield/',
                       "TimePicker": 'https://kivymd.readthedocs.io/en/1.1.1/components/timepicker/',
                       "Toolbar": 'https://kivymd.readthedocs.io/en/1.1.1/components/toolbar/',
                       "Tooltip": 'https://kivymd.readthedocs.io/en/1.1.1/components/tooltip/',
                       "Transition": 'https://kivymd.readthedocs.io/en/1.1.1/components/transition/',
                       "Widget": 'https://kivymd.readthedocs.io/en/1.1.1/components/widget/'
                       }

        for i in range(0, 100):
            tela.geometry(f'{comp}x{alt + i}')
            tela.update()

        # Vamos construir o frame para colocar as coisas, para podermos destruir
        # mais fácil as coisas

        cor = tela.cget("background")

        frame = Frame(tela, bg=cor)
        frame.place(x=70, y=350, width=310, height=130)

        def obtendo_classe():
            frase = "Insira a classe desejada."

            def desetando(event):
                if clas.get() == frase:
                    clas.delete(0, 'end')
                    clas.configure(fg='black')

            def setando(event):
                if clas.get() == '':
                    clas.insert(0, frase)
                    clas.configure(fg='gray')

            clas = Entry(frame)
            clas.insert(0, frase)
            clas.place(x=10, y=10)
            clas.configure(fg='gray')

            lista_classes = Listbox(frame)
            for classe_total in componentes.keys():
                lista_classes.insert("end", classe_total)

            def colocando_sugestoes(event, lista):

                if len(event.keysym) == 1:
                    # Digitamos uma letra.
                    # Daí vamos pegar o Sanha e listar para ele.
                    lista.delete(0, 'end')

                    lista.update()

                    oq_foi_digitado_ate_agora = clas.get().upper()

                    for opcao in componentes.keys():
                        if opcao.upper().startswith(oq_foi_digitado_ate_agora):
                            lista.insert("end", opcao)

            lista_classes.place(x=10, y=40, width=125, height=80)

            clas.bind("<FocusIn>", desetando)
            clas.bind("<FocusOut>", setando)
            clas.bind("<Key>", lambda event: colocando_sugestoes(event, lista_classes))

            def inserindo(event):
                sugestao_selecionada = lista_classes.curselection()

                # Economizando memória.
                sugestao_selecionada = lista_classes.get(0, 'end')[sugestao_selecionada[0]]

                sugestao_selecionada = f'MD{sugestao_selecionada}:'

                # Vamos agora escrever
                local.insert(local.index("insert"), sugestao_selecionada)

                # Colorindo
                hierarquizando(local)

                local.insert(local.index("insert"), '\n')

            lista_classes.bind("<Double-1>", inserindo)

            return lista_classes

        lista = obtendo_classe()

        def mostrando_parametros(event):
            classe_selecionada = lista.get(0, 'end')[lista.curselection()[0]]

            try:
                from webbrowser import open
                # Vamos bradar:
                open(componentes[classe_selecionada])
            except:
                return messagebox.showerror(
                    "ERROR",
                    "Sem Internet talvez."
                )

        lista.bind("<Return>", mostrando_parametros)
