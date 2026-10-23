# Evidências de hardware e análise estática — Microwear S11 Pro

O nome comercial Microwear S11 Pro foi fornecido pelo usuário. O firmware analisado fornece evidência para a plataforma JieLi/JL701N, não uma confirmação independente da marca ou revisão física.

## Identificação do SoC e arquitetura

O cabeçalho de flash JLFS decodificado contém `product_id: JL701N`. O formato UFW externo também identifica `JL701N`. O projeto e linguagem de Ghidra usados foram `pi32v2:LE:32:default`; o SDK público JieLi lista `pi32v2-r3` para a família 700N/701N. A atribuição `BR28` e a provável arquitetura pi32v2 também foram informadas pelo solicitante. Isso sustenta a direção de toolchain, mas não identifica por si só a revisão da PCB ou o BSP usado pela Microwear.

## Flash e memória

O arquivo JLFS interno `work/decoded/jlfs/00000040_isd_config.ini` (127 bytes) possui registros interpretados conforme a documentação oficial JieLi. Seu fingerprint foi omitido porque o arquivo começa por um blob opaco identificado como material de chave no parser. O JSON de parâmetros refere-se a esse arquivo. Existe também uma entrada UFW externa de mesmo nome, distinta, com 1.273 bytes; não foi decodificada como INI e seu CRC raw permanece inconclusivo. Fingerprints das duas configurações são omitidos nesta cópia pública.

| Chave | Valor observado | Leitura limitada |
|---|---|---|
| `SPI` | `4_3_0_0` | parâmetros SPI compactados; a documentação define o formato como `datawidth_clk_mode_port` |
| `UTTX` | `PB08` | saída TX serial configurada |
| `UTBD` | uint32 little-endian `1.000.000` | baud rate configurado |
| `EX_FLASH` | `PC03_1A_PC08` | campo JieLi de CS/interface/alimentação da flash externa |
| `EX_FLASH_IO` | `4_PC01_PC02_PC04_PC05_PC00` | formato `width_CLK_DO_DI_D2_D3`; configuração de largura 4 linhas e sinais listados |

A documentação JieLi afirma que o método `EX_FLASH`/`EX_FLASH_IO` é usado em JL701N e descreve a configuração como flash externa. O mapa JLFS também lista áreas lógicas `VM`, `PRCT`, `BTIF`, `FATFSI`, `BCSUI` e `EXIF`. Isso é evidência de configuração/particionamento, não prova do fabricante, part number ou capacidade dos chips instalados.

Há um `flash_size_field` interno calculado como 16.773.120 bytes (`0xFFF000`) no cabeçalho decodificado. A semântica e a relação com memória física não foram validadas. Não concluir “flash de 16 MB” a partir desse campo, nem a partir do tamanho de 2.428.928 bytes do payload UFW `flash.bin`.

`UTTX=PB08` e baud 1 Mbit/s não constituem um método de recuperação: TX é apenas uma configuração de saída serial e não documenta RX, boot strap, ISP ou restauração. Nenhum pino desconhecido foi acionado.

## Display e touchscreen

No `app.bin` extraído, foram encontradas as strings:

- `lcd_init` em offset `0xCCE7A`;
- `sh8601` em `0xCD618` e `gc9b71` logo em seguida, em `0xCD61F`;
- `bcs_touch` em `0x168BF6`.

O texto `WATCH S11` também aparece no `app.bin`. Apesar desses nomes, uma consulta de referências cruzadas do Ghidra no endereço-base provisório 0 não encontrou referências para `sh8601`, `gc9b71` ou `bcs_touch`. A presença dessas strings só confirma que estão no blob; pode significar suporte compilado, tabela de nomes ou recurso de identificação. Não prova qual caminho de inicialização é escolhido nem qual IC está fisicamente instalado.

As páginas/datasheets externos consultados descrevem o SH8601A como driver para AMOLED LTPS 480×480 (um modelo/variante da família SH8601) e o GC9B71 como driver a-TFT LCD de 360×360, com outras configurações listadas, inclusive 320×360 e 320×390. Esses materiais não foram incorporados ao pacote local e descrevem componentes candidatos, não o hardware do relógio. As dimensões não correspondem diretamente ao material gráfico adicional extraído (320×384); esse tamanho é apenas dos arquivos de imagem e não estabelece a resolução nativa do painel. `bcs_touch` não identifica fabricante/part number de touchscreen. A diagonal, resolução e tipo físico do display continuam sem confirmação.

## Análise Ghidra reproduzível

Instalados Ghidra 12.2, Temurin JDK 25 e processador comunitário JieLi/pi32v2. O Ghidra importou `app.bin` como raw binary com imagem-base `0x0`, escolhida pelo operador; o arquivo JLFS não fornece ali um endereço de execução. Um probe independente decodificou uma sequência plausível de inicialização no offset 0 (`mov sp`, `mov ssp`, `push`, chamadas e rotina de cópia/limpeza). Entre os offsets testados, 0 é o melhor candidato a início de código, mas não há prova de que o Boot ROM salte para ele. A ferramenta criou uma função manualmente rotulada como entrada provisória; o ponto de entrada não foi demonstrado pelo firmware.

A autoanálise registra 1.186 funções e 40.795 objetos de instrução no listing atual. Esses são contadores da análise, não números reais de funções/opcodes do firmware; a função de entrada foi criada manualmente. O relatório de auditoria contou 51 eventos de conflito em 26 endereços e 37 mensagens de erro P-code. O plugin pi32v2 cobre a maioria, mas não todas, as instruções. A importação raw marcou o bloco inteiro como R/W/X, o que não prova que todo o payload seja código executável. Os nomes de drivers não têm xrefs resolvidos no projeto atual; zero xrefs não prova que não sejam usados.

Projeto: `work/ghidra-projects/S11Pro-analysis.gpr` e diretório `.rep`; uma cópia ZIP existe localmente, mas está excluída da publicação por padrão porque contém firmware/dados derivados. Scripts de apoio: `work/ghidra-scripts/ProbeStart.java`, `MarkEntry.java`, `AnalysisSummary.java` e `DriverRefs.java`. Os offsets absolutos, endereço de carga, referência da entry point e mapa de memória ainda precisam de confirmação pelo bootloader/ROM, mapa de linker ou leitura controlada do dispositivo.

## Conclusão operacional

Evidências fortes: pacote aponta para JL701N; a configuração do firmware descreve flash externa por interface de quatro linhas; o binário contém nomes de drivers SH8601, GC9B71 e BCS touch. Desconhecidos que exigem inspeção física ou BSP específico: IC ativo de display/touch, resolução e diagonal do painel, part number e capacidade das memórias, revisão da placa e pinagem completa. Até esses itens e a recuperação não serem comprovados, o scaffold não deve ser instalado.

## Referências

- [JieLi — configuração `isd_config.ini`](https://doc.zh-jieli.com/Tools/zh-cn/dev_tools/toolchains/ini_cfg.html)
- [JieLi — configuração de flash externa para JL701N e família](https://doc.zh-jieli.com/Tools/zh-cn/mass_prod_tools/burner_1tuo8/extern_flash_burn.html)
- [JieLi — compatibilidade de toolchain pi32v2-r3](https://doc.zh-jieli.com/Tools/zh-cn/dev_tools/toolchains/linux_lib.html)
- [PDF preliminar SH8601A](https://admin.osptek.com/uploads/SH_8601_A0_Data_Sheet_Preliminary_UCS_V0_0_191226_1_143481d321.pdf)
- [PDF GC9B71, versão 1.1](https://admin.osptek.com/uploads/GC_9_B71_Data_Sheet_V1_1_622df4ec27.pdf)
