# Auditoria de integridade — UFW/JLFS do Microwear S11 Pro

**Estado:** auditoria estática, sem escrita no relógio. O arquivo original continua preservado em `original/176103986767848.ufw`, modo somente leitura, tamanho 2.557.568 bytes, SHA-256 `0ad4460ba411122f934a292a5ea78294158a4e21af9dabbe72f920324f623b43`.

## Resultado principal

As duas divergências mais preocupantes do relatório inicial foram causadas por comparar representações diferentes:

- O CRC do cabeçalho flash **confere** (`0xF520`) se calculado sobre os 30 bytes totalmente decifrados após o campo CRC e **antes** de restaurar VID/PID visíveis para exibição. O valor anterior `0x400C` foi calculado depois de restaurar esses campos e, portanto, não era o intervalo de entrada do CRC usado pelo parser JieLi.
- O CRC de dados de `uboot.boot` (`0xDC88`) não confere sobre o payload bankcb-cifrado salvo diretamente (`0xAFF9` calculado). Depois de aplicar a transformação `descramble_bankcb` do parser público, o CRC do payload confere; também conferem o CRC do cabeçalho do bankcb e o CRC do corpo do banco. **Não foi feita descompressão.**

O auditor independente está em [audit_integrity.py](../tools/audit_integrity.py), e os resultados completos estão em [integrity-audit.json](integrity-audit.json). O script reimplementa CRC-16 e a sequência ENC em Python puro; não depende de `crcmod` nem dos helpers do extrator. Ele não modifica a entrada.

## Algoritmo e domínios testados

Para os campos UFW/JLFS e bankcb abaixo foi usado CRC-16 com largura 16, polinômio `0x1021`, valor inicial `0x0000`, `refin=false`, `refout=false`, `xorout=0x0000` (variante não refletida estilo XMODEM). Os campos de 16 bits são armazenados little-endian. A função pública JieLi `jl_crc16` tem esses parâmetros; o auditor independente implementa a mesma fórmula em `audit_integrity.py`.

| Campo | Intervalo calculado (fim exclusivo) | Bytes usados | Armazenado | Calculado | Resultado |
|---|---|---|---:|---:|---|
| UFW `hdrcrc` | cabeçalho descrifrado `[0x02,0x40)` | 62 bytes, excluindo o campo CRC | `0x5394` | `0x5394` | confere |
| UFW `listcrc` | `[0x40,0x310)` | nove registros de entrada no estado raw/ENC-scrambled | `0xD0B9` | `0xD0B9` | confere |
| UFW `flash.bin` `data_crc` | `[0x400,0x251400)` | 2.428.928 bytes raw do payload flash | `0xD655` | `0xD655` | confere |
| JLFS flash header | `[flash+0x02,flash+0x20)` | 30 bytes totalmente decifrados com ENC `0xFFFF`; sem restaurar VID/PID | `0xF520` | `0xF520` | confere |
| JLFS `uboot.boot` `data_crc` | `[flash+0xA0,flash+0x164F)` | payload de 5.551 bytes após `descramble_bankcb` | `0xDC88` | `0xDC88` | confere |
| bankcb cabeçalho | `uboot.boot+[0x00,0x0E)` | 14 bytes do cabeçalho descrambled | `0xF4C0` | `0xF4C0` | confere |
| bankcb conteúdo | `uboot.boot+[0x10,0x15AF)` | 5.535 bytes do banco descrambled | `0x97E7` | `0x97E7` | confere |

O algoritmo ENC é um XOR-stream JieLi, chave inicial `0xFFFF`, estado reiniciado em cada chamada. A validação do cabeçalho flash segue a ordem do parser `fwunpack_newfw.py`: decifrar 32 bytes; testar CRC em `[2:32)`; somente depois restaurar os campos VID/PID visíveis para montar a visão interpretada. A cópia para exibição não é a entrada do CRC.

No JLFS, os quatro cabeçalhos superiores foram recalculados após decifragem e conferem: `uboot.boot` `0x807F`, `isd_config.ini` `0x003F`, `app_dir_head` `0xF801`, `key_mac` `0x28C9`. Os valores `0xFFFF` em entradas de região reservada/partição são placeholders, não falhas de CRC. O manifesto JLFS registra os demais cabeçalhos e payloads extraídos com o CRC calculado sobre os bytes escritos em cada arquivo.

## Campos de dados UFW não resolvidos

O cálculo de CRC-16 sobre bytes raw do payload confere em `flash.bin`, `info.log` (vazio), `ota.bin` e `tail.bin`. Há cinco campos cujo CRC declarado não coincide com os bytes raw armazenados sob a fórmula acima:

| Entrada externa | Campo armazenado | CRC sobre bytes raw | Situação |
|---|---:|---:|---|
| `uboot.version` | `0x4EC3` | `0x2BE2` | escopo/transformação não documentados |
| `isd_config.ini` externo (1.273 B) | `0xAB74` | `0x80F1` | escopo/transformação não documentados |
| `v_ota.bin` | `0x6285` | `0x6056` | escopo/transformação não documentados |
| `farg.cfg` | `0x8312` | `0xF103` | escopo/transformação não documentados |
| `blimit.bin` | `0x5A48` | `0x5011` | escopo/transformação não documentados |

Esses cinco resultados são divergências aritméticas no domínio **raw**; não provam corrupção. O parser público `fwunpack_newfw.py` verifica `hdrcrc`, `listcrc` e o CRC raw de `flash.bin`, mas não documenta uma validação equivalente para esses tipos de entrada. Para `blimit.bin`, a decodificação conhecida por plaintext recupera uma estrutura candidata `JLDGAUTH` e tem round-trip cifra/decifra, mas o CRC externo calculado sobre essa cópia decifrada também não coincide (`0x150C`); os CRCs internos testados permanecem sem semântica confirmada. Não foi feito brute force de CRC nem alteração de bytes.

Importante: o `isd_config.ini` externo UFW de 1.273 bytes é um componente distinto do `isd_config.ini` JLFS interno de 127 bytes. O JSON de parâmetros de placa refere-se somente ao interno de 127 bytes; consulte [isd_config_parameters.json](isd_config_parameters.json), que registra agora a proveniência.

## `uboot.boot`: transformação e limites

O payload raw preservado tem SHA-256 `b919036982cb8bd9ba7faa1159a3a13b46fb704f127316e167a37804359bf0db`. O parser público trata a primeira entrada superior como SPL, decifra o cabeçalho bankcb de 16 bytes, valida seu CRC e decifra o intervalo do banco. A saída derivada bankcb-descrambled foi gravada separadamente em `work/decoded/jlfs/00000020_uboot.boot.bankcb.bin`, SHA-256 `cdec2ee950ac6679fbbb136139faef96f08f0efd9182d81735de8f45c946f21f`; o payload raw original continua intacto.

A flag JLFS tem o bit `0x40` ligado. A [especificação pública de novo firmware JieLi](https://kagaimiq.github.io/jielie/datafmt/newfw.html) associa esse bit a conteúdo `uboot.boot` comprimido com LZ4 em famílias como BR23/BR25/BR28; o [parser público](https://github.com/kagaimiq/jl-misctools/blob/main/firmware/fwunpack_newfw.py) marca o SPL como comprimido e aplica bankcb descramble. A rotina executada aqui só faz bankcb descramble e CRC; **não** executa descompressor LZ4 e não determina se o conteúdo resultante é o bootloader completo.

## Reprodução

A partir do diretório do projeto:

```bash
python3 tools/audit_integrity.py original/176103986767848.ufw > /tmp/s11pro-integrity.json
```

O JSON versionado nesta pasta foi gerado pelo mesmo comando com `--out docs/integrity-audit.json`. O parâmetro `--out` recusa sobrescrever um arquivo existente. O parser de referência `work/jl-misctools/firmware/fwunpack_newfw.py` requer o módulo Python `crcmod` nesta imagem; por isso, os valores aqui foram reproduzidos pelo auditor puro e comparados com as rotinas-fonte públicas, não por afirmar que esse comando upstream foi executado sem dependências.

## Referências do formato

- Parser público JLFS: [kagaimiq/jl-misctools — `fwunpack_newfw.py`](https://github.com/kagaimiq/jl-misctools/blob/main/firmware/fwunpack_newfw.py), em particular a verificação do flash header, `descramble_bankcb`, CRC de cabeçalho JLFS e validação do UFW.
- Especificação de novo firmware JieLi: [jielie `newfw.html`](https://kagaimiq.github.io/jielie/datafmt/newfw.html), que documenta LZ4 quando o bit `0x40` está setado em `uboot.boot`.
- Implementação pública `jl_crc16` e parser de contêiner usados como referência local: `work/jieli-research/tools/ufw-repack/jltech/crc.py` e `work/jieli-research/tools/ufw-repack/repack_ufw.py`. O repacker declara expressamente que seu parser de layout tolera CRCs stale e não os valida; as validações deste documento são recálculos explícitos.
