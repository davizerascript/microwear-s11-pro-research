# `upgrade.sty` — constatações

Arquivo analisado: `work/decoded/jlfs/00242adb_upgrade.sty` (522 bytes). O conteúdo não tem magic ASCII identificável no início: começa `01 f8 00 20 88 5c a4 62`. Há sequências que parecem campos little-endian/pointers e nomes terminados em NUL, incluindo `none` (offset `0x94`), `strpic` (`0x9c`) e `none` (`0xc8`). O restante é predominantemente binário. CRCs calculados sobre o arquivo inteiro: CRC-32/IEEE `0xcc7793fd`; CRC-16/XMODEM `0xc902`. Estes valores são fingerprints calculados, não validação de checksum: não foi localizado algoritmo/campo de checksum aplicável ao `.sty`.

O contexto informado identifica `upgrade.sty` como payload UI em `ui_upgrade` dentro de JLFS; a integridade CRC da entrada JLFS já foi validada separadamente. O repositório público `jl-misctools` caracteriza-se como utilitários JieLi e contém ferramentas UI explicitamente para `menu.res` e PIX font; sua documentação disponível não descreve `.sty` nem oferece parser desse tipo [1]. Um patch do repositório `jieli-research` documenta `.sty`, `.res`, `.str` e `.tab` como recursos JLUI dentro de um sdfile chamado `JL` [2]. Isso sustenta a associação ampla a recursos de UI JieLi/JLUI, não a interpretação do layout binário deste arquivo.

**Classificação:** provável recurso/descritor binário de UI `upgrade` pertencente ao ecossistema JLUI/JieLi; formato interno, significado dos campos e compatibilidade específica não determinados. Não há evidência aqui para atribuir suporte a JL701N. Confiança: média para a família/função geral (nome, contexto JLFS e documentação de `.sty` como JLUI), baixa para semântica/formato exatos. Para elevar a conclusão faltam especificação pública ou parser que reconheça `.sty`, confirmação da versão/target do firmware e definição verificável dos campos/checksum.

## Referências

[1]: https://github.com/kagaimiq/jl-misctools "jl-misctools — JieLi utilities and UI resource tools"
[2]: https://github.com/ElectronicCats/jieli-ble-badge-research/blob/main/patches/badge/badge-menu.patch "Jieli BLE badge research — patch documenting JLUI resource files"
