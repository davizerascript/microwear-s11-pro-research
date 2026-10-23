# Entradas externas do UFW

Este inventário descreve as **nove entradas da tabela UFW externa** do arquivo `176103986767848.ufw`. Não confundir esses componentes com nomes iguais dentro do JLFS. Tamanhos, offsets, CRCs e fingerprints de entradas não sensíveis também estão em [ufw-inventory.json](ufw-inventory.json); os cálculos reproduzíveis estão em [integrity-audit.md](integrity-audit.md) e [integrity-audit.json](integrity-audit.json). Fingerprints das entradas opacas/de autenticação foram omitidos.

| Entrada | Tipo | Offset UFW | Tamanho | Evidência/estado |
|---|---:|---:|---:|---|
| `flash.bin` | 0 | `0x400` | 2.428.928 B | O CRC raw UFW `0xD655` confere. Em cópia de trabalho o conteúdo foi analisado como JLFS; ver o relatório principal e o inventário JLFS. |
| `info.log` | 2 | `0x251400` | 0 B | Entrada vazia; CRC raw `0x0000`. |
| `uboot.version` | 55 | `0x251400` | 32 B | Bytes binários sem versão legível nesta extração. CRC armazenado `0x4EC3`; CRC-16 sobre bytes raw `0x2BE2`; semântica/transformação não resolvida. É distinta da entrada JLFS `uboot.boot`. |
| `isd_config.ini` externa | 52 | `0x251420` | 1.273 B | Payload binário opaco nesta análise. CRC armazenado `0xAB74`; sobre bytes raw `0x80F1`. Não foi decodificado como arquivo INI. **Não é** o `isd_config.ini` JLFS interno de 127 bytes usado em `isd_config_parameters.json`. |
| `v_ota.bin` | 56 | `0x251920` | 64 B | Conteúdo binário; CRC armazenado `0x6285`, raw `0x6056`; formato não identificado. |
| `ota.bin` | 100 | `0x251960` | 125.966 B | CRC raw `0x0E22` confere. Há strings ASCII `edr_ota2.bin` (offsets internos `0x10`, `0x70`), `ble_ota.bin` (`0x30`, `0xB6B3`) e `lcflash_ota.bin` (`0x50`, `0x1958E`). Esses nomes foram observados em bytes; a tabela/semântica interna não foi validada. |
| `farg.cfg` | 251 | `0x270580` | 5 B | Cinco bytes binários. CRC armazenado `0x8312`, raw `0xF103`; formato não identificado. |
| `blimit.bin` | 161 | `0x2705A0` | 144 B | O CRC UFW armazenado é `0x5A48`; CRC-16 raw `0x5011` não coincide e seu escopo permanece desconhecido. Uma análise local de referência sugere um candidato com magic de autenticação `JLDGAUTH`, mas não o valida como schema nem prova o significado do payload. Como pode conter material de autenticação, o estado/cifra, hashes e valores do candidato foram deliberadamente omitidos da cópia pública. |
| `tail.bin` | 255 | `0x270640` | 64 B | Contém a string visível `JLUFW` no offset interno `0x30`; CRC raw `0x00C2` confere. O significado do trailer não foi estabelecido. |

## Como interpretar os CRCs externos

O auditor usa CRC-16 com polinômio `0x1021`, `init=0`, sem reflexão e sem XOR final, com campos little-endian, sobre o intervalo raw indicado no manifesto. Os CRCs raw conferem em `flash.bin`, `info.log`, `ota.bin` e `tail.bin`. Para `uboot.version`, `isd_config.ini` externo, `v_ota.bin`, `farg.cfg` e `blimit.bin`, a comparação raw diverge. Isso é uma observação reproduzida, **não prova de corrupção**: o escopo pode depender de uma transformação não documentada ou o campo pode ter semântica específica por tipo. O parser público de UFW consultado valida cabeçalho, lista e payload `flash.bin`, mas não fornece uma regra de validação para os outros quatro/cinco tipos.

Nenhuma dessas entradas opacas foi executada. Não foram aplicadas tentativas de decodificação por brute force para forçar correspondência de CRC. Os arquivos extraídos são cópias byte-a-byte dos intervalos UFW, exceto o artefato `blimit` decifrado, que foi escrito separadamente.
