from backend import *

"""
Devemos ter um sistema de construção de elementos na linguagem kv
Uma forma de verificar possíveis erros
Uma forma de sugerir possíveis complementos
Uma forma de salvar tudo após o fechamento.
"""


# Vamos construir nossa IDLE aqui.

def construtor(arquivokv):
    janela = criando_janela("Construindo", comp, alt)

    fonte_titulo = ("Times New Roman", 16, 'bold')
    titulo = Label(janela, text=arquivokv, bg='#dde', font=fonte_titulo)
    titulo.place(x=comp / 2 - 4 * len(arquivokv), y=10)

    # Primeiro, devemos ler as informações que já estão presentes no arquivo
    linhas_passadas = obtendo_texto_anterior(arquivokv)

    # Vamos disponibilizar o local para escrever
    fonte_texto = ("Verdana", 10)
    posx, posy, altura_texto = 20, 50, 300
    espaco_para_construir = Text(janela, font=fonte_texto)
    espaco_para_construir.place(x=posx, y=posy, width=comp - 2 * posx, height=altura_texto)

    if escuro:
        janela.configure(bg='#696969')
        titulo.configure(bg='#696969')
        espaco_para_construir.configure(bg='#1C1C1C', fg='white')

    # Alterando_Cores_para facilitar
    construindo_tags(espaco_para_construir, tags)

    # Preenchendo
    preenchendo(espaco_para_construir, linhas_passadas)

    # Vamos colocar as cores no texto inicial
    hierarquizando(espaco_para_construir, True)

    # Agora, construir o sistema de bind
    espaco_para_construir.bind("<Key>", lambda event: suplementando(event, espaco_para_construir, janela))
    espaco_para_construir.bind("<Tab>", lambda event: consertando_tab(event, espaco_para_construir))

    # Salvando
    def fechou():
        novas_linhas = espaco_para_construir.get('1.0', 'end').split("\n")

        try:
            # Isso aqui é muito foda compadre.
            while novas_linhas[-1] == '':
                novas_linhas.pop()

            novas_linhas = '\n'.join(novas_linhas)

            with open(arquivokv, 'w', encoding="utf-8") as base:
                base.write(novas_linhas)
        except:
            pass

        janela.destroy()

    # Caso destruirmos a janela, devemos salvar todx o conteúdo escrito
    janela.protocol("WM_DELETE_WINDOW", fechou)

    def botao_configuracao():
        btn = Button(janela, text='Configurações',
                     command=lambda arq=arquivokv: alterando(arq, janela, titulo, espaco_para_construir))
        btn.place(x=comp - btn.winfo_reqwidth() - 20, y=360)

    botao_configuracao()

    def ajuda():
        # Vamos dispor informações sobre classes e seus parâmetros

        # Vamos mudar a cor para indicar se vamos destruir ou criar a ajuda.
        # Não precisamos de uma variável de booleana, pois o if do tamanho de janela já serve.

        btn = Button(janela, bg='#94f7f4', text='Ajuda')
        btn["command"] = lambda: apresentando_ajuda(janela, btn, espaco_para_construir)
        btn.place(x=20, y=360)

        mensagem = "Clicando duas vezes, você escreve a sugestão dentro do espaço." + \
            "\n\nSelecionando uma classe e clicando em Enter, uma página da Web com essa classe lhe será apresentada."

        informador(janela, mensagem, 2, 365)

    ajuda()

    janela.mainloop()


if __name__ == '__main__':
    construtor('exemplo2.kv')
