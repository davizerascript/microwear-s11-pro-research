# Achados: `config.dat`

**Artefato:** `work/decoded/jlfs/0024ef19_config.dat` (384 bytes).

O conteúdo começa com `JCRT`. Pelo parser local `scripts/patch_config_dat.py`, esse magic identifica uma estrutura de configuração com cabeçalho little-endian e entradas de 32 bytes: os campos incluem índice, tipo, offset e tamanho do payload, CRC-16 e nome. O cabeçalho observado decodifica como magic `JCRT`, self-CRC `0x15C3`, CRC de cabeçalhos `0x6491`, tamanho total `384` e sete entradas. Recalculei CRC-16/CCITT (polinômio `0x1021`, init `0`) sobre os intervalos: o self-CRC em `[0x06,0x20)` confere (`0x15C3`); o CRC dos sete descritores em `[0x20,0x100)` confere (`0x6491`); e os sete CRCs individuais de payload também conferem. A versão inicial do patcher local tinha um limite hardcoded `[0x20,0xE0)`, que omitia o sétimo descritor e produzia `0xB54F`; a cópia de trabalho do script foi corrigida para derivar o fim pelo `item_count`. Um teste `--dry-run` no arquivo extraído reportou `item_head_crc=0x6491` em `[0x20,0x100)` e self-CRC `0x15C3`; nenhum arquivo foi escrito e o arquivo local permaneceu inalterado. A fingerprint SHA-256 foi omitida da publicação porque este arquivo contém um campo `link_key`.

| Índice | Tipo | Offset/tamanho | Nome | Conteúdo observado |
|---:|---:|---:|---|---|
| 0 | 1 | `0x100` / 6 | `ver_info` | `00 02 00 82 00 00` |
| 1 | 2 | `0x110` / 22 | `ver_info_ext` | 16 bytes opacos redigidos, sufixo ASCII `,jl_v8` |
| 2 | 2 | `0x130` / 16 | `serial_num` | identificador mascarado (`jl_AC701N_[redacted]` na cópia de publicação) |
| 3 | 2 | `0x140` / 1 | `reset_io` | ASCII `1` |
| 4 | 2 | `0x150` / 4 | `pilot_lamp_io` | ASCII `PB03` |
| 5 | 1 | `0x160` / 16 | `link_key` | 16 bytes de material de chave; valor deliberadamente não publicado |
| 6 | 2 | `0x170` / 6 | `power_io` | ASCII `PC03_1` |

A tabela preserva offsets e tamanhos dos campos, mas mascara os valores de identificador/chave. A separação estrutural entre o campo de 16 bytes `serial_num` e o byte seguinte `reset_io` foi verificada no arquivo local; nenhum valor do serial nem do material de chave é exposto aqui. Os tipos numéricos `1` e `2` estão preservados como códigos; não lhes atribuo significado não documentado.

**Classificação:** registro binário de configuração Jieli no formato JCRT, contendo campos nomeados para versão, serial/identificador e sinais/IO, além de uma chave binária. O diretório público `jl-misctools` documenta `mkjlfs.py` como construtor de imagens/entradas JLFS e seus CRCs, mas não documenta JCRT nem a semântica desses itens [1]. O parser e patcher local oferecem evidência direta da interpretação de cabeçalho/entradas e do campo `ver_info` [2]. O texto `AC701N` no serial sugere associação com esse identificador de chip/produto, mas não prova compatibilidade ou que o arquivo foi produzido especificamente para o SoC: o repositório público de UBOOT lista AC701N como BR28 e ressalva que o suporte do utilitário é parcial [3]. Nenhuma compatibilidade com BR35/AC707N ou RU2 é inferida.

**Confiança:** alta para magic, tamanhos, nomes/valores e CRCs; moderada para a classificação como configuração Jieli JCRT; baixa a moderada quanto à função precisa e ao hardware de destino. Para resolver isso faltam documentação de formato JCRT do fornecedor ou código-fonte/artefato comparável que associe os IDs dos itens e seus tipos a semântica e alvo de hardware.

## Referências

[1]: https://github.com/kagaimiq/jl-misctools/blob/main/firmware/mkjlfs.py "Código público mkjlfs.py"
[2]: https://github.com/kagaimiq/jl-misctools "Repositório público jl-misctools, utilitários JieLi"
[3]: https://github.com/kagaimiq/jl-uboot-tool "Repositório público JieLi UBOOT tool e observações de suporte por chip"
