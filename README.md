# MSX **Graphos IV** - Suíte de Edição Gráfica (Python Edition)

![Graphos IV Logo](images/graphos_IV.png)

> ⚠️ **Status do Projeto: Em Desenvolvimento (Work in Progress)**
>
> Este software encontra-se em estado inicial de desenvolvimento (Alpha). Funcionalidades podem estar incompletas ou sujeitas a alterações. O objetivo é recriar a experiência do Graphos III com tecnologia moderna e o trabalho está em andamento contínuo.

Um ambiente gráfico moderno, desenvolvido em Python, para criar e visualizar imagens e recursos no formato **SCREEN 2** do MSX. Este projeto é uma homenagem e uma recriação funcional do icônico editor brasileiro **Graphos III** de Renato Degiovani.

## 🛠️ Pré-requisitos e Instalação

Para executar este projeto corretamente, certifique-se de ter o **Python 3.14** instalado em sua máquina.

### Configuração do Ambiente

Siga os passos abaixo para preparar o ambiente de execução:

1.  **Crie um ambiente virtual** (essencial para isolar as dependências do projeto):
    ```bash
    python -m venv .venv
    ```

2.  **Ative o ambiente virtual** (dependendo do seu sistema operacional):
    *   Windows: `.venv\Scripts\activate`
    *   Linux/Mac: `source .venv/bin/activate`

3.  **Instale as dependências** listadas no arquivo de requisitos:
    ```bash
    pip install -r requirements.txt
    ```

## 🚀 Como Executar

O sistema é modular, composto por um editor principal e visualizadores independentes. Com o ambiente virtual ativo (`.venv`), utilize os comandos abaixo no seu terminal:

### 🖥️ Editor Principal (Interface Unificada)
Para abrir a interface principal do Graphos IV, que centraliza o acesso a todas as ferramentas:
```bash
pip install -r requirements.txt
```

### 📂 Visualizadores Independentes (Viewers)
Caso deseje executar apenas os módulos de visualização separadamente:

*   **Visualizador de Alfabetos (.ALF):**
    ```bash
    python alphabetV.py
    ```
*   **Visualizador de Layouts (.LAY):**
    ```bash
    python layoutV.py
    ```
*   **Visualizador de Telas (.SCR):**
    ```bash
    python screenV.py
    ```
*   **Visualizador de Shapes (.SHP):**
    ```bash
    python shapeV_2.py
    ```

---

## 🎨 O Graphos IV: Funcionalidades

O **Graphos IV** expande o conceito original, não apenas oferecendo um editor de pixels, mas uma suíte completa. O foco permanece nas restrições clássicas do MSX1:
* Resolução de **256x192 pixels**.
* Paleta de **16 cores fixas**.
* Restrição de cor: **2 cores por bloco de 8x1 pixels**.

### Estrutura de Menus e Integração
A interface principal (`main.py`) organiza as funcionalidades e agora integra diretamente os visualizadores através da opção **Ver/Exportar**:

*   **Tela:** Controle de Display, Edição e Visualização (`screenV.py`).
*   **Alfabeto:** Ferramentas para edição de fontes e Visualização (`alphabetV.py`).
*   **Shapes:** Criação de sprites/blocos e Visualização (`shapeV_2.py`).
*   **Layout:** Gerenciamento de layouts (bitmaps comprimidos) e Visualização (`layoutV.py`).
*   **Arquivos:** Gerenciamento de disco, importação e exportação de dados.
*   **Versão do Sistema:** Informações sobre a build atual e créditos.

---

## 📂 Detalhes dos Utilitários de Visualização

Estes módulos permitem visualizar e converter arquivos legados originais do Graphos III.

### 1. Visualizador de Shapes (`shapeV_2.py`)
Ferramenta dedicada à leitura de arquivos `.SHP`. O Graphos III utilizava shapes para "carimbar" desenhos na tela.
*   **Funcionalidades:** Navegação, zoom visual (até 16x) e exportação.
![Shape Viewer](images/shapeV_2.png)

### 2. Visualizador de Alfabeto (`alphabetV.py`)
Ferramenta para carregar e inspecionar arquivos de fontes (`.ALF`).
![Alphabet Viewer](images/alphabetV.png)

### 3. Visualizador de Telas (`screenV.py`)
Carrega "dumps" de tela (`.SCR`). Permite visualizar a arte final pixel-perfect como seria no MSX.
![Screen Viewer](images/screenV.png)

### 4. Visualizador de Layouts (`layoutV.py`)
Ferramenta especializada na leitura de arquivos de Layout (`.LAY`), que utilizam compressão RLE proprietária contendo apenas o padrão de bits (sem cor).
![Layout Viewer](images/layoutV.png)

---

## ⚙️ Ferramentas Utilizadas

| Categoria | Ferramenta | Descrição |
| :--- | :--- | :--- |
| **Linguagem** | Python 3.14 | Linguagem base do projeto. |
| **GUI** | CustomTkinter | Interface gráfica moderna e responsiva. |
| **Dados** | SQLite3 | Armazenamento de projetos e metadados. |
| **Imagem** | PIL/Pillow | Manipulação de bits e exportação gráfica. |
| **IA** | Google Gemini | Apoio técnico em especificações VDP e arquitetura. |

## 📜 Referencial Histórico: Graphos III

O Graphos III foi um dos mais notáveis editores gráficos para o MSX brasileiro, criado por **Renato Degiovani**. Foi crucial para a comunidade MSX na década de 80, permitindo que usuários criassem telas de jogos e programas aproveitando ao máximo a restrição gráfica do SCREEN 2.

## 🤖 Suporte de IA

Este projeto conta com o auxílio do modelo de linguagem **Google Gemini** para validação de especificações técnicas do VDP (Video Display Processor) do MSX1, layout de memória da **SCREEN 2** (PNT, PCT, GGT) e otimização de código Python.

