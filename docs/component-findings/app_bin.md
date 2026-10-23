# `app.bin` — achados do artefato

**Artefato:** `work/decoded/jlfs/00002020_app.bin` (2.158.452 bytes; SHA-256 `94dce0755d4c70f26f870fe1429deb7183bd4090429daab79b21522192d977be`). O cabeçalho JLFS e o CRC16 do payload já foram validados no contexto fornecido.

## Evidência observada

- `file` identifica apenas `data`. Os primeiros bytes são `ee ff 40 60 10 00 ed ff 40 60 10 00 d8 e8 07 00...`; não há assinatura de contêiner convencional evidente no início. Não foi observado cabeçalho ELF ou magic LZ4-frame (`04 22 4d 18`) no início. Isso não exclui blocos LZ4 sem enquadramento.
- Bytes iniciais têm aspecto de instruções/dados de máquina, não texto; `strings` retorna sequências curtas majoritariamente não legíveis, sem identificação de produto ou arquitetura. Não há, a partir disso, atribuição confiável de SoC ou de modelo.
- A entropia em blocos de 64 KiB não é uniforme: fica aproximadamente 6,8–7,1 bits/byte na maior parte dos primeiros ~1,25 MiB, cai em regiões posteriores (por exemplo, ~5,5–6,0 em partes entre ~0xD0000 e ~0x120000) e é ~5,0 nos últimos ~0xEF74 bytes, com trechos de zeros notáveis. Tais estatísticas mostram dados heterogêneos, mas não delimitam sozinhas seções ou compressão.
- A documentação pública do fluxo SDK **BR35/AC707N** descreve um `app.bin` concatenado: código `.text` e seções de dados/overlays em claro, seguido por `dat_bank.lz4`, gerado com `lz4_packet` e dicionário `.text` [1]. Isso torna plausível haver trecho comprimido em um app.bin desse fluxo; não prova que este artefato específico use esse layout. A documentação é específica de AC707N/BR35 e não autoriza transferir essa identificação a JL701N, RU2 ou a este binário.
- A fonte pública JieLi para **BR52** também mostra uma receita de concatenação com uma saída `compress.bin` de `lz4_packet` [2], mas é outra família; é evidência apenas de que o SDK usa empacotamento proprietário por concatenação em outros alvos, não um decodificador para este arquivo.
- Os repositórios locais contêm documentação e utilitários de firmware; a documentação local `jieli-sdk-build.md` confirma a receita BR35/AC707N referida acima. Não executei empacotadores, descompactadores ou gravadores. As ferramentas locais genéricas para firmware não identificaram, por evidência inspecionada, offsets/estrutura específica deste payload.

## Classificação e limites

Classificação mais segura: imagem bruta de aplicação extraída de uma entrada JLFS, sem contêiner ou cabeçalho autoidentificável no início; provavelmente composta por segmentos binários, potencialmente com regiões comprimidas em formato LZ4-packet/proprietário. **Não foi possível confirmar nem localizar com precisão uma parte descompactável deste arquivo**, pois o pacote documentado depende de limites de segmentos, metadados do build ou decoder compatível; não há magic de LZ4-frame que permita descompressão genérica. Também faltam identificação independente da família/SoC e especificação/decoder correspondente a este firmware. Confiança moderada na classificação geral como imagem binária segmentada; baixa quanto ao algoritmo, offsets e arquitetura exata.

## Referências

[1]: https://github.com/ElectronicCats/jieli-ble-badge-research/blob/main/docs/jieli-sdk-build.md "Build JieLi AC707N SDK end-to-end"
[2]: https://gitlab.zh-jieli.com/ai_test/jl709n/-/blob/feature_vivo_01_04/SDK/cpu/br52/tools/download.c "JieLi BR52 download.c"
