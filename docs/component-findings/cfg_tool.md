# `cfg_tool.bin` — achados

**Artefato:** `work/decoded/jlfs/00002040_cfg_tool.bin` (935 bytes; a CRC16 JLFS armazenada confere sobre os bytes extraídos desta entrada).

Não há magic ASCII evidente no início: os primeiros 24 bytes são `a3 03 00 00 00 1a 42 00 00 00 00 00 00 1b 42 00 00 00 00 00 8f 5e c2 03`. Interpretados como palavras little-endian de 32 bits, começam por `0x000003a3`, `0x00421a00`, `0`, `0x00421b00`; sem especificação correspondente, não atribuo semântica a esses valores. O conteúdo é majoritariamente binário, com blocos extensos preenchidos por `00` e `ff`.

Há **20 rótulos regulares** em ASCII de largura fixa: `AC701N_watch` e `AC701N_2` até `AC701N_20`, iniciando em torno de `0x99` e espaçados regularmente em slots preenchidos com NUL. Há ainda dois fragmentos imprimíveis incidentais que não foram contados como rótulos. Também há valores numéricos binários no restante do arquivo. Isso é evidência compatível com tabela de configurações/perfis nomeados, mas não permite decodificar os campos sem uma definição de estrutura ou código consumidor. Não se reconheceu CRC interno conclusivo; a CRC JLFS validada pertence à entrada extraída e não identifica, por si só, o formato interno.

## Classificação

Classificação mais provável: **recurso binário de configuração de runtime JieLi chamado `cfg_tool.bin`**, contendo slots/perfis rotulados `AC701N_*`. A documentação pública de build do SDK JieLi descreve `cfg_tool.bin` como recurso passado com `p11_code.bin` e `config.dat` à etapa de empacotamento do firmware; o documento em questão é especificamente para o SDK `ac707n_watch_lvgl`, com alvo `br35`/AC707N. [1] Isso sustenta a função geral de recurso de configuração, não que este payload específico tenha sido produzido por esse SDK nem que seja compatível com JL701N. Os nomes `AC701N_*` não bastam para essa conclusão e podem ser apenas rótulos gravados no conteúdo.

**Confiança:** média para a categoria geral “recurso de configuração JieLi”, baixa para layout/campos internos e origem exata. No material local pesquisado em `jieli-research` e `jl-misctools`, não foi localizado parser ou especificação que decodifique este payload. Não foram executados empacotadores nem gravadores; o firmware não foi alterado e não houve tentativa de atualização/gravação.

## Referências

[1]: https://github.com/ElectronicCats/jieli-ble-badge-research/blob/main/docs/jieli-sdk-build.md "JieLi AC707N SDK build guide"
