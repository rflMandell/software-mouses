# Mouse Manager - Universal Mouse Management Software

Um software de gerenciamento e configuracao de mouses.

## Índice

* [Características](#-caracter%C3%ADsticas)

* [Requisitos do Sistema](#-requisitos-do-sistema)

* [Instalação](#-instala%C3%A7%C3%A3o)

* [Como Usar](#-como-usar)

* [Estrutura do Projeto](#-estrutura-do-projeto)

* [Funcionalidades Detalhadas](#-funcionalidades-detalhadas)

* [Solução de Problemas](#-solu%C3%A7%C3%A3o-de-problemas)

* [Desenvolvimento](#-desenvolvimento)

## Características

### **Detecção Automática**

* Detecta automaticamente todos os mouses conectados

* Identifica tipo de conexão (USB, Bluetooth, PS/2)

* Mostra informações do mouse selecionado

* Atualização em tempo real da lista de dispositivos

### **Configurações Avançadas**

* Ajuste de velocidade/sensibilidade do mouse

* Controle de aceleração

* Configuração de velocidade do duplo clique

* Troca de botões primário/secundário

* Configurações de scroll e wheel

### **Backup e Restauração**

* Backup automático das configurações

* Restauração rápida de configurações salvas

* Perfis personalizados para diferentes usuários

* Histórico de alterações

## Requisitos do Sistema

### **Sistema Operacional**

* Windows 7 ou superior

* **Recomendado:** Windows 10/11

### **Python**

* Python 3.7 ou superior

* **Recomendado:** Python 3.9+

### **Hardware**

* Pelo menos 50MB de espaço livre

* Resolução mínima: 800x600

* **Recomendado:** 1024x768+

### **Permissões**

* Permissões de usuário padrão

* **Administrador** para algumas configurações avançadas

## 🚀 Instalação

### **Método 1: Instalação Simples**

1. **Clone ou baixe o projeto:**

```bash
git clone https://github.com/rflMandell/software-mouses.git
cd software-mouses
```

1. **Execute diretamente:**

```bash
python main.py
```

### **Método 2: Ambiente Virtual (Recomendado)**

1. **Crie um ambiente virtual:**

```bash
python -m venv software-mouses_env
```

1. **Ative o ambiente:**

```bash
# Windows
software-mouses_env\Scripts\activate

# Linux/Mac (se aplicável)
source software-mouses_env/bin/activate
```

1. **Execute a aplicação:**

```bash
python main.py
```

### **Método 3: Dependências Opcionais**

Para funcionalidades avançadas, instale as dependências opcionais:

```bash
pip install psutil pywin32 pillow requests
python main.py
```

## 📖 Como Usar

### **1. Primeira Execução**

* Execute `python main.py`

* Uma mensagem de boas-vindas será exibida

* A aplicação criará automaticamente as pastas necessárias

### **2. Detectar Mouses**

* Clique em **"Atualizar Lista"** na aba "Detecção de Mouses"

* Todos os mouses conectados serão listados

* Clique em um mouse para ver informações detalhadas

### **3. Configurar Settings**

* Vá para a aba **"Configurações do Sistema"**

* Ajuste velocidade, aceleração e outras configurações

* Clique em **"Aplicar Configurações"** para salvar

### **4. Backup e Restauração**

* Use **"Criar Backup"** para salvar configurações atuais

* Use **"Restaurar Backup"** para voltar a configurações salvas

* Os backups ficam salvos na pasta `backups/`

### **5. Logs e Diagnósticos**

* Verifique a aba **"Logs"** para acompanhar operações

* Use **"Informações do Sistema"** para diagnósticos

* Logs detalhados ficam em `logs/software-mouses.log`

## 📁 Estrutura do Projeto

```
mouse-manager/
│
├── main.py                 # Arquivo principal de entrada
├── requirements.txt        # Dependências do projeto
├── README.md              # Este arquivo
│
├── modules/               # Módulos principais
│   ├── __init__.py
│   ├── mouse_detector.py  # Detecção de mouses
│   └── system_settings.py # Configurações do sistema
│
├── views/                 # Interface gráfica
│   ├── __init__.py
│   └── main_window.py     # Janela principal
│
├── logs/                  # Logs da aplicação (criado automaticamente)
│   └── mouse_manager.log
│
├── config/                # Configurações (criado automaticamente)
│   └── first_run.flag
│
├── backups/               # Backups das configurações (criado automaticamente)
│   └── backup_YYYYMMDD_HHMMSS.json
│
└── assets/                # Recursos opcionais
    └── icon.ico           # Ícone da aplicação (opcional)
```

## 🔧 Funcionalidades Detalhadas

### **Detecção de Mouses**

* **Scan automático** de dispositivos HID

* **Filtros** para identificar mouses

* **Cache otimizado** para melhor performance

* **Informações completas** de cada dispositivo

### **Configurações do Sistema**

* **Velocidade do ponteiro** (1-20)

* **Aceleração** (ligada/desligada)

* **Velocidade do duplo clique** (200-900ms)

* **Troca de botões** (destro/canhoto)

* **Configurações de scroll**

### **Sistema de Backup**

* **Backup automático** antes de alterações

* **Múltiplos pontos de restauração**

* **Validação de integridade** dos backups

* **Compressão automática** de arquivos antigos

### **Logs e Monitoramento**

* **Logs estruturados** com níveis de severidade

* **Rotação automática** de arquivos de log

* **Monitoramento em tempo real**

* **Exportação de relatórios**

## 🔧 Solução de Problemas

### **Problema: "Módulos não encontrados"**

**Solução:**

```bash
# Verifique se está no diretório correto
cd software-mouses

# Verifique a versão do Python
python --version

# Execute novamente
python main.py
```

### **Problema: "Permissões insuficientes"**

**Solução:**

* Execute o prompt de comando como Administrador

* Ou execute apenas as funções que não requerem privilégios elevados

### **Problema: "Interface não aparece"**

**Solução:**

```bash
# Verifique se o tkinter está instalado
python -c "import tkinter; print('OK')"

# Se der erro, reinstale o Python com tkinter
```

### **Problema: "Mouses não detectados"**

**Solução:**

* Verifique se os mouses estão conectados

* Clique em "Atualizar Lista" várias vezes

* Verifique os logs para erros específicos

### **Problema: "Configurações não aplicadas"**

**Solução:**

* Execute como Administrador para configurações do sistema

* Verifique se não há software de mouse conflitante

* Reinicie a aplicação após alterações

## 🛠️ Desenvolvimento

### **Executar Testes**

```bash
# Instalar dependências de desenvolvimento
pip install pytest black flake8 mypy

# Executar testes
pytest tests/

# Formatação de código
black .

# Linting
flake8 .
```

### **Estrutura de Desenvolvimento**

* **Modular:** Cada funcionalidade em módulo separado

* **Documentado:** Docstrings em todas as funções

* **Testável:** Estrutura preparada para testes unitários

* **Extensível:** Fácil adição de novas funcionalidades

### **Contribuindo**

1. Fork o projeto

2. Crie uma branch para sua feature

3. Commit suas alterações

4. Push para a branch

5. Abra um Pull Request

## 📝 Notas Importantes

* ⚠️ **Sempre faça backup** antes de alterar configurações importantes

* 🔒 **Algumas configurações** requerem privilégios de administrador

* 💾 **Logs são salvos automaticamente** para diagnósticos

* 🔄 **A aplicação detecta alterações** em tempo real

* 🎯 **Otimizada para Windows** mas preparada para expansão

## 📞 Suporte

* 📧 **Email:** [rflmandelcr@hotmail.com](mailto:rflmandelcr@hotmail.com)

* 🐛 **Issues:** GitHub Issues

* 💬 **Discussões:** GitHub Discussions

---

**Mouse Manager** - Dsenvolvido por um amante de mouses para outros amantes de mouses

_Versão 1.0.0 - Última atualização: 10/2025_