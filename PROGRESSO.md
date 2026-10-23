# Microwear S11 Pro — progresso da engenharia reversa

**Atualizado em 2026-10-22.** A análise foi estática e feita em cópias de trabalho. Nenhum firmware foi alterado, instalado ou transmitido ao relógio.

## Modelo e versão declarados

O modelo comercial **Microwear S11 Pro** é o informado pelo usuário; a evidência binária identifica componentes/plataforma JieLi (`JL701N`), mas não prova por si só a marca ou revisão física do relógio. O arquivo aninhado `ui_upgrade/upgrade.json` declara literalmente `version_id: "W002"` (53 bytes; CRC-16 do header/dados `0x3FB1`/`0x792D`, ambos conferindo). Portanto, a forma segura de catalogar a versão indicada pelo pacote é **W002**, sem inventar uma versão semântica ou data de release. O campo separado `config.dat`/JCRT `ver_info` termina em `VER=0x0000` segundo a interpretação local; não há base para tratá-lo como substituto do `version_id`. O nome numérico do UFW também não foi convertido em timestamp. Veja [upgrade_json.md](docs/component-findings/upgrade_json.md).

## Integridade do firmware e CRCs

O original UFW está preservado em `original/`, somente leitura. Tem 2.557.568 bytes e SHA-256 `0ad4460ba411122f934a292a5ea78294158a4e21af9dabbe72f920324f623b43`. O companion `175905457427793.bin` tem SHA-256 `65d5464dca61d051ded8092faa83318f1761dbc6016a711f037a97bc10aaafd3`.

Uma implementação independente recalculou o CRC do cabeçalho UFW (`0x5394`), da lista (`0xD0B9`) e do `flash.bin` raw (`0xD655`); os três conferem. A divergência antiga do cabeçalho flash JLFS foi um erro de ordem: `0xF520` confere quando calculado sobre o cabeçalho totalmente decifrado antes de restaurar VID/PID para exibição. O `0x400C` anterior veio da cópia de apresentação, não da entrada correta do CRC.

O `data_crc` JLFS de `uboot.boot` (`0xDC88`) também confere depois do bankcb descramble. O payload raw ainda bankcb-scrambled calcula `0xAFF9`; essa diferença não indica corrupção. Os CRCs do cabeçalho e corpo bankcb conferem. A especificação pública associa a flag `0x40` a compressão LZ4 de `uboot.boot`, mas **não foi executada descompressão LZ4**. Cinco entradas externas UFW têm CRC armazenado diferente do CRC-16 calculado sobre bytes raw; escopo/transformação permanecem sem documentação, então não foram declaradas corrompidas. Métodos, intervalos e valores constam em [integrity-audit.md](docs/integrity-audit.md) e [integrity-audit.json](docs/integrity-audit.json). O inventário dos nove itens está em [outer-components.md](docs/outer-components.md) e [ufw-inventory.json](docs/ufw-inventory.json).

## Componentes e recursos

O contêiner contém nove entradas UFW; `flash.bin` foi analisado como JLFS em uma cópia de trabalho. O inventário JLFS registra 17 entradas/âncoras, incluindo `app.bin` (2.158.452 bytes), `cfg_tool.bin`, `tone`/TIDX e seus recursos de áudio, `ui_upgrade` com `upgrade.json`, `upgrade.res`, `upgrade.str`, `upgrade.sty`, além de `p11_code.bin`, `config.dat`/JCRT e `eq_cfg_hw.bin`. `cfg_tool.bin` tem 20 rótulos regulares (`AC701N_watch` e `AC701N_2` a `_20`), não 21. O [mapa de partições](docs/partition-map.md), o [inventário JLFS sanitizado](docs/jlfs-inventory.json) e os [achados por artefato](docs/componentes-detalhados.md) descrevem evidências e limites.

Há dois itens chamados `isd_config.ini`. O externo UFW tem 1.273 bytes e continua opaco. O interno JLFS tem 127 bytes, em `flash+0x164f`, e começa com um prefixo opaco de material de chave; sua fingerprint foi omitida. O JSON de parâmetros identifica explicitamente a origem em [isd_config_parameters.json](docs/isd_config_parameters.json). Os registros interpretados contêm `UTTX=PB08`, `UTBD=1000000`, `EX_FLASH=PC03_1A_PC08` e interface `EX_FLASH_IO` de quatro linhas. Isso descreve a configuração gravada, mas não confirma fabricante/capacidade da flash, revisão da placa ou pinagem física.

## Hardware, display e touchscreen

O contêiner e o cabeçalho decodificado identificam `JL701N`; a direção de toolchain `pi32v2-r3` é consistente com fontes JieLi públicas para a família 700N/701N. `BR28` e essa arquitetura também foram indicados pelo solicitante. Não há foto da PCB, marcação de IC ou dump de memória física que confirme painel, touchscreen, RAM, fabricante/capacidade de flash ou revisão da placa.

`app.bin` contém strings `lcd_init`, `sh8601`, `gc9b71` e `bcs_touch`, mas o Ghidra não resolveu referências cruzadas para esses nomes na análise atual. São pistas de suporte/nomeação no blob, não identificação de componente montado. Os resultados e ressalvas estão em [hardware-findings.md](docs/hardware-findings.md).

## Ghidra, SDK e compilação

A toolchain JieLi `20260730.1` para `pi32v2`, Ghidra 12.2, JDK 25 e plugin comunitário pi32v2 foram usados localmente. O compilador emitiu um objeto ELF32 relocatable de `main.c` (`-target pi32v2 -mcpu=r3`). Esse é somente um teste de compilação de objeto; não houve linkagem, imagem inicializável, teste funcional ou execução no relógio. O scaffold em `firmware/` não tem startup, linker script, memória configurada, drivers ou bootloader e **não é flashável**.

O binário `app.bin` foi importado como raw binary com base `0x0`, escolhida pelo operador e não fornecida pelo JLFS. O offset 0 decodifica uma sequência plausível de startup e é o melhor candidato entre os offsets testados; ainda não se provou que seja o endereço para onde o boot salta. Os valores 1.186 funções e 40.795 objetos de instrução descrevem o listing atual, não contagens reais do firmware. O log contém 51 eventos de conflito em 26 endereços e 37 erros P-code; o plugin não cobre todas as instruções e o bloco raw inteiro foi marcado R/W/X pelo importador. O projeto Ghidra local está em `work/ghidra-projects/S11Pro-analysis.gpr`/`.rep`; a cópia ZIP local também existe, mas ambos são excluídos da publicação por padrão, pois contêm firmware e dados derivados. Mais detalhes em [hardware-findings.md](docs/hardware-findings.md).

## Arquivo companion recebido

`175905457427793.bin` começa com `BCSDIAL20250928164504`. O processo feito foi carving por assinaturas, não um parser semântico do formato: foram encontradas 50 imagens JPEG válidas por Pillow, todas 320×384. Isso não estabelece resolução nativa do display nem animação. Veja [bcsdial-analysis.md](docs/bcsdial-analysis.md). As imagens extraídas, o ZIP e a prévia GIF existem apenas como artefatos locais ignorados por padrão; não os publique sem verificar os direitos de redistribuição.

## Segurança e recuperação

Não houve tentativa de atualização, flash, OTA, escrita de partição ou recuperação. Ainda não há método de restauração provado para este exemplar: faltam dump completo e byte-exato da memória do relógio, pinout confirmado e procedimento oficial/compatível de bootloader/ISP que restaure o original. **Não instale nem transmita o scaffold.**

As ferramentas de extração receberam salvaguardas contra CRCs essenciais inválidos, path traversal e sobrescrita em algumas rotas. O parser JLFS continua amarrado a este workspace e a um checkout de referência local; consulte [tool-audit.md](docs/tool-audit.md) antes de publicar ou executar em firmware de terceiros.

## Próximas dependências técnicas

1. Dump de flash somente de leitura do próprio relógio e fotos macro da PCB, revisão e marcações dos chips.
2. Procedimento de recuperação/bootloader/ISP específico e restaurável, confirmado antes de qualquer escrita.
3. SDK/BSP, linker script e drivers da PCB S11 Pro, especialmente para o painel e touchscreen realmente montados.
4. Decodificador RU30/`.sty` compatível e documentação do contêiner BCSDIAL.
5. Endereço de carga, entry point e mapa de memória de `app.bin` confirmados pelo bootloader/ROM ou linker map.

**Resultado prático:** há evidências documentadas, ferramentas executáveis neste workspace e um objeto pi32v2 compilado. Os extratores ainda não formam um pacote independente para clone limpo. Ainda não existe sistema alternativo inicializável, hardware plenamente identificado ou método seguro para instalá-lo.
