

# 🖐️ Controle de Cursor com Gestos da Mão (OpenCV + MediaPipe + PyAutoGUI)

Este projeto permite controlar o **cursor do mouse**, realizar **cliques esquerdo/direito** e até mesmo **rolar páginas verticalmente**, tudo com **gestos das mãos capturados pela webcam**, utilizando as bibliotecas **OpenCV**, **MediaPipe** e **PyAutoGUI**.


## 🧰 Tecnologias Utilizadas

* [Python](https://www.python.org/)
* [OpenCV](https://opencv.org/)
* [MediaPipe](https://google.github.io/mediapipe/)
* [PyAutoGUI](https://pyautogui.readthedocs.io/)

## 📦 Instalação

1. **Clone o repositório:**

```bash
git clone https://github.com/seu-usuario/nome-do-repo.git
cd nome-do-repo
```

2. **Crie um ambiente virtual (opcional, mas recomendado):**

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
```

3. **Instale as dependências:**

```bash
pip install -r requirements.txt
```


## ▶️ Como Usar

1. Execute o script:

```bash
python controle_mao.py
```

2. Use os seguintes gestos para controlar o mouse:

### 🖱️ Controle de Cursor

* Aponte com o dedo **indicador esticado** para mover o cursor.

### 👆 Clique Esquerdo

* **Toque o polegar no indicador**.

### 👉 Clique Direito

* **Toque o polegar no dedo médio**.

### 📜 Rolagem de Página

* Estique os dedos **indicador e médio**, com os dedos **anelar e mínimo curvados**.
* Mova os dedos para cima ou para baixo para rolar a página.

### ❌ Encerrar

* Pressione `Q` ou `Ctrl + C` no terminal para sair.

---

## ⚙️ Ajustes e Parâmetros

Você pode personalizar diversos parâmetros no código:

* `smoothening`: suavização do movimento do cursor.
* `CLICK_COOLDOWN_TIME`: tempo mínimo entre cliques.
* `SCROLL_SENSITIVITY`: velocidade da rolagem.
* `FINGERS_CLOSE_THRESHOLD_X_SCROLL`: distância máxima entre dedos indicador e médio para ativar o gesto de rolagem.

---

## 🚨 Cuidados

* **Iluminação adequada** ajuda na detecção dos gestos.
* **Evite sobreposição de dedos**, pois pode dificultar a detecção correta.
* **Desative o modo "failsafe" do PyAutoGUI** (já está feito no script).

---

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

