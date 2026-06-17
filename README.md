<div align="center">

<br/>

# 🌌 NOCTIS
### *Rastreie suas conquistas entre as estrelas*

<br/>

> **NOCTIS** é um game tracker pessoal completo, onde você pode organizar sua biblioteca de jogos, acompanhar seu progresso, avaliar títulos, criar listas personalizadas e explorar o que está em alta — tudo com autenticação real e dados persistentes por usuário.

<br/>

![Stack](https://img.shields.io/badge/Frontend-React-61DAFB?style=for-the-badge&logo=react)
![Stack](https://img.shields.io/badge/Estilo-Tailwind_CSS-38BDF8?style=for-the-badge&logo=tailwindcss)
![Stack](https://img.shields.io/badge/Backend-FastAPI-009688?style=for-the-badge&logo=fastapi)
![Stack](https://img.shields.io/badge/Banco-SQLite-003B57?style=for-the-badge&logo=sqlite)
![Stack](https://img.shields.io/badge/API-RAWG-FF5722?style=for-the-badge)

</div>

<div align="center">
  
## 🛠️ Stack Tecnológica

| Camada | Tecnologia |
| :--- | :--- |
| **Linguagens** | HTML, JavaScript, Python |
| **Frontend** | React + Tailwind CSS |
| **Backend** | FastAPI |
| **Banco de Dados** | SQLite |
| **Autenticação** | JWT Token |
| **API Externa** | [RAWG Video Games Database](https://rawg.io/) |

</div>

## ✨ Funcionalidades

**1. 🔐 Tela de Login e Cadastro com JWT Token:**
Autenticação segura com tokens JWT. Cada usuário possui dados completamente isolados dos demais.

**2. 🔍 Busca de Jogos via API:**
Pesquisa em tempo real no catálogo da RAWG com mais de 500 mil títulos, com debounce automático e exibição de jogos populares na abertura.

**3. 🎮 Definição de Status por Jogo:**
Marque cada jogo com um status personalizado: `Jogado`, `Jogando`, `Quero Jogar`, `Abandonado` ou `Platinado`.

**4. 🔎 Filtragem por Gênero, Ano e Empresa:**
Filtre o catálogo por gênero, ano de lançamento, estúdio desenvolvedor e plataforma, de forma combinada.

**5. ⭐ Avaliação Facilitada com Estrelas, Comentários e Notas:**
Sistema de avaliação por critérios com meia estrela, comentário livre e nota geral calculada automaticamente.

**6. 🏆 Criação de Conquistas Manuais:**
Conquistas pré-definidas por jogo (Bosses Derrotados, Abates, Mortes, Assistências etc.) e conquistas personalizadas criadas pelo próprio usuário.

**7. 📋 Adição e Remoção Fácil de Jogos em Catálogos e Listas Personalizadas:**
Crie listas temáticas, adicione ou remova jogos com um clique e reordene como quiser.

**8. 👤 Página de Perfil com Estatísticas Pessoais:**
Veja seus dados em tempo real: jogos na biblioteca, gênero preferido, horas jogadas, melhor e pior jogo avaliado, conquistas desbloqueadas e sistema de ranks por progresso.

**9. 📈 Aba de Jogos Trending do Momento:**
Exibe os jogos mais adicionados no último ano e o Top 5 mais bem avaliados, com dados ao vivo da RAWG.

**10. 📖 Descrição dos Jogos:**
Cada jogo exibe sinopse traduzida para PT-BR automaticamente (API mymemory pode falhar em alguns casos sendo limitada a um número específico de caracteres), data de lançamento completa, nota da comunidade e plataformas disponíveis.

**11. ✏️ Mudança de Dados do Usuário:**
Na aba de Perfil, o usuário pode alterar nome, e-mail, senha e foto de perfil — com sincronização imediata no banco de dados e na interface.

---
## 📄 Documentação Do Projeto

Segue documentação em arquivo PDF dos detalhes do projeto: Descrição, Stack utilizada, 11 Funcionlidades aplicadas com exibição direta via código e Aplicação, Utilização e Motivação das Orientações a Objetos (Herança, Herança Abstrata, Polimorfismo e Encapsulamento):

#### https://drive.google.com/file/d/1XPNl6B6HocJony--JJRfUWtVZGWZIxq4/view?usp=drive_link
---
## 🏗️ Padrões de Projeto (Design Patterns)

Para garantir a escalabilidade, manutenção e um código limpo, o NOCTIS aplica princípios sólidos de engenharia de software, incluindo a implementação dos seguintes Padrões de Projeto:

### 1. Abstract Factory
* **Justificativa:** O projeto necessita criar famílias de objetos relacionados — como diferentes tipos de componentes visuais (cards de jogos, modais, itens de lista) e diferentes categorias de conquistas — sem acoplar o código a classes concretas específicas.
* **Implementação:** Aplicado na geração e renderização dinâmica dos elementos da interface gráfica e na estrutura de conquistas personalizadas. Através de fábricas de componentes, o frontend consegue instanciar diferentes visuais e comportamentos para os jogos com base em seus atributos, e até origem de importação dos dados, abstraindo a lógica de criação e permitindo que novos tipos de elementos sejam adicionados facilmente no futuro sem alterar a base existente. Esse padrão permite que, no futuro, o projeto tenha integração com diferentes fontes de dados: Steam, Epic, Riot, Xboxlive, PSN, etc..

### 2. Adapter
* **Justificativa:** O NOCTIS depende fortemente de uma API externa (RAWG Video Games Database). O formato dos dados brutos devolvidos por essa API difere do modelo de dados interno gerido pelo backend (FastAPI/SQLite) e esperado pelo frontend.
* **Implementação:** O padrão Adapter atua na camada de serviço do sistema como um tradutor. Ele recebe a carga de dados JSON da RAWG API e adapta (converte) essas informações para o contrato estrutural nativo do NOCTIS. Isso blinda a aplicação: se a RAWG alterar sua estrutura de resposta, apenas a classe Adapter precisará ser modificada, mantendo o resto do sistema intocável.

### 3. State
* **Justificativa:** A regra de negócios central do NOCTIS é baseada na transição de status dos jogos na biblioteca do usuário (`Quero Jogar`, `Jogando`, `Jogado`, `Abandonado` ou `Platinado`). O comportamento e as ações permitidas na interface dependem inteiramente deste estado atual.
* **Implementação:** O padrão State é utilizado para gerenciar o ciclo de vida do jogo na biblioteca do usuário. Em vez de usar extensas cadeias de `if/else` para definir regras condicionais (por exemplo, habilitar a função de dar nota apenas se o jogo estiver "Jogado" ou "Platinado"), a lógica de negócio é delegada aos respectivos estados. Cada status define o comportamento e as transições possíveis, tornando o código mais coeso e extensível.

---
## 🚀 Como Executar o Projeto

### Pré-requisitos

- [Node.js](https://nodejs.org/) (v18+)
- [Python](https://www.python.org/) (v3.10+)

---

### 📦 Instalação

**1. Clone o repositório**
```bash
git clone https://github.com/seu-usuario/noctis.git
cd noctis
```

**2. Instale as dependências do Frontend**
```bash
cd frontend
npm install
```

**3. Instale as dependências do Backend**
```bash
cd backend
python -m venv venv
```

---

### ▶️ Executando os Servidores

> ⚠️ É necessário rodar o **backend** e o **frontend** simultaneamente, cada um em um terminal separado.

**Terminal 1 — Backend (FastAPI)**
```bash
cd backend

# Windows
venv\Scripts\activate

# Linux / macOS
source venv/bin/activate

# Instalar dependências Python (apenas na primeira vez)
pip install -r requirements.txt

# Iniciar o servidor
uvicorn app.main:app --reload
```
> O backend estará disponível em `http://localhost:8000`

---

**Terminal 2 — Frontend (React)**
```bash
cd frontend
npm run dev
```
> O frontend estará disponível em `http://localhost:5173`

---

<div align="center">

<br/>

*© 2026 NOCTIS — Rastreie suas conquistas entre as estrelas* 🌌

</div>
