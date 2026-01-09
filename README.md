# 🎮 Pixel Dash

Pixel Dash é um jogo de plataforma 2D desenvolvido em Python utilizando a biblioteca Pygame Zero. O jogador deve atravessar um longo nível repleto de plataformas, inimigos e obstáculos, coletando moedas e alcançando o final da fase.

---

## 📌 Visão Geral

- **Gênero:** Plataforma 2D
- **Linguagem:** Python
- **Biblioteca:** Pygame Zero
- **Objetivo:** Chegar ao final do nível e coletar o máximo de moedas possível

---

## 🕹️ Controles

| Tecla | Ação |
|-----|-----|
| A ou ← | Mover para a esquerda |
| D ou → | Mover para a direita |
| W, ↑ ou Espaço | Pular |
| Pulo no ar | Executa pulo duplo |

---

## 🎯 Mecânicas do Jogo

- Sistema de gravidade
- Pulo duplo
- Câmera com rolagem horizontal
- Colisão com plataformas, inimigos e moedas
- Sistema de pontuação
- Música e efeitos sonoros ativáveis/desativáveis no menu

---

## 👾 Inimigos

- **Walkers:** Andam horizontalmente entre dois pontos
- **Flyers:** Inimigos voadores com movimento horizontal
- **Jumpers:** Saltam periodicamente
- **Swoopers:** Movimentação senoidal
- **Spikes:** Espinhos fixos (contato é sempre fatal)

> Alguns inimigos podem ser derrotados ao serem atingidos por cima.

---

## 🪙 Moedas

- Total de moedas no nível: **30**
- As moedas são animadas
- Coletar todas as moedas libera uma mensagem especial ao finalizar o nível

---

## 🧩 Estados do Jogo

- **Tutorial**
- **Menu**
- **Playing**
- **Game Over**
- **Complete (Nível Concluído)**

---

## 🔊 Áudio

O jogo possui:
- Música de fundo
- Sons de pulo, coleta de moedas, derrota de inimigos, vitória e game over

Caso algum arquivo de áudio não seja encontrado, o jogo continua funcionando normalmente.

---

## 🧱 Estrutura do Nível

- Plataformas de diferentes tamanhos
- Obstáculos com espinhos
- Inimigos distribuídos progressivamente
- Bandeira animada indicando o final da fase

---

## ▶️ Como Executar

1. Instale o Python 3.x  
2. Instale o Pygame Zero:
   ```bash
   pip install pgzero
