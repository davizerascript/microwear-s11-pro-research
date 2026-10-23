# `uboot.boot` — componente JLFS

Arquivo raw extraído: `work/decoded/jlfs/00000020_uboot.boot` (5.551 bytes; SHA-256 `b919036982cb8bd9ba7faa1159a3a13b46fb704f127316e167a37804359bf0db`). O primeiro bloco de 32 bytes não tem magic legível; `file` classifica o blob apenas como `data`. Isso não impede validar a estrutura bankcb após aplicar a transformação descrita pelo parser público.

## Estrutura, CRC e transformação

A entrada JLFS é a primeira do diretório superior, tem nome `uboot.boot`, flags `0x40` e CRC de dados armazenado `0xDC88`. O parser público aplica `descramble_bankcb` ao SPL antes de usar o payload. A sequência foi reproduzida em uma cópia e gerou separadamente `work/decoded/jlfs/00000020_uboot.boot.bankcb.bin` (5.551 bytes; SHA-256 `cdec2ee950ac6679fbbb136139faef96f08f0efd9182d81735de8f45c946f21f`). O arquivo raw original não foi alterado.

Após bankcb descramble, o cabeçalho de 16 bytes começa `01 00 9f 15 00 00 16 00 10 00 00 00 e7 97 c0 f4`. Os campos interpretados pelo layout público dão `bankid=1`, `banksize=0x159F` (5.535 bytes), `bankoff=0x10`, CRC do corpo `0x97E7` e CRC do cabeçalho `0xF4C0`. Os testes reproduzidos foram:

- CRC-16 do cabeçalho bankcb, bytes `[0x00,0x0E)`: armazenado/calculado `0xF4C0`, confere.
- CRC-16 do corpo bancário bankcb, bytes `[0x10,0x15AF)`: armazenado/calculado `0x97E7` após descramble, confere.
- CRC-16 dos 5.551 bytes da entrada JLFS após bankcb descramble: o `data_crc` JLFS `0xDC88` confere.
- CRC-16 do payload raw bankcb-scrambled: `0xAFF9`, não confere com `0xDC88`; essa diferença é esperada antes da transformação e não indica corrupção.

A especificação pública de novo firmware JieLi diz que, para `uboot.boot`, o bit `0x40` da flag marca o conteúdo comprimido com LZ4 em formatos de Bluetooth chips como BR23/BR25/BR28 [1]. Isso é evidência de formato aplicável ao layout analisado, não validação por descompressão deste payload específico. O parser executado aqui só descrambla bankcb e calcula CRCs; nenhum LZ4 foi descomprimido, e tamanho/saída de um decodificador LZ4 não foram testados. Não se afirma que o arquivo resultante já seja executável ou um bootloader completo.

O CRC32 zlib `0x4D7CD849` sobre a cópia raw é apenas uma fingerprint sem campo esperado correspondente; não serve para confirmar ou negar integridade do payload.

## Classificação

**Demonstrado:** entrada JLFS inicial denominada `uboot.boot`, flag de compressão `0x40`, estrutura bankcb reconhecida após descramble e CRCs bankcb/JLFS válidos após transformação.

**Documentado, mas ainda não exercitado neste arquivo:** a flag `0x40` representa compressão LZ4 na especificação pública do formato.

**Não demonstrado:** descompressão LZ4, conteúdo de código resultante, endereço de carga, compatibilidade de execução com esta PCB ou método de restauração.

## Referências

[1]: https://kagaimiq.github.io/jielie/datafmt/newfw.html "Formato de novo firmware JieLi"
[2]: https://raw.githubusercontent.com/kagaimiq/jl-misctools/main/firmware/fwunpack_newfw.py "Parser público JLFS fwunpack_newfw.py"
