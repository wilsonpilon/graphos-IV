# MSX **GraphosPy** - Editor Gráfico SCREEN 2 (MSX-Inspired)

Um editor gráfico moderno, desenvolvido em Python, para criar imagens no formato **SCREEN 2** do MSX, inspirado no icônico editor brasileiro **Graphos III** de Renato Degiovani.

## 🚀 Sobre o Projeto

O **GraphosPy** é um projeto de "pixel art" focado nas restrições gráficas do MSX1 em seu modo **SCREEN 2 (Gráfico 2)**, que possui:

* Resolução de **256x192 pixels**.
* Paleta de **16 cores fixas** (a paleta MSX1).
* Restrição de cor: **2 cores (Foreground e Background) por bloco de 8x1 pixels** (linha de caractere).

O objetivo é recriar a experiência de edição e as ferramentas-chave do Graphos III (como editor de fontes/alfabeto e trabalho com *shapes*), utilizando uma interface gráfica moderna e multiplataforma.

## ⚙️ Ferramentas Utilizadas

| Categoria | Ferramenta | Descrição |
| :--- | :--- | :--- |
| **Linguagem Principal** | Python | Linguagem de programação robusta e versátil. |
| **Interface Gráfica (GUI)** | CustomTkinter (CTK) | Extensão do Tkinter para criar interfaces modernas, *cross-platform* e com temas customizáveis. |
| **Banco de Dados** | SQLite3 | Banco de dados leve e embutido (built-in do Python) ideal para armazenar dados do projeto como: paletas, pincéis personalizados, e metadados de imagens. |
| **Manipulação de Imagem** | PIL/Pillow | Biblioteca essencial para carregar, manipular e salvar os dados de pixel (incluindo a exportação no formato binário RAW/SCR do MSX SCREEN 2). |
| **Suporte de IA** | **Google Gemini** | Utilizado para acelerar o desenvolvimento, obter especificações técnicas precisas (como o *layout* de memória VDP do SCREEN 2), e sugerir arquiteturas e padrões de código. |

## 📐 Arquitetura Sugerida (MVC Simplificado)

Adotaremos uma arquitetura Model-View-Controller (MVC) simplificada para separar as responsabilidades do código, facilitando a manutenção e a adição de novos recursos.

1.  **Model (`msx_data_model.py`)**:
    * Gerencia os dados da imagem MSX SCREEN 2 (estrutura de 3 camadas: *Pattern Generator*, *Colour Table* e *Pattern Name Table*).
    * Implementa a lógica de restrição de 2 cores por bloco de 8x1 pixels.
    * Lida com a conversão de/para o formato binário do MSX (`.SCR` ou `.SC2`).
    * Gerencia a conexão e operações com o SQLite (salvar/carregar projetos, shapes, fontes).

2.  **View (`gui_view.py`)**:
    * Cria e gerencia a interface gráfica usando **CustomTkinter**.
    * Exibe a área de desenho (Canvas), a paleta de cores MSX, a janela de zoom/preview e os painéis de ferramentas.
    * Recebe a interação do usuário (cliques, movimentos do mouse).

3.  **Controller (`app_controller.py`)**:
    * Conecta o **Model** e a **View**.
    * Processa eventos do usuário (ex: "clicou na cor X", "usou a ferramenta linha", "salvar").
    * Atualiza o **Model** com as ações do usuário e notifica a **View** para redesenhar a tela.

## 🎨 Principais Recursos (Inspirados no Graphos III)

O projeto visa incorporar as funcionalidades que tornaram o Graphos III famoso:

* **Edição em Grade (Pixel-by-Pixel):** Área de desenho principal para a tela 256x192.
* **Editor de Paleta MSX:** Exibição das 16 cores fixas do MSX1.
* **Ferramentas Básicas:** Ponto, Linha, Círculo, Preenchimento (Flood-fill).
* **Zoom/Preview:** Uma janela menor mostrando a área do cursor com zoom e uma prévia da imagem final.
* **Editor de Alfabeto (Fontes 8x8):** Recurso para criar ou modificar caracteres (Patterns) 8x8 e manipular a Tabela de Cores (Colour Table) associada, fundamental para o SCREEN 2.
* **Sistema de Shapes:** Capacidade de salvar e carregar pequenos blocos de imagem (shapes/cliparts) para reutilização rápida (Ex: elementos de cenários de jogos).
* **Importação/Exportação:** Exportar a imagem para o formato binário do MSX SCREEN 2 (`.SCR` ou similar) para uso em emuladores ou MSX reais.

## 💾 Uso do SQLite

O banco de dados SQLite será usado para persistir dados estruturados do editor:

* **Tabela `SHAPES`:** Armazenará pequenos fragmentos de dados (Pattern, Colour e Name Tables) para o sistema de Shapes.
* **Tabela `FONTES`:** Armazenará conjuntos de caracteres 8x8 personalizados criados pelo usuário.
* **Tabela `PROJETOS`:** Salvará o estado completo do projeto (a matriz 256x192 + os dados de cor) para que o usuário possa continuar a edição.

## 📜 Referencial Histórico: Graphos III

O Graphos III foi um dos mais notáveis editores gráficos para o MSX brasileiro, criado por **Renato Degiovani**. Foi crucial para a comunidade MSX na década de 80, permitindo que usuários criassem telas de jogos e programas aproveitando ao máximo a restrição gráfica do SCREEN 2. Sua arquitetura de edição baseada em caracteres 8x8 e o suporte a *shapes* e alfabeto o tornaram uma ferramenta poderosa e um ícone do software nacional.

## 🤖 Suporte de IA: Google Gemini

Este projeto conta com o auxílio do modelo de linguagem **Google Gemini** para:

* **Apoio Técnico:** Confirmação de especificações do VDP (Video Display Processor) do MSX1 e do *layout* de memória da **SCREEN 2** (PNT, PCT, GGT).
* **Sugestão de Código:** Geração de *snippets* de Python, CustomTkinter e consultas SQLite para tarefas repetitivas.
* **Revisão de Arquitetura:** Validação do design MVC e da estrutura de classes.

A colaboração com a IA visa garantir a fidelidade técnica às restrições do hardware MSX e otimizar o processo de desenvolvimento.
