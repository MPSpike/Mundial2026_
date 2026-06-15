# Mundial 2026 — Calendário Automático

Este pacote contém tudo o que precisas para teres a página do Mundial 2026
sempre atualizada automaticamente, com deploy num URL gratuito.

## O que está aqui

- `index.html` — a página do calendário (a mesma que já tinhas)
- `update_results.py` — script que vai buscar os resultados mais recentes
  ao [openfootball/worldcup.json](https://github.com/openfootball/worldcup.json)
  (fonte gratuita, sem necessidade de chave de API) e atualiza o `index.html`
- `.github/workflows/update-results.yml` — automação que corre este script
  todos os dias e faz commit das alterações

---

## PASSO 1 — Criar o repositório no GitHub

1. Vai a [github.com/new](https://github.com/new)
2. Nome do repositório: por exemplo `mundial2026`
3. Visibilidade: **Public** (necessário para o plano gratuito do Netlify)
4. Cria o repositório (não acrescentes README/licença, vamos fazer upload)

## PASSO 2 — Fazer upload destes ficheiros

**Opção A — pela interface web (mais simples):**

1. No repositório novo, clica em **"uploading an existing file"**
2. Arrasta TODOS os ficheiros e pastas deste pacote (incluindo a pasta `.github`
   com a sua estrutura interna — o GitHub mantém a estrutura de pastas)
3. Escreve uma mensagem de commit (ex: "Setup inicial") e confirma

**Opção B — por linha de comandos (se tiveres git instalado):**

```bash
cd pasta-onde-descomprimiste-o-zip
git init
git remote add origin https://github.com/SEU-UTILIZADOR/mundial2026.git
git add .
git commit -m "Setup inicial"
git branch -M main
git push -u origin main
```

## PASSO 3 — Ativar o GitHub Actions (automação diária)

1. No repositório, vai ao separador **Actions**
2. Se aparecer um aviso a perguntar se queres ativar workflows, clica em
   **"I understand my workflows, go ahead and enable them"**
3. Devias ver o workflow **"Atualizar resultados Mundial 2026"** listado
4. Para testar imediatamente: clica nele → **"Run workflow"** → **"Run workflow"**
   (botão verde) — isto corre a atualização manualmente uma vez

A partir daqui, este workflow corre **automaticamente todos os dias às 08:00 UTC**
(09:00 ou 10:00 em Portugal, dependendo da hora de verão) e atualiza o `index.html`
com os resultados mais recentes, fazendo commit dessas alterações.

## PASSO 4 — Deploy automático com Netlify (URL gratuito)

1. Vai a [app.netlify.com/signup](https://app.netlify.com/signup) e cria conta
   (podes usar "Sign up with GitHub" — mais rápido)
2. No painel, clica em **"Add new site"** → **"Import an existing project"**
3. Escolhe **GitHub** e autoriza o acesso
4. Seleciona o repositório `mundial2026`
5. Configurações de build:
   - **Build command:** deixa vazio
   - **Publish directory:** `.` (ponto, significa a raiz do repositório)
6. Clica em **"Deploy site"**

Em ~30 segundos tens um URL tipo `https://random-name-123.netlify.app`

### Personalizar o nome do subdomínio

1. No painel do site, vai a **"Site configuration"** → **"Change site name"**
2. Escolhe um nome, ex: `mundial2026-pt` → fica `mundial2026-pt.netlify.app`

---

## Como funciona o ciclo completo

```
Todos os dias às 08:00 UTC:
  GitHub Actions corre update_results.py
        ↓
  Script vai buscar resultados ao openfootball/worldcup.json
        ↓
  Atualiza os placares (value=) no index.html
        ↓
  Recalcula a tabela de classificação dos grupos
        ↓
  Faz commit + push das alterações
        ↓
  Netlify deteta o novo commit automaticamente
        ↓
  Faz deploy da nova versão (1-2 minutos)
        ↓
  A tua página fica atualizada, sem qualquer ação manual!
```

## Testar manualmente sem esperar pelo cron

No separador **Actions** do repositório, abre o workflow e clica em
**"Run workflow"** sempre que quiseres forçar uma atualização imediata.

## Notas

- Os jogos sem resultado final continuam com os campos vazios, como pediste
- Se quiseres mudar o horário da atualização diária, edita a linha `cron`
  em `.github/workflows/update-results.yml` (formato: minuto hora dia mês dia-semana, em UTC)
- Se quiseres usar um domínio próprio mais tarde, no Netlify vai a
  **"Domain management"** → **"Add a domain"** e segue as instruções de DNS
