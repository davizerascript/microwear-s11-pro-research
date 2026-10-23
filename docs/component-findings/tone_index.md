# Índice e recursos `tone`

`tone/index.idx` (`002114bb_index.idx`) tem 174 bytes e começa com ASCII `TIDX`. O CRC-16 little-endian do cabeçalho é `0x9125` e confere sobre os seis bytes de preenchimento `FF` mais a contagem little-endian 12, usando polinômio `0x1021`, `init=0`, sem reflexão e sem XOR final. Há 12 registros de tamanho variável, contíguos de `0x10` até EOF (`0xae`); cada CRC-16 de registro confere. Cada registro traz tamanho, índice 1-based e nome terminado em NUL.

Nomes/IDs: 1 `drain`, 2 `sos`, 3–6 `msg0.mp3`–`msg3.mp3`, 7–10 `call0.mp3`–`call3.mp3`, 11 `asrhello.mp3`, 12 `asrbye.mp3`.

## Conteúdo confirmado do diretório pai

O diretório JLFS `tone` contém 13 filhos: o índice acima, `drain.wtg` (5.600 bytes), `sos.wtg` (2.100 bytes) e os dez MP3 listados. Todos os 13 headers e CRCs de dados dos filhos conferem sobre os bytes extraídos. A ferramenta independente `file` reconheceu **10/10** arquivos `.mp3` como áudio MP3/ADTS. Os dois `.wtg` permanecem como `data` opaco: o formato e a finalidade não foram determinados.

Isto demonstra a presença dos arquivos nomeados no diretório, não quando ou como o firmware os toca. Nenhum decoder de `.wtg`, reprodução de áudio ou transcrição foi executado. O índice TIDX em si não é um payload de áudio e não confirma comportamento específico do JL701N.

## Referências

- [Formato de firmware JieLi / estrutura `tone.idx`](https://kagaimiq.github.io/jielie/datafmt/newfw.html).
- [Gerador público `tonecfgmk.py`](https://github.com/kagaimiq/jl-misctools/blob/main/firmware/tonecfgmk.py).
