# `upgrade.str` — constatações

**Artefato:** `work/decoded/jlfs/00242abb_upgrade.str` (2.644 bytes). A inspeção foi somente de leitura; nenhum empacotador/gravador foi executado e nenhum firmware ou hardware foi alterado.

Os primeiros quatro bytes são ASCII `RU30` (`52 55 33 30`). O cabeçalho contém, entre outros, `00 03 01 00` nos offsets `0x04–0x07` e `1c 00 00 00` em `0x10–0x13` (inteiro little-endian 28). A partir de `0x14` há registros/dados binários; offsets mais adiante contêm blocos bitmap ou codificados, sem strings textuais legíveis relevantes. `strings` encontrou `RU30` em `0x00` e apenas sequências curtas não interpretáveis em `0x3f0` e `0xa08` (entre outras). Tamanho exato: 2.644 bytes; SHA-256: `5901f377343872e28dfb1619e57208875fe6f002f6673b765956a08c8f22cbf1`; CRC-32 IEEE calculado sobre o arquivo inteiro: `8d0f5b13`. Este CRC integral não é apresentado como CRC do contêiner JLFS; conforme o contexto fornecido, o CRC dos dados JLFS confere.

A evidência local identifica o conteúdo como recurso de UI com assinatura `RU30`, mas não revela de modo suficiente o significado dos campos, a versão exata do esquema ou a função específica de `upgrade.str`. A busca não encontrou especificação pública identificável para `RU30`. O repositório público `jl-misctools` declara conter utilitários diversos JieLi e recursos de UI [1]; seu parser de `menu.res` exige explicitamente a assinatura `RU2\x19` e chama seu tipo `jieli-ru2` [2]. Isso documenta um formato distinto, não decodifica nem prova compatibilidade com `RU30`. Não há base para atribuir este arquivo a uma família de chip específica, nem para alegar compatibilidade com JL701N, BR35/AC707N ou RU2.

**Classificação:** arquivo binário de recurso de UI JieLi, assinatura `RU30`; função interna/formato detalhado indeterminados. **Confiança:** alta para bytes, tamanho e hash; moderada para a identificação genérica como recurso de UI (contexto fornecido e localização); baixa/inconclusiva para esquema, função precisa e compatibilidade.

## Referências

[1]: https://github.com/kagaimiq/jl-misctools "Repositório jl-misctools"
[2]: https://github.com/kagaimiq/jl-misctools/blob/main/ui_resource/menu.res/ru2unpack.py "Parser público RU2 de menu.res"
