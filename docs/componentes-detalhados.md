# Microwear S11 Pro — componentes detalhados

## Escopo e critério de leitura

Este relatório consolida **exclusivamente** os resultados estruturados e as fontes fornecidas, sem nova pesquisa. Ele descreve os dez artefatos extraídos do contêiner JLFS. A classificação e a função são separadas para não transformar associação contextual em identificação de formato ou de hardware.

- **Demonstrado**: diretamente observado no arquivo, reproduzido por cálculo/validação indicada no resultado, ou explicitamente descrito por um parser/documento citado.
- **Hipótese**: interpretação plausível, associação contextual ou comparação com outra família/SDK; não deve ser tratada como identificação confirmada.
- **CRC externo/JLFS**: valida a entrada no contêiner, quando indicado, mas não necessariamente o formato interno do payload.
- CRCs calculados sobre o arquivo são mantidos como **fingerprints** quando não há campo esperado, algoritmo e escopo conhecidos.

## Visão consolidada

| Artefato | Classificação consolidada | Função provável | Confiança principal |
|---|---|---|---|
| `00002020_app.bin` | Imagem bruta de aplicação JLFS, binário heterogêneo/possivelmente segmentado | Payload de aplicação | Moderada para a categoria; baixa para arquitetura e compressão |
| `00000020_uboot.boot` | Primeiro membro JLFS, SPL/`uboot.boot`, marcado como comprimido | Inicialização/SPL | Moderada para o papel e a flag; baixa para codec e plataforma |
| `00242a9b_upgrade.res` | Payload proprietário/variante RU30 | Recurso associado a `ui_upgrade` | Alta para observações; baixa para semântica/formato |
| `00242abb_upgrade.str` | Recurso binário de UI JieLi com assinatura RU30 | Recurso de UI, função específica desconhecida | Moderada para UI; baixa para schema e compatibilidade |
| `00242adb_upgrade.sty` | Provável recurso/descritor de UI JLUI/JieLi | Descritor/estilo do recurso `upgrade` | Média para associação de UI; baixa para layout |
| `0024b3f1_p11_code.bin` | Provável payload/recurso P11 de entrada de empacotador | Código/recurso P11 | Média para o papel; baixa para estrutura |
| `0024ef19_config.dat` | Estrutura de configuração JCRT | Configuração de versão, identidade, IO e chave | Alta para estrutura/CRC; baixa a moderada para semântica e alvo |
| `0024f0b9_eq_cfg_hw.bin` | Provável blob de configuração de EQ/efeitos | Perfis de áudio, roteamento e EQ | Média para a função ampla; baixa para formato/plataforma |
| `00002040_cfg_tool.bin` | Provável recurso de configuração/runtime JieLi | Tabela de slots/perfis | Média para a categoria; baixa para layout/origem |
| `002114bb_index.idx` | Índice TIDX de diretório de tons | Índice de nomes de tons por ID | Alta para estrutura e classificação |

---

## 1. `00002020_app.bin`

**Caminho:** `work/decoded/jlfs/00002020_app.bin`  
**ID:** `app.bin`

### Classificação e função provável

- **Demonstrado:** imagem bruta de aplicação extraída do JLFS, com 2.158.452 bytes, sem contêiner autoidentificável observável.
- **Função provável:** payload de aplicação, aparentemente heterogêneo e possivelmente segmentado.
- **Hipótese não confirmada:** partes comprimidas no formato proprietário `LZ4-packet` e presença de seções equivalentes às descritas em receitas de outros SDKs. Não é possível indicar offsets, limites de segmentos ou partes descompactáveis com segurança.

### Evidências e CRC

- SHA-256: `94dce0755d4c70f26f870fe1429deb7183bd4090429daab79b21522192d977be`.
- O cabeçalho e o CRC16 da entrada JLFS conferem segundo o contexto fornecido; isso valida a extração/entrada do contêiner, não identifica o layout interno da aplicação.
- Identificado apenas como `data`; não há cabeçalho ELF nem magic de LZ4-frame observável no início.
- Prefixo observado: `ee ff 40 60 10 00 ed ff 40 60 10 00 d8 e8 07 00`.
- Strings são majoritariamente não legíveis.
- A entropia em blocos de 64 KiB varia aproximadamente entre 6,8 e 7,1 bits/byte em boa parte da região inicial; há regiões posteriores de menor entropia e regiões com zeros. Isso **não** delimita compressão ou seções.
- Não foi atribuído CRC interno ao payload.

### Confiança

**Moderada** para a classificação geral como payload de aplicação binário heterogêneo; **baixa** para família/arquitetura, algoritmo de compressão e localizações de segmentos.

### Fontes

- [Jieli SDK build / app.bin — referência BR35/AC707N](https://github.com/ElectronicCats/jieli-ble-badge-research/blob/main/docs/jieli-sdk-build.md): descreve, em outro contexto, concatenação de seções e segmento `dat_bank.lz4` produzido por `lz4_packet` com dicionário `.text`.
- [Referência BR52 — `download.c`](https://gitlab.zh-jieli.com/ai_test/jl709n/-/blob/feature_vivo_01_04/SDK/cpu/br52/tools/download.c): descreve concatenação com `lz4_packet` para outra família.

As duas referências são **comparativas**. Não demonstram compatibilidade com JL701N nem transferem a identificação de BR35/AC707N, BR52 ou RU2 para este arquivo.

---

## 2. `00000020_uboot.boot`

**Caminho:** `work/decoded/jlfs/00000020_uboot.boot`  
**ID:** `uboot.boot`

### Classificação e função provável

- **Demonstrado pelo parser público/contexto:** payload do primeiro membro JLFS, nomeado `SPL/uboot.boot`; a entrada tem flag `0x40`. A [especificação pública de novo firmware JieLi](https://kagaimiq.github.io/jielie/datafmt/newfw.html) diz que essa flag indica compressão LZ4 para `uboot.boot` em famílias como BR23/BR25/BR28.
- **Função provável:** estágio inicial de boot/SPL.
- **Ainda não testado neste artefato:** descompressão LZ4 nem validação da imagem de saída; compatibilidade de execução com esta PCB também não foi demonstrada.

### Evidências e CRC

- Tamanho: 5.551 bytes.
- SHA-256: `b919036982cb8bd9ba7faa1159a3a13b46fb704f127316e167a37804359bf0db`.
- Bytes iniciais: `fe df 00 0a 1f 3e 6a f8 e0 c1 a3 67 29 2a 9b 63 ff df 9d 1f 1f 3e 7c f8 f0 41 b5 67 ae a5 5b 97`.
- `file` reconhece somente `data`; não foram encontradas strings ASCII nem ocorrências de `JLFS`, `LZ4`, `uboot`, `AC707N`, `BR35` ou `JL701N`.
- CRC32 padrão zlib calculado sobre o arquivo: `0x4d7cd849`. É apenas um valor calculado; não existe, nos dados fornecidos, CRC esperado nem convenção conhecida que permita validá-lo.

### CRC e transformação bankcb

O payload raw de 5.551 bytes tem CRC-16 calculado `0xAFF9`, diferente do `data_crc` JLFS `0xDC88`. Isso era um falso negativo causado por comparar bytes ainda bankcb-scrambled. Após `descramble_bankcb`, em cópia separada, o CRC-16 da entrada inteira confere com `0xDC88`. O cabeçalho bankcb também confere (`0xF4C0` sobre `[0x00,0x0E)`), assim como o corpo do banco (`0x97E7` sobre `[0x10,0x15AF)`). O artefato descrambled é mantido separado do payload raw.

A flag `0x40` é documentada como LZ4 na [especificação pública JieLi](https://kagaimiq.github.io/jielie/datafmt/newfw.html) para `uboot.boot`. A etapa executada foi somente bankcb descramble; **nenhum descompressor LZ4 foi aplicado**. O CRC32 zlib `0x4D7CD849` do arquivo raw é apenas uma fingerprint, sem campo esperado associado.

### Confiança

**Alta** para a correspondência dos CRCs bankcb/JLFS após descramble; **moderada** para a função SPL e para a leitura de LZ4 documentada pela especificação; **baixa** para execução, endereço de carga e compatibilidade com esta placa.

### Fonte

- [Formato público de novo firmware JieLi](https://kagaimiq.github.io/jielie/datafmt/newfw.html): associa bit `0x40` a LZ4 para `uboot.boot` em formatos de chips Bluetooth como BR28.
- [Parser público `fwunpack_newfw.py`](https://github.com/kagaimiq/jl-misctools/blob/main/firmware/fwunpack_newfw.py): trata o primeiro membro como SPL, aplica `descramble_bankcb` e registra a flag de compressão.

---

## 3. `00242a9b_upgrade.res`

**Caminho:** `work/decoded/jlfs/00242a9b_upgrade.res`  
**ID:** `upgrade.res`

### Classificação e função provável

- **Demonstrado:** arquivo binário de 31.843 bytes com magic ASCII `RU30` nos bytes 0–3.
- **Função provável:** payload proprietário/variante RU30 associado contextualmente ao recurso de UI `ui_upgrade`.
- **Hipótese não confirmada:** layout interno, semântica dos campos, subformato RU30 e compatibilidade com RU2, JL701N, BR35/AC707N ou outras famílias.
- **Metadado de versão irmão:** o diretório `ui_upgrade` também contém `upgrade.json`, que declara literalmente `version_id: "W002"`; isso é um identificador de versão do pacote, não uma versão semântica confirmada. Detalhes e CRCs estão em [upgrade_json.md](component-findings/upgrade_json.md).

### Evidências e CRC

- Cabeçalho opaco ocupa pelo menos `0x00–0x4f`; a região `0x50..EOF` contém 31.763 bytes binários.
- Campos observados:
  - `0x04–0x07`: `00 03 01 00`;
  - `0x08–0x0b`: `01 00 00 00`;
  - `0x0c–0x0f`: `df 6c 47 e5`;
  - `0x30–0x4f`: outros campos binários sem interpretação validada.
- SHA-256: `0f978805ff0fc4bde0513cb45b97911ab1ff9050106e2596756e867e5deef44e`.
- CRC-32 padrão:
  - arquivo inteiro: `0x6f346916`;
  - após os quatro bytes iniciais: `0xcbd87dad`;
  - região `0x50..EOF`: `0xf96962fc`.
- O valor little-endian em `0x0c` é `0xe5476cdf`, não coincide com os CRC-32 calculados. Não há base para declarar qual algoritmo, escopo ou finalidade esse campo possui.
- O CRC da entrada JLFS confere segundo o contexto fornecido; isso valida o contêiner externo, não o formato RU30.

### Confiança

**Alta** para observações byte a byte, hash e CRCs calculados; **baixa** para classificação semântica além da associação contextual com `ui_upgrade`.

### Fontes

- [Formato JLFS](https://kagaimiq.github.io/jielie/datafmt/jlfs.html).
- [Formato/áreas de firmware](https://kagaimiq.github.io/jielie/datafmt/newfw.html).
- [Pesquisa Jieli BLE Badge](https://github.com/ElectronicCats/jieli-ble-badge-research).

As fontes públicas listadas documentam JLFS e áreas de firmware, mas não fornecem um schema RU30 aplicável a este arquivo.

---

## 4. `00242abb_upgrade.str`

**Caminho:** `work/decoded/jlfs/00242abb_upgrade.str`  
**ID:** `00242abb_upgrade.str`

### Classificação e função provável

- **Demonstrado:** recurso binário de 2.644 bytes com magic ASCII `RU30` no offset 0.
- **Função provável:** recurso de UI JieLi; a finalidade específica do recurso `str` não foi determinada.
- **Hipótese não confirmada:** schema RU30, semântica dos campos e compatibilidade com JL701N, BR35/AC707N ou RU2.

### Evidências e CRC

- Bytes `0x04–0x07`: `00 03 01 00`.
- Offset `0x10`: `1c 00 00 00`, inteiro little-endian 28.
- Strings: `RU30` no offset 0 e fragmentos não interpretáveis em offsets como `0x3f0` e `0xa08`; não há texto funcional legível.
- SHA-256: `5901f377343872e28dfb1619e57208875fe6f002f6673b765956a08c8f22cbf1`.
- CRC-32 IEEE do arquivo inteiro: `0x8d0f5b13`. Esse cálculo não foi identificado como CRC da entrada JLFS nem como checksum RU30.
- O parser analisado para `RU2` exige `RU2\x19` e nomeia seu tipo `jieli-ru2`; isso não prova interpretação nem compatibilidade com `RU30`.

### Confiança

**Alta** para observações binárias e hash; **moderada** para a classificação genérica como recurso de UI; **baixa/inconclusiva** para função, schema e compatibilidade.

### Fontes

- [Repositório `jl-misctools`](https://github.com/kagaimiq/jl-misctools).
- [Parser RU2 `ru2unpack.py`](https://github.com/kagaimiq/jl-misctools/blob/main/ui_resource/menu.res/ru2unpack.py).

---

## 5. `00242adb_upgrade.sty`

**Caminho:** `work/decoded/jlfs/00242adb_upgrade.sty`  
**ID:** `upgrade_sty`

### Classificação e função provável

- **Demonstrado:** arquivo binário de 522 bytes, sem magic ASCII identificado no início, localizado no contexto do recurso `ui_upgrade`.
- **Função provável:** recurso/descritor de UI associado ao ecossistema JLUI/JieLi, possivelmente relacionado ao estilo ou descrição de `upgrade`.
- **Hipótese não confirmada:** formato interno, semântica dos campos, referências/pointers e compatibilidade com hardware específico.

### Evidências e CRC

- Bytes iniciais: `01 f8 00 20 88 5c a4 62`.
- Strings ASCII observáveis: `none` nos offsets `0x94` e `0xc8`, e `strpic` em `0x9c`.
- A maioria dos bytes é binária, com padrões compatíveis com campos/pointers little-endian, sem decodificação confirmada.
- CRC-32/IEEE do arquivo inteiro: `0xcc7793fd`.
- CRC-16/XMODEM: `0xc902`.
- Os dois valores são fingerprints calculados, não checksums validados para o formato.
- O CRC da entrada JLFS é válido segundo o contexto fornecido.

### Confiança

**Média** para a associação geral a UI/JLUI; **baixa** para formato, semântica e compatibilidade.

### Fontes

- [Repositório `jl-misctools`](https://github.com/kagaimiq/jl-misctools).
- [Patch de menu do projeto Jieli BLE Badge](https://github.com/ElectronicCats/jieli-ble-badge-research/blob/main/patches/badge/badge-menu.patch).

A documentação/ferramentas citadas não fornecem parser ou especificação confirmada de `.sty` para este alvo.

---

## 6. `0024b3f1_p11_code.bin`

**Caminho:** `work/decoded/jlfs/0024b3f1_p11_code.bin`  
**ID:** `p11_code`

### Classificação e função provável

- **Demonstrado:** binário de 15.112 bytes (`0x3b08`), sem magic ASCII evidente, com registros aparentes e dados binários densos.
- **Função provável:** payload de código/recurso P11 fornecido como entrada a um empacotador JieLi.
- **Hipótese não confirmada:** estrutura interna, finalidade precisa, checksums internos e origem/compatibilidade. A receita pública citada pertence a BR35/AC707N e não prova a origem deste exemplar.

### Evidências e CRC

- SHA-256: `6837261c75cf3e8c0b59fc2d4469d568d21ce6f37c67001a8dfbcc32d475da1f`.
- Prefixo: `07 00 80 3a 80 00 00 00 70 00 00 00 f1 2e 29 63 00 00 04 00 55 aa 55 aa f0 3a 00 00 cf 99 63 a4`.
- Região `0x10–0x6f`: seis registros aparentes de 16 bytes, com índices 0–5 e padrão `55 aa 55 aa`.
- Dados binários densos começam em `0x70`.
- Strings observáveis: `sc7a20h` em `0x204` e `0x261`; `demo` em `0x2a0`; `sensor` em `0x2a5`.
- O CRC da entrada JLFS confere segundo o contexto fornecido; nenhum CRC interno foi atribuído.

### Confiança

**Média** quanto ao papel de componente/entrada P11; **baixa** quanto à interpretação da estrutura interna.

### Fontes

- [Receita SDK Jieli BR35/AC707N](https://github.com/ElectronicCats/jieli-ble-badge-research/blob/main/docs/jieli-sdk-build.md).
- [Formato de firmware Jieli](https://kagaimiq.github.io/jielie/datafmt/newfw.html).

A receita BR35/AC707N é evidência comparativa de nomenclatura/pipeline, não prova de compatibilidade JL701N.

---

## 7. `0024ef19_config.dat`

**Caminho:** `work/decoded/jlfs/0024ef19_config.dat`  
**ID:** `0024ef19_config.dat`

### Classificação e função provável

- **Demonstrado:** estrutura de configuração JCRT de 384 bytes, com sete itens nomeados e CRCs estruturais que conferem.
- **Função provável:** configuração com campos nomeados para versão/identificador, sinais de IO, chave de enlace e alimentação.
- **Hipótese/limite:** os significados exatos dos códigos, a semântica operacional de cada IO e o dispositivo de destino não podem ser estabelecidos apenas pelo arquivo.
- O nome do campo `serial_num` sugere função de identificador; seu valor foi redigido para publicação e **não** é usado para afirmar alvo ou compatibilidade. Não foi inferida associação com BR35/AC707N ou RU2.

### Evidências e CRC

- Cabeçalho `JCRT`.
- Self-CRC `0x15C3`: confere.
- CRC dos sete descritores `0x6491`: confere sobre o intervalo `[0x20,0x100)`.
- Os sete CRCs de payload conferem.
- Entradas identificadas:

| Item | Tipo | Offset | Tamanho/conteúdo observado |
|---|---:|---:|---|
| `ver_info` | 1 | `0x100` | 6 bytes: `000200820000` |
| `ver_info_ext` | 2 | `0x110` | 22 bytes: 16 bytes opacos redigidos, sufixo ASCII `,jl_v8` |
| `serial_num` | 2 | `0x130` | 16 bytes: identificador mascarado |
| `reset_io` | 2 | `0x140` | 1 byte: ASCII `1` |
| `pilot_lamp_io` | 2 | `0x150` | 4 bytes: `PB03` |
| `link_key` | 1 | `0x160` | 16 bytes de material de chave; valor deliberadamente não publicado |
| `power_io` | 2 | `0x170` | 6 bytes: `PC03_1` |

- Os offsets/tamanhos separam o campo de 16 bytes `serial_num` do byte adjacente `reset_io`. Valores completos de identificador, token opaco e chave são omitidos da cópia destinada à publicação.

### CRC dos descritores e patcher local

O intervalo correto cobre `item_count=7` descritores de 32 bytes: `[0x20,0x100)`, CRC armazenado/calculado `0x6491`. O patcher local antigo usava o fim hardcoded `0xE0`, omitindo um descritor e produzindo `0xB54F`; a cópia de trabalho foi corrigida para derivar o limite da contagem. O teste foi exclusivamente `--dry-run`; o arquivo local permaneceu inalterado e nenhum firmware foi modificado. Sua fingerprint foi omitida da publicação porque inclui um campo `link_key`.

### Confiança

**Alta** para bytes, estrutura identificada e CRCs; **moderada** para atribuição Jieli/JCRT; **baixa a moderada** para semântica detalhada e dispositivo de destino.

### Fontes

- [`mkjlfs.py`](https://github.com/kagaimiq/jl-misctools/blob/main/firmware/mkjlfs.py).
- [Repositório `jl-misctools`](https://github.com/kagaimiq/jl-misctools).
- [Ferramentas `jl-uboot-tool`](https://github.com/kagaimiq/jl-uboot-tool).

As fontes apoiam a estrutura JCRT/JLFS e o tratamento de CRC, mas não definem a semântica completa dos códigos JCRT nem o alvo do dispositivo.

---

## 8. `0024f0b9_eq_cfg_hw.bin`

**Caminho:** `work/decoded/jlfs/0024f0b9_eq_cfg_hw.bin`  
**ID:** `eq_cfg_hw`

### Classificação e função provável

- **Demonstrado:** blob binário de 4.081 bytes, sem magic textual ou rótulos legíveis, com campos numéricos aparentes.
- **Função provável:** configuração de EQ/efeitos de áudio; a referência pública descreve `eq_cfg_hw.bin` como contendo cópia de perfis de efeitos de microfone, roteamento e EQ em um SDK de outra família.
- **Hipótese não confirmada:** que este exemplar tenha exatamente esse layout/função, ou que seja compatível com JL701N.

### Evidências e CRC

- SHA-256: `645acbb8426c148dbd859eb8689d2b31058f9d4798d97e82d5c1581cb902f51c`.
- Início: `02 01 00 00 00 fd ff 36 00 03 04 00 1c 00 7c 00`.
- CRC-32 padrão do payload: `0xfd0baaba`.
- Adler-32: `0xa8c9dc79`.
- O CRC JLFS do contêiner é válido segundo o contexto; os valores acima não foram identificados como checksums internos esperados.

### Confiança

**Média** para a função ampla; **baixa** para formato, origem e compatibilidade de plataforma.

### Fonte

- [SDK BR23 — `download.c`](https://gitlab.zh-jieli.com/soundbox/novisualization/ac695n_soundbox_sdk/-/raw/bd84e3897269f96b334123ba0ea31aa2cdd2f17f/cpu/br23/tools/download.c).

A fonte é de BR23/AC695N e é apenas evidência nominal/comparativa; não prova a origem deste payload.

---

## 9. `00002040_cfg_tool.bin`

**Caminho:** `work/decoded/jlfs/00002040_cfg_tool.bin`  
**ID:** `00002040_cfg_tool`

### Classificação e função provável

- **Demonstrado:** recurso binário de configuração/runtime de 935 bytes, com slots regulares rotulados `AC701N_watch` e `AC701N_2` até `AC701N_20`.
- **Função provável:** tabela de slots/perfis consumida por algum runtime ou ferramenta de configuração JieLi.
- **Hipótese não confirmada:** layout dos campos, origem exata no SDK e compatibilidade com JL701N. Os rótulos `AC701N_*` não são prova suficiente de chip ou compatibilidade.

### Evidências e CRC

- O CRC JLFS da entrada/contêiner é informado como válido.
- Início hexadecimal: `a3 03 00 00 00 1a 42 00 00 00 00 00 00 1b 42 00 00 00 00 00 8f 5e c2 03`.
- Palavras little-endian iniciais observadas: `0x000003a3`, `0x00421a00`, `0`, `0x00421b00`; não há especificação para atribuir semântica com segurança.
- Strings em slots regulares: `AC701N_watch`, `AC701N_2`–`AC701N_20`, seguidas por áreas NUL; o restante é principalmente binário, com áreas preenchidas por `00` e `ff`.
- Não foi identificado CRC interno conclusivo.

### Confiança

**Média** para a categoria geral de recurso de configuração JieLi; **baixa** para layout/campos e origem específica.

### Fontes

- [Documentação de build AC707N/br35](https://github.com/ElectronicCats/jieli-ble-badge-research/blob/main/docs/jieli-sdk-build.md).
- Cópia local consultada: `work/jieli-research/docs/jieli-sdk-build.md`.

A documentação aberta registra `cfg_tool.bin` no pipeline de um SDK AC707N/br35, mas não comprova que este artefato foi produzido por esse SDK.

---

## 10. `002114bb_index.idx`

**Caminho:** `work/decoded/jlfs/002114bb_index.idx`  
**ID:** `tone_index`

### Classificação e função provável

- **Demonstrado:** índice de diretório de tons no formato `TIDX`/`tone.idx`, com 12 registros CRC-validados.
- **Função provável:** associar nomes de tons a IDs numéricos sequenciais; **não é um payload de áudio**.
- O diretório pai `tone` contém `index.idx`, dois arquivos `.wtg` opacos e dez MP3 que correspondem aos nomes indexados; todos os CRCs de headers/dados dos filhos conferem e `file` reconheceu 10/10 MP3s. Isso não prova quando ou como o firmware os reproduz. Detalhes em [tone_index.md](component-findings/tone_index.md).

### Evidências e CRC

- Magic ASCII: `TIDX`.
- Cabeçalho com CRC-16 `0x9125`, compatível com polinômio CCITT `0x1021`, inicialização 0, calculado sobre seis bytes de preenchimento `FF` e a contagem little-endian de 12.
- 12 registros contíguos de comprimento variável, do offset `0x10` até EOF `0xae`.
- O CRC little-endian armazenado de cada registro coincide com o CRC do corpo do respectivo registro.
- Nomes indexados, pelos IDs 1–12: `drain`, `sos`, `msg0.mp3`, `msg1.mp3`, `msg2.mp3`, `msg3.mp3`, `call0.mp3`, `call1.mp3`, `call2.mp3`, `call3.mp3`, `asrhello.mp3`, `asrbye.mp3`.
- Tamanho total: 174 bytes.

### Confiança

**Alta** para a estrutura TIDX e a classificação do índice; nenhuma conclusão específica de chip foi feita.

### Fontes

- [Formato de firmware Jieli](https://kagaimiq.github.io/jielie/datafmt/newfw.html).
- [Gerador local/público `tonecfgmk.py`](https://github.com/kagaimiq/jl-misctools/blob/main/firmware/tonecfgmk.py).

---

## Limitações gerais

1. A validação do CRC JLFS, quando indicada, confirma a entrada no contêiner, mas não substitui um parser do formato interno de cada payload.
2. Não foi obtida especificação pública aplicável a RU30, `.sty`, P11, `cfg_tool.bin`, EQ ou à estrutura completa da aplicação `app.bin` para este alvo.
3. Comparações com BR35/AC707N, BR52, BR23/AC695N e RU2 foram mantidas como referências de contexto; não demonstram compatibilidade com JL701N ou com o Microwear S11 Pro.
4. Entropia, strings, magics e CRCs genéricos não bastam, isoladamente, para identificar arquitetura, codec, offsets, consumidor ou alvo de hardware.
5. Não foram executados empacotadores, descompactadores, gravadores, nem testes em firmware/hardware. O firmware e o hardware permaneceram inalterados.
6. O CRC32 zlib calculado para `uboot.boot` não pode ser usado como teste de integridade sem o valor esperado e a convenção de checksum do firmware.

## Testes pendentes recomendados

- Obter o **JLFS original completo**, incluindo cabeçalhos/entradas e todos os campos de comprimento, flags e CRC, para correlacionar cada payload com seus metadados externos.
- Identificar ou reconstruir, a partir do mesmo alvo e versão, o parser/decoder de `descramble_bankcb` e do codec indicado pela flag `0x40` de `uboot.boot`; então validar o resultado por assinatura, tamanho e CRC esperados.
- Localizar uma especificação ou consumidor correspondente para RU30, `.sty`, P11, EQ, `cfg_tool.bin` e `app.bin`; comparar com amostras de proveniência comprovadamente igual, sem importar layouts de outras famílias.
- Recuperar a convenção de checksum de `upgrade.res` e testar especificamente o campo em `0x0c` (`0xe5476cdf`) contra algoritmos, endianness e escopos documentados pelo firmware, sem assumir CRC-32 padrão.
- Confirmar a estrutura JCRT contra código consumidor ou documentação do fornecedor, incluindo a semântica dos códigos IO, `link_key` e versões; manter o intervalo `[0x20,0x100)` como o intervalo que reproduz o CRC `0x6491` até nova evidência.
- Correlacionar o TIDX com os arquivos de áudio vizinhos e verificar se cada ID/nome é resolvido corretamente pelo firmware.
- Só após obter parser, checksums e alvo confirmados, considerar testes de descompressão, repacotamento ou gravação; esses testes não foram realizados neste levantamento.
