# 🚀 Mayday - O Guia do Desenvolvedor e Manual do Jogo 🎮

Olá, Kaiky! Este documento foi feito especialmente para você. Aqui, explico de forma **muito simples e direta** tudo o que construímos juntos no desenvolvimento do **Mayday**, como o jogo funciona por trás dos panos e como usar cada funcionalidade. Boa leitura!

---

## 🌌 1. O que é o Mayday?
**Mayday** é um jogo de plataforma 2D de ficção científica (Sci-Fi) onde você controla o **Sargento Kael Voss** no ano 3247. Após sua nave cair em um planeta florestal alienígena hostil, seu objetivo é sobreviver, enfrentar criaturas perigosas (Macacos e Pássaros alienígenas) e chegar até o **Beacon** (sinalizador de resgate) para ser salvo.

---

## 🛠️ 2. A Jornada de Desenvolvimento (Como o jogo evoluiu)
O jogo passou por várias fases de melhorias para chegar ao nível premium atual:

1. **A Base Física**: Criamos o movimento do jogador, pulo, gravidade e colisão simples com o chão e as plataformas.
2. **Ciclo de Testes (QA)**: Refinamos os pulos para que ficassem macios, ajustamos as colisões para o jogador não "afundar" ou ficar preso nas paredes, e calibramos a inteligência dos inimigos.
3. **O Editor de Níveis Interativo (Modo Dev)**: Para evitar ter que ficar mudando posições de plataformas no código toda hora, criamos um **Editor Visual**. Você aperta **`E`**, arrasta o que quiser com o mouse, calibra a altura dos inimigos com as setas do teclado e aperta **`Enter`** para salvar a fase inteira automaticamente!
4. **Design Moderno e Cyberpunk**: Substituímos os menus simples por uma interface futurista espetacular. O jogo agora baixa automaticamente fontes premium do Google Fonts (`Orbitron` e `Rajdhani`) e tem botões em formato de cápsula com neon brilhante que reagem ao passar o mouse.
5. **Menu de Pausa e Configurações**: Adicionamos o menu ao apertar **`Esc`** com um efeito sonoro incrível de abafamento da música, e uma tela de configurações onde você muda a resolução da tela e o volume arrastando o mouse na hora.
6. **Ajuste de Combate Final**: Corrigimos o combate contra os pássaros. Aumentamos a área de ataque do jogador para cima e para dentro de seu próprio corpo, tornando muito mais fácil e justo bater no pássaro quando ele dá o rasante de cima.

---

## 📂 3. Entendendo os Arquivos do Jogo (Sem complicação)
O código do jogo foi dividido em arquivos separados, cada um responsável por uma tarefa:

*   **`main.py` (O Coração)**: Controla o fluxo do jogo (se você está no menu, jogando, na tela de configurações ou pausado) e roda o loop infinito que atualiza as imagens na tela 60 vezes por segundo.
*   **`entities.py` (Os Personagens)**: Onde estão descritos os comportamentos do Jogador, do Macaco e do Pássaro. Controla a vida (HP), ataques, inteligência artificial dos inimigos e animações.
*   **`level.py` (O Cenário)**: Onde as plataformas, os checkpoints e o sinalizador final são gerados. Ele lê o arquivo salvo pelo editor (`level_data.json`) para carregar a fase exatamente como você a posicionou.
*   **`assets.py` (O Carregador)**: Responsável por gerenciar os arquivos visuais (imagens de fundo, animações) e arquivos sonoros (efeitos sonoros e música). Possui um sistema de segurança: se faltar algum som, ele roda em modo silencioso sem travar o jogo.
*   **`ui.py` (O Desenhista)**: Responsável por desenhar tudo o que é interface: a barra de vida (HUD), os botões de neon, os textos da história, o painel do editor de nível e o menu de pausa.
*   **`settings.py` (A Central)**: Guarda variáveis globais de configuração como a resolução atual, se o jogo está em tela cheia, o volume geral e se o FPS está ativo.

---

## 🎮 4. Funcionalidades do Jogo Explicas uma a uma

### 🏠 O Menu Principal
O menu de entrada tem um visual cyberpunk futurista. Ao passar o mouse nos botões chanfrados de neon, eles acendem com uma aura azul e expandem levemente com animação suave de aproximação. As opções são iniciar a missão, configurar ou fechar o jogo.

### 📜 A Tela de História (Story Screen)
Apresenta um texto contextualizando a missão do Sgt. Kael Voss antes da partida começar. Pressionar **`Espaço`** inicia o jogo.

### ⏸️ O Menu de Pausa (Tecla `Esc`)
Ao pressionar **`Esc`** durante a partida:
*   A ação é congelada instantaneamente.
*   **Abafamento Sonoro**: A música de fundo diminui de volume dinamicamente para **`30%`** do volume normal, dando um efeito de "abafado" muito profissional. Quando você despausa, o volume original retorna imediatamente.
*   O menu flutuante surge no centro da tela com cantos decorados e três botões: **Continuar**, **Configurações** e **Voltar ao Menu**.

### ⚙️ Tela de Configurações Dinâmica
Acessível a partir do Menu Principal ou do Menu de Pausa:
*   **Resolução Dinâmica**: Você pode alternar entre `1280x720`, `1600x900` e `1920x1080`. O Pygame recria a tela no mesmo instante e reajusta o tamanho de todas as imagens de fundo e textos automaticamente de forma proporcional.
*   **Modo de Tela**: Alterna entre Janela e Tela Cheia (Fullscreen).
*   **Slider de Volume Geral**: Uma barra onde você clica e arrasta o mouse para ajustar o volume de 0% a 100%. O som de fundo e os efeitos sonoros de ataques/pulos mudam na hora!
*   **Roteamento Inteligente**: Se você abriu as configurações a partir do Menu de Pausa, ao clicar em "VOLTAR" ele te devolve exatamente para a pausa! Se abriu do Menu Principal, volta para o Menu Principal. Suas preferências são salvas em `Assets/settings_data.json` e lembradas na próxima vez que você abrir o jogo.

### 🛠️ Modo Editor de Níveis (Modo Dev)
Se o "Modo Dev" estiver ativado nas Configurações, você pode pressionar **`E`** durante o jogo para entrar no modo de edição:
*   **Clique e Arraste**: Clique em qualquer plataforma, checkpoint, inimigo ou no próprio jogador com o mouse e arraste para o lugar que desejar.
*   **Ajuste Fino de Altura**: Selecione um personagem ou objeto e use as **Setas para Cima e para Baixo** do teclado para regular milimetricamente a altura vertical (altura do desenho) em relação ao solo.
*   **Salvar**: Pressione **`Enter`** para gravar a fase inteira em `Assets/level_data.json`.
*   Para voltar a jogar a fase que você acabou de criar, basta apertar **`E`** novamente!

---

## ⌨️ 5. Resumo de Controles e Atalhos do Jogo

| Tecla / Comando | Ação |
| :--- | :--- |
| **`A` / `D` (ou Setas)** | Mover o Sargento Kael Voss para Esquerda / Direita |
| **`Shift Esquerdo`** | Segurar para Correr mais rápido |
| **`W` / `Espaço`** | Pular (Segure para pular mais alto, solte para cair antes) |
| **`Botão Esquerdo do Mouse`** | Ataque Rápido / Leve (Soca com a lâmina) |
| **`Botão Direito do Mouse`** | Ataque Forte (Gira e joga os inimigos longe com empurrão) |
| **`Esc`** | Pausar / Despausar o jogo no meio da partida |
| **`E` (Com Modo Dev ligado)** | Entrar ou Sair do Modo Editor de Níveis |
| **`Clique + Arrastar` (No Editor)** | Mover plataformas, inimigos e objetos com o mouse |
| **`Seta Cima / Seta Baixo` (No Editor)** | Regular a altura de desenho do objeto selecionado |
| **`Enter` (No Editor)** | Salvar as posições atuais da fase no arquivo JSON |
| **`R` (Na tela de derrota)** | Reviver rapidamente no último checkpoint ativado |

---

Espero que este guia facilite o seu entendimento de toda a estrutura incrível que criamos para o **Mayday**! Qualquer dúvida ou alteração que quiser fazer no futuro, este manual estará aqui para te guiar. Divirta-se jogando! 🚀👽  
