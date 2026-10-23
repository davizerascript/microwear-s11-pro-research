# Achado: `p11_code.bin`

**Artefato:** `work/decoded/jlfs/0024b3f1_p11_code.bin` (15.112 bytes; SHA-256 `6837261c75cf3e8c0b59fc2d4469d568d21ce6f37c67001a8dfbcc32d475da1f`). `file` identifica apenas como `data`, sem formato reconhecido.

## Evidência observável

O início não contém assinatura ASCII óbvia. Bytes 0–31: `07 00 80 3a 80 00 00 00 70 00 00 00 f1 2e 29 63 00 00 04 00 55 aa 55 aa f0 3a 00 00 cf 99 63 a4`. Os bytes 0x10–0x6f exibem seis registros de 16 bytes com índices crescentes (`00`–`05`), campo `04 00`, marcador repetido `55 aa 55 aa`, valores semelhantes a offsets e palavras variáveis. Em 0x70 começa conteúdo binário denso; o tamanho total é 0x3b08. Strings ASCII notáveis: `sc7a20h` em 0x204 e 0x261, `demo` em 0x2a0 e `sensor` em 0x2a5. A maior parte do conteúdo é não imprimível. O CRC JLFS do registro/contêiner confere segundo a validação fornecida; não foi inferido nem recalculado um CRC interno a partir desses bytes.

## Classificação

**Mais provável: payload de código/recurso de configuração P11 usado como entrada de recurso de firmware JieLi; não identificado como imagem de firmware independente nem como formato interno decodificado.** A evidência pública localiza `p11_code.bin` explicitamente como argumento `-res` de `isd_download.exe`, junto a `cfg_tool.bin` e `config.dat`, numa receita de build para alvo **BR35/AC707N** [1]. Isso sustenta sua função como componente fornecido ao empacotador, mas não explica a estrutura interna nem prova que o componente observado veio desse alvo. A documentação pública geral de firmware JieLi descreve a arquitetura de imagem superior e menciona `cfg_tool.bin`, mas não documenta `p11_code.bin` [2]. Portanto, não atribuo compatibilidade com JL701N, nem identifico arquitetura de CPU, ABI ou função do código apenas pelas strings e bytes.

**Confiança:** média para a identificação como entrada/componente P11 de recurso; baixa para qualquer semântica interna específica. Falta documentação pública do formato P11 ou comparação controlada com `p11_code.bin` de SDK/alvo comprovadamente correspondente, incluindo layout, campos e verificações internas. Nenhum empacotador ou gravador foi executado e nenhum firmware/hardware foi alterado.

## Referências

[1]: https://github.com/ElectronicCats/jieli-ble-badge-research/blob/main/docs/jieli-sdk-build.md "ElectronicCats, build JieLi AC707N SDK"
[2]: https://kagaimiq.github.io/jielie/datafmt/newfw.html "JieLi new firmware format"
