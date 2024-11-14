from backend import *


def manipulando_arquivos():
    janela = criando_janela("IDE KV",
                            comprimento,
                            altura)

    # Apresentando o ambiente.
    ambiente = StringVar(janela)
    longo_caminho = StringVar(janela)

    def apresentando_ambiente():
        longo_caminho.set(os.getcwd())
        ambiente.set(os.path.basename(longo_caminho.get()))
        # Vamos mostrar todas as pastas e os arquivos .kv que estão no ambiente
        Label(janela, text=f"Mostrando Ambiente Dentro de: ",
              bg="#dde").place(x=10, y=10)

        Label(janela, textvariable=ambiente, fg="red", bg="#dde").place(x=185, y=10)

        # Devemos disponibilizar formas de alteração do ambiente.
        botao1 = Button(janela, text='Ambientação')
        botao1["command"] = lambda: alterando_ambiente(ambiente, longo_caminho, janela)
        botao1.place(x=260, y=30, height=20)

    apresentando_ambiente()

    mostrando_arquivos(ambiente, longo_caminho, janela)

    # Vamos disponibilizar os botões Sanhudos
    def criar_arquivokv():
        # Vamos sanhar
        ja_clicou = BooleanVar(janela)
        ja_clicou.set(False)

        def manipular():
            if not ja_clicou.get():
                # Quer dizer que não foi clicado ainda
                ja_clicou.set(True)
                # Vamos fazer aparecer um Entry
                frase_entrada = "Nome do Arquivo"

                def desetar(event):
                    if nome_arquivo.get() == frase_entrada:
                        nome_arquivo.delete(0, 'end')
                        nome_arquivo.configure(fg='black')
                        ajuda.set("Press Enter")

                def setar(event):
                    if nome_arquivo.get() == "":
                        # Vamos destruir mesmo
                        nome_arquivo.destroy()
                        labal.destroy()

                def arquivando(event):
                    if messagebox.askokcancel('Eita!',
                                              f"Deseja mesmo criar o arquivo kv {nome_arquivo.get()} na pasta {ambiente.get()}?"):
                        nome = nome_arquivo.get()
                        if not nome.endswith('.kv'):
                            nome = nome + '.kv'

                        p = open(nome, "x")
                        p.close()

                        # Vamos destruir as coisas agora
                        nome_arquivo.destroy()
                        labal.destroy()

                        # E reconstruir o tv
                        mostrando_arquivos(ambiente, longo_caminho, janela)

                ajuda = StringVar(janela)
                ajuda.set("")
                labal = Label(janela, textvariable=ajuda, bg='#dde')
                labal.place(x=150, y=320)
                nome_arquivo = Entry(janela)
                nome_arquivo.insert(0, frase_entrada)
                nome_arquivo.configure(fg='gray')
                nome_arquivo.place(x=20, y=320, width=100)

                nome_arquivo.bind("<FocusIn>", desetar)
                nome_arquivo.bind("<FocusOut>", setar)
                nome_arquivo.bind("<Return>", arquivando)
            else:
                # print("Já está disponível para colocar o nome")
                pass

        Button(janela, text='Criar KV', command=manipular).place(x=20, y=280, width=100)

    criar_arquivokv()

    def criar_pasta():
        ja_clicou = BooleanVar(janela)
        ja_clicou.set(False)

        def manipular():
            if not ja_clicou.get():
                ja_clicou.set(True)

                # Vamos fazer aparecer um Entry
                frase_entrada = "Nome da Pasta"

                def desetar(event):
                    if nome_pasta.get() == frase_entrada:
                        nome_pasta.delete(0, 'end')
                        nome_pasta.configure(fg='black')
                        ajuda.set("Press Enter")

                def setar(event):
                    if nome_pasta.get() == "":
                        nome_pasta.destroy()
                        labal.destroy()

                def pastando(event):
                    if messagebox.askokcancel('Eita!',
                                              f"Deseja mesmo criar a pasta {nome_pasta.get()} no ambiente {ambiente.get()}?"):
                        nome = nome_pasta.get()

                        os.mkdir(os.path.join(longo_caminho.get(), nome))

                        # Vamos destruir as coisas agora
                        nome_pasta.destroy()
                        labal.destroy()

                        # E reconstruir o tv
                        mostrando_arquivos(ambiente, longo_caminho, janela)

                ajuda = StringVar(janela)
                ajuda.set("")
                labal = Label(janela, textvariable=ajuda, bg='#dde')
                labal.place(x=150, y=320)
                nome_pasta = Entry(janela)
                nome_pasta.insert(0, frase_entrada)
                nome_pasta.configure(fg='gray')
                nome_pasta.place(x=230, y=320, width=100)

                nome_pasta.bind("<FocusIn>", desetar)
                nome_pasta.bind("<FocusOut>", setar)
                nome_pasta.bind("<Return>", pastando)
            else:
                # print("Já clicou")
                pass

        Button(janela, text='Criar Pasta', command=manipular).place(x=230, y=280, width=100)

    criar_pasta()

    janela.mainloop()


if __name__ == '__main__':
    manipulando_arquivos()
