import os
import csv
import time
from datetime import datetime
import requests
from io import BytesIO
from PIL import Image
from requests.exceptions import RequestException

# -------------------------------
# CONFIGURAÇÕES
# -------------------------------
BASE_URL = "https://rpachallengeocr.azurewebsites.net"
SEED_URL = f"{BASE_URL}/seed"
OUTPUT_DIR = "downloads"
CSV_FILE = "data/faturas.csv"
LOGS_DIR = "logs"

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs("data", exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)

today = datetime.today().date()
MAX_RETRIES = 3

# Arquivo de log
log_file_path = os.path.join(LOGS_DIR, f"log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")

def log(msg):
    print(msg)
    with open(log_file_path, "a", encoding="utf-8") as lf:
        lf.write(msg + "\n")

# -------------------------------
# VARIÁVEIS DE CONTROLE
# -------------------------------
processed_ids = set()
faturas_baixadas = []
faturas_ignoradas = []
faturas_falha = []

# -------------------------------
# INICIALIZAÇÃO DO CSV
# -------------------------------
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["ID_Fatura", "Due_Date", "URL_Fatura"])

# -------------------------------
# REQUISIÇÃO POST
# -------------------------------
headers = {
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Origin": BASE_URL,
    "Referer": BASE_URL + "/",
    "User-Agent": "Mozilla/5.0",
    "X-Requested-With": "XMLHttpRequest"
}

try:
    response = requests.post(SEED_URL, data={}, headers=headers, timeout=10)
    response.raise_for_status()
    faturas_data = response.json().get("data", [])
except RequestException as e:
    log(f"❌ Erro ao acessar o seed: {e}")
    exit(1)

# -------------------------------
# PROCESSAMENTO DE CADA FATURA
# -------------------------------
for f in faturas_data:
    id_fatura = f.get("id")
    due_date_str = f.get("duedate")
    invoice_path = f.get("invoice")

    if not id_fatura or not due_date_str or not invoice_path:
        log(f"⚠️ Dados incompletos para fatura: {f}")
        continue

    if id_fatura in processed_ids:
        continue
    processed_ids.add(id_fatura)

    url_fatura = BASE_URL + invoice_path

    try:
        due_date = datetime.strptime(due_date_str, "%d-%m-%Y").date()
    except ValueError:
        log(f"⚠️ Data inválida para fatura {id_fatura}: {due_date_str}")
        continue

    log(f"🔹 Fatura: {id_fatura} | Due Date: {due_date} | Hoje: {today}")

    if due_date <= today:
        file_name = os.path.join(OUTPUT_DIR, f"{id_fatura}.pdf")
        success = False

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                r = requests.get(url_fatura, timeout=10)
                r.raise_for_status()

                if url_fatura.lower().endswith(('.jpg', '.jpeg', '.png')):
                    image = Image.open(BytesIO(r.content)).convert('RGB')
                    image.save(file_name, "PDF")
                else:
                    with open(file_name, "wb") as f_pdf:
                        f_pdf.write(r.content)

                log(f"✅ Fatura {id_fatura} salva como {file_name}")
                faturas_baixadas.append(file_name)
                success = True
                break

            except RequestException as e:
                log(f"⚠️ Tentativa {attempt} falhou para {id_fatura} (rede): {e}")
                time.sleep(1)
            except (OSError, IOError) as e:
                log(f"❌ Erro ao salvar fatura {id_fatura}: {e}")
                break

        if not success:
            log(f"❌ Não foi possível baixar a fatura {id_fatura} após {MAX_RETRIES} tentativas")
            faturas_falha.append(id_fatura)
            continue

        # Atualiza CSV
        try:
            with open(CSV_FILE, "a", newline="", encoding="utf-8") as f_csv:
                writer = csv.writer(f_csv)
                writer.writerow([id_fatura, due_date_str, url_fatura])
        except Exception as e:
            log(f"❌ Erro ao atualizar CSV para {id_fatura}: {e}")
            faturas_falha.append(id_fatura)
    else:
        log(f"⏭ Fatura {id_fatura} não vencida ainda ({due_date}) - não será baixada")
        faturas_ignoradas.append(f"{id_fatura} ({due_date_str})")

# -------------------------------
# RESUMO FINAL
# -------------------------------
log("\n===== RESUMO DE EXECUÇÃO =====")
log(f"Faturas baixadas: {len(faturas_baixadas)}")
for f in faturas_baixadas:
    log(f" - {f}")

log(f"\nFaturas ignoradas (não vencidas): {len(faturas_ignoradas)}")
for f in faturas_ignoradas:
    log(f" - {f}")

log(f"\nFaturas com falha: {len(faturas_falha)}")
for f in faturas_falha:
    log(f" - {f}")

log(f"\n✅ Processo concluído! Faturas salvas em {OUTPUT_DIR} e CSV atualizado em {CSV_FILE}")
log(f"📂 Log salvo em: {log_file_path}")
