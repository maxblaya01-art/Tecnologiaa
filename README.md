# 📱 Tecnologia Store — Gerador de Divulgação Shopee

## ⭐ O que este projeto faz

Cole um link da Shopee no aplicativo e ele tenta preencher automaticamente:

- nome do produto;
- preço;
- preço anterior;
- desconto;
- imagem;
- link final.

Depois é possível gerar uma divulgação pronta, copiar o texto e compartilhar pelo Android.

---

# 🚀 COMO GERAR O APK PELO GITHUB

## Opção mais fácil

### 1. Crie um repositório
No GitHub, crie um repositório chamado:

`tecnologia-store-apk`

Pode deixar como **Public**.

### 2. Envie os arquivos

Extraia este pacote no celular/computador.

**IMPORTANTE:** envie a pasta `.github` também.

A estrutura final do GitHub deve ficar exatamente assim:

```text
tecnologia-store-apk/
├── .github/
│   └── workflows/
│       └── build-apk.yml
├── buildozer.spec
├── main.py
└── .gitignore
```

### 3. Faça o Commit

Depois que os arquivos aparecerem no GitHub, faça:

`Commit changes`

### 4. Abra Actions

No seu repositório:

**Actions → 🚀 Gerar APK Android**

### 5. Gere o APK

Toque em:

**Run workflow → Run workflow**

Espere terminar. A primeira compilação pode demorar bastante porque o Android SDK/NDK será preparado.

### 6. Baixe o APK

Quando aparecer uma execução com ✓ verde:

**Abra a execução → Artifacts → TecnologiaStore-APK**

Baixe o arquivo ZIP do artefato e extraia o APK.

---

# ⚠️ MUITO IMPORTANTE NO CELULAR

Se você estiver usando o navegador do Android e a pasta `.github` não aparecer para enviar, não continue sem ela.

O GitHub precisa receber:

`.github/workflows/build-apk.yml`

É esse arquivo que cria automaticamente o botão de compilação em **Actions**.

Se o GitHub não permitir enviar a pasta oculta pelo celular, use o método de upload pelo GitHub Codespaces ou Git/GitHub Desktop em um computador.

---

# 🛒 COMO USAR O APLICATIVO

1. Abra o APK.
2. Cole um link da Shopee.
3. Toque em **Buscar informações**.
4. Confira os dados encontrados.
5. Corrija algum campo se necessário.
6. Toque em **GERAR DIVULGAÇÃO**.
7. Toque em **COPIAR TEXTO** ou **COMPARTILHAR**.

---

# ⚠️ Sobre a Shopee

A Shopee pode alterar o HTML, exigir JavaScript, redirecionar links ou bloquear consultas automáticas. Quando isso acontecer, o aplicativo permite preencher/revisar os dados manualmente.

Para uma versão comercial mais robusta, a melhor solução é usar uma API ou integração oficialmente autorizada de afiliados, quando disponível.

---

# 🔥 PRÓXIMA VERSÃO

O projeto pode ser expandido para gerar automaticamente uma arte de divulgação semelhante ao modelo da Tecnologia Store, incluindo:

- foto do produto;
- nome;
- preço;
- preço anterior;
- percentual de desconto;
- botão visual de compra;
- identidade da Tecnologia Store;
- texto pronto para WhatsApp;
- compartilhamento da imagem;
- histórico de produtos;
- vários modelos de arte.



## 🔧 Correção para erro "Aidl not found"

O `buildozer.spec` desta versão já contém:

`android.accept_sdk_license = True`

Isso permite que o GitHub Actions aceite automaticamente as licenças do Android SDK durante a compilação. Sem isso, o SDK pode pular a instalação do Build-Tools e o Buildozer termina com `Aidl not found`.
