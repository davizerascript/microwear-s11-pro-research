# `upgrade.res` — component finding

Arquivo analisado: `work/decoded/jlfs/00242a9b_upgrade.res` (31,843 bytes).

A observação direta confirma os quatro bytes iniciais ASCII `RU30` (offset `0x00`). Os bytes seguintes até `0x4f` são um cabeçalho/descritor opaco: por exemplo, `0x04–0x07 = 00 03 01 00`, `0x08–0x0b = 01 00 00 00`, `0x0c–0x0f = df 6c 47 e5`, e `0x30–0x4f` contém campos binários variados. A partir de `0x50` há 31,763 bytes de dados predominantemente binários. Não há nomes de arquivos ou strings ASCII legíveis significativas além de `RU30`; `strings` mostra poucos fragmentos curtos sem contexto interpretável.

Verificações reproduzíveis: SHA-256 do arquivo `0f978805ff0fc4bde0513cb45b97911ab1ff9050106e2596756e867e5deef44e`; CRC-32 padrão do arquivo inteiro `0x6f346916`, dos bytes após a magic `0xcbd87dad` e da região `0x50..EOF` `0xf96962fc`. O valor little-endian em `0x0c` (`0xe5476cdf`) não coincide com esses CRC-32. Não foi identificado esquema de checksum para esse campo nem significado confiável para os demais campos. Conforme contexto fornecido, o CRC da entrada JLFS que contém o arquivo confere; isso valida a integridade no contêiner externo, não decodifica este formato.

A documentação pública consultada descreve JLFS e o formato unificado de firmware Jieli, inclusive áreas de recursos e entradas de arquivos, mas não documenta `RU30` nem este cabeçalho. A documentação JLFS define CRC16 para entradas e trata do filesystem externo [1]. O documento de firmware relaciona formatos de firmware e áreas de recursos em chips como BR22/BR23/BR25/BR28 [2]; não estabelece que um payload individual `RU30` obedeça a esses layouts. As ferramentas locais examinadas incluem um construtor JLFSv2; não foi encontrado suporte documentado a `RU30` nas referências consultadas. O `jieli-research` local identifica explicitamente seu alvo como AC707N/BR35, portanto seus achados não autorizam atribuir este formato a JL701N ou generalizar compatibilidade [3]. A ferramenta RU2 pública, conforme contexto fornecido, também rejeita a variante RU30.

**Classificação:** recurso binário proprietário/variante `RU30`, associado pelo contexto ao payload de UI `ui_upgrade`; os bytes disponíveis não bastam para afirmar codificação, subformato, tabela ou função interna exata além dessa associação contextual. Não demonstrada compatibilidade com RU2, JL701N, BR35/AC707N ou outras famílias. Para fechar a identificação faltam uma especificação/fonte que implemente RU30 ou amostras/documentação independentes que permitam validar offsets, tamanhos e checksums; sem isso, os campos do cabeçalho permanecem não classificados.

## Referências

[1]: https://kagaimiq.github.io/jielie/datafmt/jlfs.html "JieLi STUFF: JLFS format"
[2]: https://kagaimiq.github.io/jielie/datafmt/newfw.html "JieLi STUFF: New Firmware Format"
[3]: https://github.com/ElectronicCats/jieli-ble-badge-research "ElectronicCats jieli-ble-badge-research repository"
