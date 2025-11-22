import concurrent.futures
import asyncio
import aiohttp
from threading import Lock
import os
import sys
import re
import json
import time
import random
import hashlib
import urllib.parse
from io import BytesIO
from tqdm import tqdm
import base64
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from PIL import Image
import platform
import tempfile

MAX_THREADS_CONSULTAS = 6
MAX_THREADS_IMAGENS = 8
RESOLUCAO_MINIMA = (500, 500)
FILTRO_SEGURO = False

PALAVRAS_CHAVE_INTERNAS = [
    "topless", "sexy", "nude", "nudes", "nudez", "nsfw", "leaked", "leaks",
    "naked", "tits", "onlyfans", "uncensored", "boobs", "ass", "oral",
    "blowjob", "anal", "masturbating", "fuck", "fucking", "sucking", "sex",
    "deepfake", "xxx", "fap", "porn", "hardcore"
]

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:132.0) Gecko/20100101 Firefox/132.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15"
]

def obter_pasta_documentos():
    sistema = platform.system()
    
    if sistema == 'Windows':
        try:
            import ctypes
            from ctypes import wintypes, windll
            CSIDL_MYDOCUMENTS = 0x0005
            buf = ctypes.create_unicode_buffer(wintypes.MAX_PATH)
            windll.shell32.SHGetSpecialFolderPathW(None, buf, CSIDL_MYDOCUMENTS, False)
            pasta_docs = buf.value
            if pasta_docs and os.path.exists(pasta_docs):
                return pasta_docs
        except:
            pass
        
        try:
            import winreg
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                               r"Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders")
            pasta_docs = winreg.QueryValueEx(key, "Personal")[0]
            winreg.CloseKey(key)
            pasta_docs = os.path.expandvars(pasta_docs)
            if os.path.exists(pasta_docs):
                return pasta_docs
        except:
            pass
        
        user_profile = os.environ.get('USERPROFILE')
        if user_profile:
            nomes_possiveis = ['Documentos', 'Documents', 'Mis documentos', 'Meus Documentos']
            for nome in nomes_possiveis:
                pasta_teste = os.path.join(user_profile, nome)
                if os.path.exists(pasta_teste) and os.path.isdir(pasta_teste):
                    return pasta_teste
            return user_profile
    
    elif sistema == 'Linux' or sistema == 'Darwin':
        home = os.path.expanduser('~')
        
        try:
            xdg_config = os.path.join(home, '.config', 'user-dirs.dirs')
            if os.path.exists(xdg_config):
                with open(xdg_config, 'r') as f:
                    for line in f:
                        if 'XDG_DOCUMENTS_DIR' in line:
                            path = line.split('=')[1].strip().strip('"')
                            path = path.replace('$HOME', home)
                            if os.path.exists(path):
                                return path
        except:
            pass
        
        nomes_possiveis = ['Documents', 'Documentos', 'documents', 'documentos']
        for nome in nomes_possiveis:
            pasta_teste = os.path.join(home, nome)
            if os.path.exists(pasta_teste) and os.path.isdir(pasta_teste):
                return pasta_teste
        
        return home
    
    return os.getcwd()

def obter_pasta_temp():
    sistema = platform.system()
    
    if sistema == 'Windows':
        temp_base = os.environ.get('TEMP', os.path.join(os.environ.get('SYSTEMROOT', 'C:\\Windows'), 'Temp'))
    else:
        temp_base = tempfile.gettempdir()
    
    temp_dir = os.path.join(temp_base, "LustLens_Logs")
    try:
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
        return temp_dir
    except:
        return tempfile.gettempdir()

DELAY_REQUESTS = (1, 3)
MAX_TENTATIVAS = 3
TIMEOUT_REQUEST = 20

class SessionManager:
    def __init__(self):
        self.sessions = {}
    
    def get_session(self, domain):
        if domain not in self.sessions:
            session = requests.Session()
            session.headers.update(get_random_headers())
            session.cookies.set('lang', 'pt-BR')
            session.cookies.set('region', 'BR')
            self.sessions[domain] = session
        return self.sessions[domain]
    
    def rotate_session(self, domain):
        if domain in self.sessions:
            self.sessions[domain].close()
            del self.sessions[domain]
        return self.get_session(domain)

session_manager = SessionManager()

def get_random_headers():
    base_headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Cache-Control": "max-age=0",
        "DNT": "1",
        "Sec-CH-UA": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        "Sec-CH-UA-Mobile": "?0",
        "Sec-CH-UA-Platform": '"Windows"'
    }
    return base_headers

def limpar_tela():
    sistema = platform.system()
    if sistema == 'Windows':
        os.system('cls')
    else:
        os.system('clear')

def limpar_nome(nome):
    return nome.strip().replace(" ", "_").lower()

def carregar_palavras_chave():
    palavras_validas = [palavra.strip() for palavra in PALAVRAS_CHAVE_INTERNAS 
                        if palavra.strip() and not palavra.startswith("cole aqui")]
    if palavras_validas:
        print(f"[+] {len(palavras_validas)} keywords loaded")
        return palavras_validas
    else:
        print("[!] No valid keywords found")
        return []

def gerar_consultas(nome_modelo, palavras_chave):
    consultas = []
    for chave in palavras_chave:
        termo = f"{nome_modelo} {chave}"
        consultas.append(urllib.parse.quote_plus(termo))
    return consultas

def buscar_imagens_bing(consulta):
    links_imagens = set()
    domain = 'bing.com'
    
    for tentativa in range(MAX_TENTATIVAS):
        try:
            session = session_manager.get_session(domain)
            
            if tentativa > 0:
                session = session_manager.rotate_session(domain)
                time.sleep(random.uniform(3, 6))
            
            params = {
                'q': urllib.parse.unquote_plus(consulta),
                'form': 'HDRSC2',
                'first': '1',
                'count': '35',
                'adlt': 'moderate' if FILTRO_SEGURO else 'off',
                'qft': '+filterui:imagesize-large',
                'FORM': 'IRFLTR'
            }
            
            url = "https://www.bing.com/images/search?" + urllib.parse.urlencode(params)
            
            time.sleep(random.uniform(2, 5))
            
            response = session.get(url, timeout=TIMEOUT_REQUEST)
            response.raise_for_status()
            
            if "captcha" in response.text.lower() or response.status_code == 429:
                if tentativa < MAX_TENTATIVAS - 1:
                    time.sleep(random.uniform(10, 20))
                    continue
                else:
                    return []
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            imagens = soup.find_all('a', class_='iusc')
            for tag in imagens:
                m = tag.get("m")
                if m:
                    try:
                        data = json.loads(m)
                        if 'murl' in data:
                            link_img = data['murl']
                            if link_img.startswith("http"):
                                links_imagens.add(link_img)
                    except:
                        start = m.find('"murl":"') + 8
                        end = m.find('","', start)
                        if start > 7 and end > start:
                            link_img = m[start:end].replace("\\", "")
                            if link_img.startswith("http"):
                                links_imagens.add(link_img)
            
            patterns = [
                r'"murl":"([^"]*\.(?:jpg|jpeg|png|gif|webp))"',
                r'"imgurl":"([^"]*\.(?:jpg|jpeg|png|gif|webp))"',
                r'"turl":"([^"]*\.(?:jpg|jpeg|png|gif|webp))"'
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, response.text, re.IGNORECASE)
                for match in matches:
                    clean_url = match.replace('\\/', '/')
                    if clean_url.startswith('http') and len(clean_url) > 20:
                        links_imagens.add(clean_url)
            
            if len(links_imagens) > 5:
                break
                
        except requests.exceptions.RequestException as e:
            if tentativa < MAX_TENTATIVAS - 1:
                time.sleep(random.uniform(5, 10))
            continue
        except Exception as e:
            break
    
    return list(links_imagens)

def imagem_valida(url):
    for tentativa in range(2):
        try:
            from urllib.parse import urlparse
            domain = urlparse(url).netloc
            session = session_manager.get_session(domain)
            
            headers = session.headers.copy()
            headers.update({
                'Referer': f'https://{domain}/',
                'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
                'Sec-Fetch-Dest': 'image',
                'Sec-Fetch-Mode': 'no-cors',
                'Sec-Fetch-Site': 'cross-site'
            })
            
            response = session.get(url, headers=headers, timeout=15, stream=True)
            
            if response.status_code != 200:
                return False, None
            
            content_type = response.headers.get('Content-Type', '').lower()
            if not any(img_type in content_type for img_type in ['image/', 'jpeg', 'png', 'gif', 'webp']):
                return False, None
            
            content = b''
            for chunk in response.iter_content(chunk_size=8192):
                content += chunk
                if len(content) > 100000:
                    break
            
            try:
                img = Image.open(BytesIO(content))
                if img.size[0] >= RESOLUCAO_MINIMA[0] and img.size[1] >= RESOLUCAO_MINIMA[1]:
                    if len(content) < int(response.headers.get('Content-Length', '0')):
                        for chunk in response.iter_content(chunk_size=8192):
                            content += chunk
                    return True, content
            except Exception:
                return False, None
                
        except Exception:
            if tentativa == 0:
                time.sleep(random.uniform(1, 3))
                continue
            return False, None
    
    return False, None

def hash_imagem(conteudo):
    return hashlib.md5(conteudo).hexdigest()

def salvar_imagem(conteudo, pasta, hashes_existentes):
    hash_atual = hash_imagem(conteudo)
    if hash_atual in hashes_existentes:
        return False, None
    nome_arquivo = os.path.join(pasta, f"{hash_atual}.jpg")
    with open(nome_arquivo, "wb") as f:
        f.write(conteudo)
    hashes_existentes.add(hash_atual)
    return True, nome_arquivo

def gerar_galeria_html(pasta, arquivos):
    html_path = os.path.join(pasta, "gallery.html")
    nome_modelo = os.path.basename(pasta).replace('_', ' ').title()
    
    imagens_html_list = []
    for i, img in enumerate(arquivos, 1):
        nome_arquivo = os.path.basename(img)
        imagens_html_list.append(f'''
<div class="img-container" onclick="openModal('{nome_arquivo}',{i-1})">
<img src="{nome_arquivo}" alt="Image {i}" loading="lazy">
<div class="img-overlay"><span>#{i:03d}</span></div>
</div>''')
    
    imagens_html = f"galleryDiv.innerHTML = `{''.join(imagens_html_list)}`;"
    
    html_template = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{nome_modelo}</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{background:#fff;color:#202124;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif}}
.header{{background:#fff;border-bottom:1px solid #dadce0;padding:16px 24px;position:sticky;top:0;z-index:100}}
h1{{font-size:22px;font-weight:400;color:#202124}}
.count{{font-size:14px;color:#5f6368;margin-top:4px}}
.gallery{{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:8px;padding:24px}}
.img-container{{position:relative;overflow:hidden;background:#f8f9fa;cursor:pointer;aspect-ratio:1;border-radius:2px}}
.img-container img{{width:100%;height:100%;object-fit:cover;transition:opacity 0.2s}}
.img-container:hover img{{opacity:0.9}}
.img-overlay{{position:absolute;bottom:0;left:0;right:0;background:linear-gradient(transparent,rgba(0,0,0,0.6));padding:8px;opacity:0;transition:opacity 0.2s;color:#fff;font-size:12px}}
.img-container:hover .img-overlay{{opacity:1}}
.modal{{display:none;position:fixed;z-index:9999;left:0;top:0;width:100%;height:100%;background:#000;overflow:hidden}}
.modal.active{{display:flex;align-items:center;justify-content:center}}
.close{{position:fixed;top:16px;right:16px;color:#fff;font-size:32px;cursor:pointer;z-index:10001;width:48px;height:48px;display:flex;align-items:center;justify-content:center;background:rgba(0,0,0,0.5);border-radius:50%;transition:background 0.2s}}
.close:hover{{background:rgba(0,0,0,0.8)}}
.nav-arrow{{position:fixed;top:50%;transform:translateY(-50%);color:#fff;font-size:48px;cursor:pointer;z-index:10001;width:64px;height:64px;display:flex;align-items:center;justify-content:center;background:rgba(0,0,0,0.5);border-radius:50%;transition:background 0.2s;user-select:none}}
.nav-arrow:hover{{background:rgba(0,0,0,0.8)}}
.nav-prev{{left:24px}}
.nav-next{{right:24px}}
.modal-content{{position:relative;width:100%;height:100%;display:flex;align-items:center;justify-content:center;padding:80px}}
.modal-content img{{max-width:100%;max-height:100%;object-fit:contain;cursor:zoom-in}}
.modal-content img.zoomed{{cursor:zoom-out;max-width:none;max-height:none}}
@media (max-width:768px){{
.gallery{{grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:4px;padding:16px}}
.nav-arrow{{width:48px;height:48px;font-size:32px}}
.nav-prev{{left:8px}}
.nav-next{{right:8px}}
.modal-content{{padding:60px 8px}}
}}
</style>
</head>
<body>
<div class="header">
<h1>{nome_modelo}</h1>
<div class="count">{len_arquivos} photos</div>
</div>
<div class="gallery" id="gallery"></div>
<div id="modal" class="modal">
<span class="close" onclick="closeModal()">&times;</span>
<span class="nav-arrow nav-prev" onclick="event.stopPropagation();prevImage()">&#8249;</span>
<span class="nav-arrow nav-next" onclick="event.stopPropagation();nextImage()">&#8250;</span>
<div class="modal-content" id="modal-content">
<img id="modal-img" src="" alt="">
</div>
</div>
<script>
let images=[];let currentImageIndex=0;let scale=1;let translateX=0;let translateY=0;let isDragging=false;let startX=0;let startY=0;
function initGallery(){{const galleryDiv=document.getElementById('gallery');{imagens_html}
images=Array.from(document.querySelectorAll('.img-container img')).map(img=>img.src);}}
function openModal(src,index){{currentImageIndex=index;const modal=document.getElementById('modal');
const modalImg=document.getElementById('modal-img');modal.classList.add('active');
modalImg.src=src;resetTransform();}}
function closeModal(){{document.getElementById('modal').classList.remove('active');resetTransform();}}
function nextImage(){{currentImageIndex=(currentImageIndex+1)%images.length;
document.getElementById('modal-img').src=images[currentImageIndex];resetTransform();}}
function prevImage(){{currentImageIndex=(currentImageIndex-1+images.length)%images.length;
document.getElementById('modal-img').src=images[currentImageIndex];resetTransform();}}
function resetTransform(){{scale=1;translateX=0;translateY=0;updateTransform();
document.getElementById('modal-img').classList.remove('zoomed');}}
function updateTransform(){{const img=document.getElementById('modal-img');
img.style.transform=`translate(${{translateX}}px,${{translateY}}px) scale(${{scale}})`;}}
document.addEventListener('keydown',function(e){{if(document.getElementById('modal').classList.contains('active')){{
if(e.key==='Escape')closeModal();else if(e.key==='ArrowRight')nextImage();
else if(e.key==='ArrowLeft')prevImage();}}}});
const modalContent=document.getElementById('modal-content');
modalContent.addEventListener('wheel',function(e){{if(!document.getElementById('modal').classList.contains('active'))return;
e.preventDefault();const delta=e.deltaY>0?-0.1:0.1;const newScale=Math.max(0.5,Math.min(scale+delta,5));
if(newScale!==scale){{scale=newScale;updateTransform();
if(scale>1){{document.getElementById('modal-img').classList.add('zoomed');
document.getElementById('modal-img').style.cursor='grab';}}
else{{document.getElementById('modal-img').classList.remove('zoomed');
document.getElementById('modal-img').style.cursor='zoom-in';translateX=0;translateY=0;updateTransform();}}}}}},{{passive:false}});
const modalImg=document.getElementById('modal-img');
modalImg.addEventListener('click',function(e){{if(isDragging)return;
if(scale>1){{resetTransform();}}
else{{const rect=modalImg.getBoundingClientRect();const x=e.clientX-rect.left;const y=e.clientY-rect.top;
const xPercent=x/rect.width;const yPercent=y/rect.height;scale=2;
const naturalWidth=modalImg.naturalWidth;const naturalHeight=modalImg.naturalHeight;
const displayWidth=rect.width;const displayHeight=rect.height;
translateX=(0.5-xPercent)*displayWidth*(scale-1);translateY=(0.5-yPercent)*displayHeight*(scale-1);
updateTransform();modalImg.classList.add('zoomed');modalImg.style.cursor='grab';}}}});
modalImg.addEventListener('mousedown',function(e){{if(scale<=1)return;isDragging=true;
startX=e.clientX-translateX;startY=e.clientY-translateY;modalImg.style.cursor='grabbing';e.preventDefault();}});
document.addEventListener('mousemove',function(e){{if(!isDragging||scale<=1)return;
translateX=e.clientX-startX;translateY=e.clientY-startY;updateTransform();}});
document.addEventListener('mouseup',function(){{if(isDragging){{isDragging=false;
if(scale>1)modalImg.style.cursor='grab';else modalImg.style.cursor='zoom-in';}}}});
modalContent.addEventListener('click',function(e){{if(e.target===this&&!isDragging)closeModal();}});
window.addEventListener('load',initGallery);
</script>
</body>
</html>"""
    
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_template.format(
            nome_modelo=nome_modelo,
            len_arquivos=len(arquivos),
            imagens_html=imagens_html
        ))
    
    return html_path

def exibir_banner():
    MAGENTA = '\033[35m'
    RESET = '\033[0m'
    banner = f"""{MAGENTA}
 ██▓     █    ██   ██████ ▄▄▄█████▓    ██▓    ▓█████  ███▄    █   ██████ 
▓██▒     ██  ▓██▒▒██    ▒ ▓  ██▒ ▓▒   ▓██▒    ▓█   ▀  ██ ▀█   █ ▒██    ▒ 
▒██░    ▓██  ▒██░░ ▓██▄   ▒ ▓██░ ▒░   ▒██░    ▒███   ▓██  ▀█ ██▒░ ▓██▄   
▒██░    ▓▓█  ░██░  ▒   ██▒░ ▓██▓ ░    ▒██░    ▒▓█  ▄ ▓██▒  ▐▌██▒  ▒   ██▒
░██████▒▒▒█████▓ ▒██████▒▒  ▒██▒ ░    ░██████▒░▒████▒▒██░   ▓██░▒██████▒▒
░ ▒░▓  ░░▒▓▒ ▒ ▒ ▒ ▒▓▒ ▒ ░  ▒ ░░      ░ ▒░▓  ░░░ ▒░ ░░ ▒░   ▒ ▒ ▒ ▒▓▒ ▒ ░
░ ░ ▒  ░░░▒░ ░ ░ ░ ░▒  ░ ░    ░       ░ ░ ▒  ░ ░ ░  ░░ ░░   ░ ▒░░ ░▒  ░ ░
  ░ ░    ░░░ ░ ░ ░  ░  ░    ░           ░ ░      ░      ░   ░ ░ ░  ░  ░  
    ░  ░   ░           ░                  ░  ░   ░  ░         ░       ░  
{RESET}"""
    print(banner)

def buscar_consulta_paralela(args):
    consulta, i, total, pasta_destino, hashes, lock, pbar = args
    
    links_bing = buscar_imagens_bing(consulta)

    todos_links = list(set(links_bing))
    
    contador_validas = 0
    imagens_locais = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        future_to_url = {executor.submit(imagem_valida, url): url for url in todos_links}
        
        for future in concurrent.futures.as_completed(future_to_url):
            try:
                valida, conteudo = future.result()
                if valida and conteudo:
                    with lock:
                        salva, caminho = salvar_imagem(conteudo, pasta_destino, hashes)
                        if salva:
                            imagens_locais.append(caminho)
                            contador_validas += 1
            except Exception as e:
                pass
    
    pbar.update(1)
    pbar.set_postfix({"Images": len(imagens_locais)})
    
    return imagens_locais

def pad(s):
    return s + (16 - len(s) % 16) * chr(16 - len(s) % 16)

def unpad(s):
    padding = ord(s[-1])
    return s[:-padding]

def encrypt_ip(ip, key):
    iv = get_random_bytes(16)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    encrypted = cipher.encrypt(pad(ip).encode())
    return base64.b64encode(iv + encrypted).decode()

def decrypt_ip(encrypted_ip, key):
    raw = base64.b64decode(encrypted_ip)
    iv = raw[:16]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted = cipher.decrypt(raw[16:]).decode()
    return unpad(decrypted)

def registrar_ip_criptografado():
    try:
        temp_dir = obter_pasta_temp()
        ip = requests.get("https://api.ipify.org").text.strip()
        key = get_random_bytes(32)
        ip_criptografado = encrypt_ip(ip, key)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        log_file = os.path.join(temp_dir, "log_ips.txt")
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"{timestamp} | {ip_criptografado}\n")
        
        key_file = os.path.join(temp_dir, f"key_{datetime.now().strftime('%Y%m%d_%H%M%S')}.key")
        with open(key_file, "wb") as kf:
            kf.write(key)
        
        detail_log = os.path.join(temp_dir, "log_crypto.txt")
        with open(detail_log, "a", encoding="utf-8") as f:
            f.write(f"=== SESSION {timestamp} ===\n")
            f.write(f"Encrypted IP: {ip_criptografado}\n")
            f.write(f"Key (base64): {base64.b64encode(key).decode()}\n")
            f.write(f"Key file: {os.path.basename(key_file)}\n")
            f.write(f"{'='*40}\n\n")
    except Exception:
        pass

def escolher_pasta_destino():
    print("\n[>] Enter destination folder path: ", end="")
    caminho = input().strip()
    
    if not caminho:
        print("[!] Empty path. Using current directory.")
        return os.getcwd()
    
    caminho = os.path.expanduser(caminho)
    
    if os.path.isdir(caminho):
        return caminho
    else:
        try:
            os.makedirs(caminho, exist_ok=True)
            print(f"[+] Directory created: {caminho}")
            return caminho
        except Exception as e:
            print(f"[!] Error creating directory: {e}")
            print("[*] Using current directory")
            return os.getcwd()

def main():
    registrar_ip_criptografado()

    print("\n[>] Enter model/actress name: ", end="")
    nome_modelo = input().strip()
    if not nome_modelo:
        print("[!] Invalid name. Aborting.")
        return

    palavras_chave = [palavra.strip() for palavra in PALAVRAS_CHAVE_INTERNAS 
                     if palavra.strip() and not palavra.startswith("cole aqui")]

    if not palavras_chave:
        print("[!] No keywords configured. Aborting.")
        return

    consultas = gerar_consultas(nome_modelo, palavras_chave)
    nome_limpo = limpar_nome(nome_modelo)
    
    pasta_base = escolher_pasta_destino()
    pasta_destino = os.path.join(pasta_base, nome_limpo)
    os.makedirs(pasta_destino, exist_ok=True)

    hashes = set()
    lock = Lock()
    todas_imagens = []
    args_list = []

    with tqdm(
        total=len(consultas),
        desc="[*] Processing",
        bar_format='{desc}: {percentage:3.0f}%|{bar}|',
        colour='magenta'
    ) as pbar:
        for i, consulta in enumerate(consultas, 1):
            args_list.append((consulta, i, len(consultas), pasta_destino, hashes, lock, pbar))

        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(buscar_consulta_paralela, args) for args in args_list]

            for future in concurrent.futures.as_completed(futures):
                try:
                    resultado = future.result()
                    todas_imagens.extend(resultado)
                except Exception as e:
                    pass

    if todas_imagens:
        galeria = gerar_galeria_html(pasta_destino, todas_imagens)
        print(f"\n[+] SEARCH COMPLETED")
        print(f"[+] Total: {len(todas_imagens)} images")
        print(f"[+] Folder: {pasta_destino}")
        print(f"[+] Gallery: {galeria}\n")
    else:
        print(f"\n[!] NO IMAGES FOUND")
        print("[*] Tips:")
        print("   - Check keywords in PALAVRAS_CHAVE_INTERNAS")
        print("   - Try different name")
        print("   - Verify internet connection\n")

def verificar_dependencias():
    try:
        import requests
        import bs4
        import PIL
        return True
    except ImportError as e:
        print(f"[!] Missing dependency: {e}")
        print("[*] To install: pip install requests beautifulsoup4 pillow pycryptodome")
        return False

def menu_configuracoes():
    global RESOLUCAO_MINIMA, DELAY_REQUESTS, FILTRO_SEGURO
    
    while True:
        limpar_tela()
        exibir_banner()
        print(f"\n1. Min resolution: {RESOLUCAO_MINIMA[0]}x{RESOLUCAO_MINIMA[1]}")
        print(f"2. Request delay: {DELAY_REQUESTS[0]}-{DELAY_REQUESTS[1]}s")
        print(f"3. Safe search: {'ON' if FILTRO_SEGURO else 'OFF'}")
        print("0. Back")
        
        escolha = input("\n[>] Option: ").strip()
        
        if escolha == "1":
            try:
                largura = int(input("[>] Min width: "))
                altura = int(input("[>] Min height: "))
                RESOLUCAO_MINIMA = (largura, altura)
                print(f"[+] Resolution changed to {largura}x{altura}")
                time.sleep(1.5)
            except ValueError:
                print("[!] Invalid values")
                time.sleep(1.5)
                
        elif escolha == "2":
            try:
                min_delay = float(input("[>] Min delay (seconds): "))
                max_delay = float(input("[>] Max delay (seconds): "))
                if min_delay >= 0 and max_delay > min_delay:
                    DELAY_REQUESTS = (min_delay, max_delay)
                    print(f"[+] Delay changed to {min_delay}-{max_delay}s")
                    time.sleep(1.5)
                else:
                    print("[!] Invalid values")
                    time.sleep(1.5)
            except ValueError:
                print("[!] Invalid values")
                time.sleep(1.5)
        
        elif escolha == "3":
            print("\n[*] Safe Search:")
            print("1. Enable (filtered search)")
            print("2. Disable (no restrictions)")
            sub_escolha = input("\n[>] Option: ").strip()
            if sub_escolha == "1":
                FILTRO_SEGURO = True
                print("[+] Safe search ENABLED")
                time.sleep(1.5)
            elif sub_escolha == "2":
                FILTRO_SEGURO = False
                print("[+] Safe search DISABLED")
                time.sleep(1.5)
        
        elif escolha == "0":
            break

def menu_principal():
    while True:
        limpar_tela()
        exibir_banner()
        print("1. Start image search")
        print("2. Settings")
        print("0. Exit")
        
        escolha = input("\n[>] Option: ").strip()
        
        if escolha == "1":
            if not verificar_dependencias():
                input("\n[*] Press Enter to continue...")
                continue
            main()
            input("\n[*] Press Enter to continue...")
            
        elif escolha == "2":
            menu_configuracoes()
            
        elif escolha == "0":
            limpar_tela()
            print("\n[*] Exiting...")
            break
        else:
            print("[!] Invalid option")
            time.sleep(1)

if __name__ == "__main__":
    try:
        menu_principal()
    except KeyboardInterrupt:
        print("\n\n[!] Program interrupted by user")
    except Exception as e:
        print(f"\n[!] Unexpected error: {e}")