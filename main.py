from gestao_recepcao import menu as menu_recepcao
from gestao_consultas import menu as menu_consultas

def menu_principal():
    while True:
        print("\n=== CLÍNICA VETERINÁRIA ===")
        print("1. Receção")
        print("2. Consultas")
        print("0. Sair")

        op = input("Escolha: ")

        if op == "1":
            menu_recepcao()
        elif op == "2":
            menu_consultas()
        elif op == "0":
            print("A sair do sistema...")
            break
        else:
            print("Opção inválida.")

if __name__ == "__main__":
    menu_principal()