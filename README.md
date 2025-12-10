# Redgtech Automação - Integração Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)
![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

Integração **não oficial** para placas de automação Redgtech (8, 16 e 32 canais) no Home Assistant.

Controle local das placas Redgtech via Home Assistant, sem depender de nuvem ou aplicativos externos.

---

## 📋 Funcionalidades

✅ **Controle local** via rede local (sem nuvem)  
✅ **Suporte a múltiplas placas** configuráveis  
✅ **Suporte a placas de 8, 16 e 32 canais**  
✅ **Failover automático** entre IP cabeado e WiFi  
✅ **Auto-recovery** - reinicia placa automaticamente se mudar de rede  
✅ **Estado otimista** - resposta instantânea na interface  
✅ **Config Flow** - configuração 100% pela interface do Home Assistant  
✅ **Entidades nomeáveis** - usa os nomes configurados na placa  
✅ **Sensor de estado** - monitora status da conexão

---

## 📦 Compatibilidade

| Produto               | Canais | Status        |
| --------------------- | ------ | ------------- |
| Placa Cloud 8 Canais  | 8      | ✅ Compatível |
| Placa Cloud 16 Canais | 16     | ✅ Compatível |
| Placa Cloud 32 Canais | 32     | ✅ Compatível |

**Requisitos**:

-   Home Assistant 2023.1 ou superior
-   Placa Redgtech conectada na mesma rede local
-   Conhecimento do IP da placa (fixo ou DHCP)

---

## 🚀 Instalação

1. **Baixe a integração**:

    - Faça download deste repositório (botão verde "Code" > "Download ZIP")
    - Ou clone via Git:
        ```bash
        git clone https://github.com/digossmi/home-assistant-redgtech-automacao.git
        ```

2. **Copie para o Home Assistant**:

    - Acesse a pasta de configuração do Home Assistant (onde fica o `configuration.yaml`)
    - Crie a pasta `custom_components` se não existir
    - Copie a pasta `redgtech_automacao` para dentro de `custom_components`:
        ```
        /config/
        └── custom_components/
            └── redgtech_automacao/
                ├── __init__.py
                ├── manifest.json
                ├── config_flow.py
                ├── coordinator.py
                ├── sensor.py
                ├── switch.py
                └── const.py
        ```

3. **Reinicie o Home Assistant**:
    - Vá em **Configurações** > **Sistema** > **Reiniciar**

---

## ⚙️ Configuração

### 1. Descobrir o IP da Placa

Antes de configurar, você precisa saber o **IP da sua placa Redgtech**. Existem algumas formas:

**Opção A**: Via aplicativo oficial Redgtech  
**Opção B**: No roteador, procure por dispositivos conectados  
**Opção C**: Use um scanner de rede (ex: Fing, Advanced IP Scanner)

**Dica**: Configure um **IP fixo** para a placa no roteador (reserva DHCP por MAC address) para evitar problemas futuros.

### 2. Adicionar a Integração

1. Vá em **Configurações** > **Dispositivos e Serviços**
2. Clique no botão **+ Adicionar Integração**
3. Procure por **"Redgtech Automação"**
4. Clique na integração quando aparecer

### 3. Configurar Placas

**Passo 1: Quantidade de Placas**

-   Informe quantas placas Redgtech você possui (1 a 10)

**Passo 2: Configuração de Cada Placa**

Para cada placa, informe:

| Campo                    | Descrição              | Exemplo         | Obrigatório |
| ------------------------ | ---------------------- | --------------- | ----------- |
| **Nome da Placa**        | Nome identificador     | `Placa Sala`    | ✅ Sim      |
| **IP Primário**          | IP cabeado (LAN)       | `192.168.1.100` | ✅ Sim      |
| **IP Secundário (WiFi)** | IP wireless (failover) | `192.168.1.150` | ❌ Opcional |
| **Número de Canais**     | 8, 16 ou 32            | `16`            | ✅ Sim      |

**Exemplo de Configuração**:

```
Nome da Placa: Casa Principal
IP Primário: 192.168.31.155
IP Secundário: 192.168.31.169 (opcional)
Número de Canais: 16
```

### 4. Finalizar

Clique em **Enviar** e a integração criará automaticamente:

-   ✅ 1 dispositivo por placa
-   ✅ X switches (8, 16 ou 32 conforme configurado)
-   ✅ 1 sensor de estado por placa

---

## 🎛️ Uso

### Controlar Canais

Após configurada, os canais aparecerão como **switches** no Home Assistant:

-   **Nome**: Usa o nome configurado na placa (ex: "Lustre Sala") ou padrão "Canal X"
-   **Estado**: ON/OFF sincronizado com a placa em tempo real
-   **Ações**: Ligar, desligar, alternar

**No Dashboard**:

```yaml
type: entities
entities:
    - switch.placa_sala_canal_1
    - switch.placa_sala_canal_2
    - switch.placa_sala_lustre_sala
```

**Em Automações**:

```yaml
action:
    - service: switch.turn_on
      target:
          entity_id: switch.placa_sala_lustre_sala
```

### Sensor de Estado

Cada placa cria um sensor que mostra:

-   **Estado**: `true` (online) ou `null` (offline)
-   **Atributos**: Estados individuais de cada canal (AC1, AC2, etc.) e nomes (Nm_1, Nm_2)

---

## 🔧 Funcionalidades Avançadas

### Failover Automático (IP Primário + Secundário)

Se você configurou **IP Secundário** (WiFi), a integração:

1. ✅ Tenta sempre o **IP Primário** (cabeado) primeiro
2. ⚠️ Se falhar 2x seguidas, tenta o **IP Secundário** (WiFi)
3. 🔄 Detecta que está no WiFi e envia comando `restart` automaticamente
4. ⏱️ Aguarda ~1 minuto para a placa voltar ao IP cabeado
5. ✅ Volta ao funcionamento normal

**Logs Indicativos**:

```
⚠️ placa_sala está no IP secundário (WiFi) 192.168.31.169
🔄 Auto-recovery: enviando restart para placa_sala voltar ao IP primário (cabo)
✅ placa_sala voltou para IP primário 192.168.31.155
```

### Estado Otimista

Quando você clica em ligar/desligar um switch:

-   Interface responde **instantaneamente** (não espera confirmação)
-   Estado permanece por **5 segundos** (modo otimista)
-   Após 5s, sincroniza com o estado real da placa
-   Se falhar, reverte ao estado anterior automaticamente

Isso garante **experiência fluida** mesmo com latência de rede.

---

## 🐛 Solução de Problemas

### Problema: "Não foi possível conectar à placa"

**Causa**: IP incorreto ou placa offline

**Solução**:

1. Verifique se o IP está correto
2. Teste acessar `http://IP_DA_PLACA/L` no navegador
3. Deve retornar um JSON com `{"success": true, "AC1": "0", ...}`
4. Se não funcionar, reinicie a placa

### Problema: "Dispositivos ficam indisponíveis"

**Causa**: Placa mudou de rede (cabeado ↔ WiFi) ou está instável

**Solução**:

1. Configure **IP Secundário** para ativar failover automático
2. Configure **IP fixo** no roteador para a placa
3. Verifique qualidade do sinal WiFi se usar wireless

### Problema: "Switches não atualizam o estado"

**Causa**: Polling lento ou placa sobrecarregada

**Solução**:

1. Aguarde até 60 segundos (intervalo de atualização automática)
2. Evite clicar rapidamente múltiplos switches (debounce de 1s)
3. Verifique logs em **Configurações** > **Sistema** > **Logs**

### Problema: "Integração não aparece"

**Causa**: Pasta copiada incorretamente ou falta reiniciar

**Solução**:

1. Confirme estrutura de pastas:
    ```
    /config/custom_components/redgtech_automacao/
    ```
2. Reinicie o Home Assistant **completamente**
3. Limpe cache do navegador (Ctrl+F5)

---

## 📊 Logs de Debug

Para ativar logs detalhados, adicione no `configuration.yaml`:

```yaml
logger:
    default: info
    logs:
        custom_components.redgtech_automacao: debug
```

Reinicie o Home Assistant e verifique os logs em **Configurações** > **Sistema** > **Logs**.

---

## 🤝 Contribuindo

Contribuições são bem-vindas!

### Como Contribuir

1. Faça um **Fork** deste repositório
2. Crie uma **branch** para sua feature: `git checkout -b minha-feature`
3. **Commit** suas mudanças: `git commit -m 'Adiciona nova feature'`
4. **Push** para a branch: `git push origin minha-feature`
5. Abra um **Pull Request**

### Reportar Bugs

Encontrou um bug? Abra uma [Issue](https://github.com/digossmi/home-assistant-redgtech-automacao/issues) descrevendo:

-   Versão do Home Assistant
-   Modelo da placa (8, 16 ou 32 canais)
-   Passos para reproduzir
-   Logs relevantes

---

## 📄 Licença

Este projeto está sob a licença **MIT**. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

## ⚠️ Disclaimer

Esta é uma integração **não oficial** desenvolvida de forma independente. Não possui vínculo com a **Redgtech** ou seus produtos oficiais.

Use por sua conta e risco. O autor não se responsabiliza por danos aos equipamentos ou problemas decorrentes do uso desta integração.

---

## 💬 Suporte

-   **Issues**: [GitHub Issues](https://github.com/digossmi/home-assistant-redgtech-automacao/issues)
-   **Discussões**: [GitHub Discussions](https://github.com/digossmi/home-assistant-redgtech-automacao/discussions)
-   **Documentação Oficial Redgtech**: [redgtech.com.br](https://redgtech.com.br)

---

## 📈 Roadmap

-   [ ] Suporte a agendamentos via integração
-   [ ] Suporte a temporizadores
-   [ ] Dashboard personalizado (Lovelace card)
-   [ ] Publicação no HACS oficial
-   [ ] Tradução para inglês
-   [ ] Suporte a outras placas Redgtech (caixa d'água, etc.)

---

**Desenvolvido por [@digossmi](https://github.com/digossmi)**
