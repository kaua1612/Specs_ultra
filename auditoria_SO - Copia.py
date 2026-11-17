import os
import platform
import subprocess
import socket
import shutil
import time
from datetime import datetime


# FUNCAO PARA EXECUTAR COMANDOS DO CMD
def cmd(comando):
    try:
        resultado = subprocess.run(
            ["cmd", "/c", comando],
            capture_output=True,
            text=True,
            encoding="cp850",
            errors="replace",
            timeout=30
        )
        return resultado.stdout.strip()
    except Exception:
        return ""


print("=" * 60)
print("          RELATORIO DE AUDITORIA DO PC")
print("=" * 60)

# EXECUTA O SYSTEMINFO APENAS UMA VEZ PARA ECONOMIZAR TEMPO
info_sistema = cmd("systeminfo")


# SISTEMA OPERACIONAL
print("\n[ SISTEMA OPERACIONAL ]")
print(f"Sistema                    : {platform.system()}")
print(f"Versao                     : {platform.release()}")
print(f"Arquitetura                : {platform.machine()}")
print(f"Nome do computador         : {platform.node()}")
print(f"Usuario                    : {os.environ.get('USERNAME')}")
print(f"Diretorio                  : {os.getcwd()}")


# PROCESSADOR
print("\n[ PROCESSADOR ]")
print(f"Identificacao              : {platform.processor()}")
print(f"Processadores logicos      : {os.cpu_count()}")

for linha in info_sistema.splitlines():
    if "Processador(es)" in linha or "Processor(s)" in linha:
        print(linha.strip())


# MEMORIA RAM (CORRIGIDO O ACENTO E REMOVIDA A REPETICAO DO SYSTEMINFO)
print("\n[ MEMORIA RAM ]")
encontrou_ram = False

for linha in info_sistema.splitlines():
    # Checa com e sem acento para funcionar em PT-BR e EN-US
    if any(termo in linha for termo in ["Memória física", "Memoria fisica", "Physical Memory"]):
        print(linha.strip())
        encontrou_ram = True

if not encontrou_ram:
    print("Informacao nao encontrada no systeminfo.")


# PLACA DE VIDEO (CORRIGIDO ENCODING DO DXDIAG)
print("\n[ PLACA DE VIDEO ]")

arquivo_dx = os.path.join(os.environ.get("TEMP", "."), "auditoria_dxdiag.txt")

try:
    if os.path.exists(arquivo_dx):
        os.remove(arquivo_dx)

    # Usa subprocess.run para aguardar o dxdiag terminar naturalmente
    subprocess.run(
        ["dxdiag", "/t", arquivo_dx],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        timeout=30
    )

    conteudo = ""
    if os.path.exists(arquivo_dx):
        # Tenta ler com a codificacao padrao do Windows (cp1252)
        with open(arquivo_dx, "r", encoding="cp1252", errors="replace") as arquivo:
            conteudo = arquivo.read()

    encontrou_gpu = False
    for linha in conteudo.splitlines():
        if any(palavra in linha.lower() for palavra in [
            "card name:",
            "nome da placa:",
            "display memory:",
            "memória de vídeo:",
            "memoria de video:",
            "dedicated memory:",
            "memória dedicada:",
            "shared memory:",
            "memória compartilhada:"
        ]):
            print(linha.strip())
            encontrou_gpu = True

    if not encontrou_gpu:
        print("GPU nao identificada.")

except Exception as e:
    print(f"Erro ao consultar placa de video: {e}")


# ARMAZENAMENTO (USANDO SHUTIL NATIVO - NAO PRECISA DE ADMIN)
print("\n[ ARMAZENAMENTO ]")
try:
    total, usado, livre = shutil.disk_usage("C:\\")
    gb = 1024 ** 3
    print(f"Unidade C:                 : Total: {total / gb:.2f} GB | Usado: {usado / gb:.2f} GB | Livre: {livre / gb:.2f} GB")
except Exception as e:
    print(f"Erro ao ler disco C: {e}")


# UNIDADES DISPONIVEIS
print("\n[ UNIDADES DISPONIVEIS ]")
print(cmd("fsutil fsinfo drives"))


# REDE
print("\n[ REDE ]")
print(f"Computador                 : {socket.gethostname()}")

resultado_rede = cmd("ipconfig")
for linha in resultado_rede.splitlines():
    if "IPv4" in linha or "IPv4 Address" in linha:
        print(linha.strip())


# BIOS
print("\n[ BIOS ]")
for linha in info_sistema.splitlines():
    if "BIOS" in linha:
        print(linha.strip())


# DATA E HORA
print("\n[ DATA E HORA ]")
print(f"Data                       : {datetime.now().strftime('%d/%m/%Y')}")
print(f"Horario                    : {datetime.now().strftime('%H:%M:%S')}")


print("\n" + "=" * 60)
print("             AUDITORIA FINALIZADA")
print("=" * 60)

input("clique ENTER para fechar o programa! ")
