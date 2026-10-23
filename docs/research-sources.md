# Fontes técnicas verificadas — Microwear S11 Pro

Atualizado em 2026-10-22. Esta nota reúne documentação externa consultada e limitações de aplicabilidade.

## Formato de firmware JieLi

O formato público JLFS descreve cabeçalho de flash e entradas de arquivo com CRC16, offsets, tamanhos, flags e nomes. Ele alerta que certos campos podem aparecer codificados e que entradas com CRC de dados `0xFFFF` podem representar tamanho variável [1]. A documentação de firmware descreve a disposição usual em BR23/BR25/BR28: `uboot.boot`, `isd_config.ini`, `app_dir_head`, `app.bin`, áreas reservadas, `tone`, VM e BTIF. Ela diz que, para `uboot.boot`, a flag `0x40` indica conteúdo comprimido com LZ4; o parser público aplica separadamente `descramble_bankcb` [2]. No arquivo S11 Pro foram reproduzidos bankcb e CRCs após essa transformação, mas **não foi executada descompressão LZ4**. A documentação apoia a interpretação de formato da flag, não prova por si só que uma descompressão concreta do blob extraído já foi validada.

## SDK e toolchain pi32v2

A documentação oficial de ferramentas JieLi informa que a toolchain Linux é disponibilizada no endpoint oficial e indica demos de bibliotecas `pi32v2-r3` para os modelos 700N/701N, separadas de AC710N [3]. Um projeto de SDK público inclui `sdk/JL701N.cbp`, caminhos extensos `cpu/br28`, opções de linker `pi32v2`/`mcpu=r3` e bibliotecas BR28 [4]. Isso dá suporte a usar pi32v2/BR28 como direção de desenvolvimento; não prova que o BSP de áudio implemente o painel ou touch do S11 Pro.

O endpoint JieLi serviu o diretório `jieli-linux-toolchains-20260730.1/`. A documentação oficial de Linux descreve instalação por extração. Uma referência independente recente também identifica essa versão como Clang 4.0.1 e recomenda validar o SHA da versão quando a URL dinâmica muda [5]. O arquivo local foi compilado em sandbox, mas o SHA publicado pela receita mais antiga da ElectronicCats era de uma versão anterior; não o usamos como se validasse a versão 2026. SHA local do arquivo baixado: `a1545cddbc451a06bac43eb5cd96d831470c42a97c5c0b1f98879a20fc7647bd`.

## Configuração compacta lida do firmware

A documentação oficial de `isd_config.ini` estabelece que cada registro compactado começa com o comprimento dos dados, seguido pela chave terminada em NUL e pelo valor; inteiros numéricos são representados como uint32 little-endian [6]. Isso corresponde ao payload JLFS interno de 127 bytes em `flash+0x164f` (SHA-256 registrado em `docs/isd_config_parameters.json`). A página oficial explica que `SPI` codifica `datawidth_clk_mode_port`, que `UTTX` seleciona TX serial e que `UTBD` é baud rate [6]. Esse componente é distinto da entrada UFW externa de mesmo nome, que tem 1.273 bytes e permanece opaca.

Outra página oficial de JieLi diz que o método de configuração externa por `EX_FLASH` e `EX_FLASH_IO` é usado, entre outros, por AC701N, JL701N e AC707N. Ela define `EX_FLASH` como CS, SPI1/C e alimentação, e `EX_FLASH_IO` como `width_CLK_DO_DI_D2_D3` [7]. No payload analisado aparecem `EX_FLASH=PC03_1A_PC08` e `EX_FLASH_IO=4_PC01_PC02_PC04_PC05_PC00`. Os valores sustentam uma configuração de flash externo por barramento de quatro linhas e mapeamento de pinos. Não identificam fabricante, part number ou capacidade do chip de memória.

## Recursos de interface

O repositório aberto `jl-misctools` contém ferramenta RU2 para `menu.res` com magic `RU2\x19`; seu parser rejeita esse firmware `RU30`, então não foi aplicado [8]. As buscas por `RU30`, `upgrade.res` e `upgrade.sty` não localizaram um decoder público confiável. A especificação RU30 permanece inconclusiva até validar outro parser ou obter ferramenta oficial compatível.

## Ghidra

A release oficial corrente consultada é Ghidra 12.2, SHA-256 do ZIP `2c2cd776db3c1f6a097ba418922378ac3649cadd5e844a6f5f088ae628a7be67` [9]. A documentação oficial da instalação requer JDK 25 de 64 bits [10]. O Temurin 25.0.5+8 foi baixado com SHA-256 `68982529869257d0ee6b824ec5aa270ff8b118bb438670da0b97ebdab178d7fb`, publicado pelo endpoint de metadados da Adoptium [11]. Ambos os hashes locais conferiram. O plugin comunitário `ghidra-jieli` marca pi32v2 como cobrindo a maioria, mas não todas, as instruções [12].

## Referências

[1]: https://kagaimiq.github.io/jielie/datafmt/jlfs.html "Formato JLFS JieLi"
[2]: https://kagaimiq.github.io/jielie/datafmt/newfw.html "Formato de novo firmware JieLi"
[3]: https://doc.zh-jieli.com/Tools/zh-cn/dev_tools/toolchains/linux_lib.html "Toolchain Linux JieLi e compatibilidade pi32v2-r3"
[4]: https://gitlab.zh-jieli.com/soundbox/novisualization/ac701n_soundbox_sdk/-/raw/335d6616a63257092f87f43cf2a6c3e59656116e/sdk/JL701N.cbp "Projeto JL701N/BR28 do SDK JieLi"
[5]: https://github.com/dsablic/sidou/blob/main/BUILDING.md "Guia de build que fixa a versão de toolchain JieLi"
[6]: https://doc.zh-jieli.com/Tools/zh-cn/dev_tools/toolchains/ini_cfg.html "Formato de configuração isd_config.ini JieLi"
[7]: https://doc.zh-jieli.com/Tools/zh-cn/mass_prod_tools/burner_1tuo8/extern_flash_burn.html "Parâmetros de flash externo para JL701N e família"
[8]: https://github.com/kagaimiq/jl-misctools/tree/main/ui_resource "Ferramentas UI RU2 JieLi"
[9]: https://github.com/NationalSecurityAgency/ghidra/releases/tag/Ghidra_12.2_build "Release oficial Ghidra 12.2"
[10]: https://github.com/NationalSecurityAgency/ghidra "Instruções oficiais de instalação Ghidra"
[11]: https://api.adoptium.net/v3/assets/latest/25/hotspot "Metadados de versão Temurin 25"
[12]: https://github.com/quarkslab/ghidra-jieli "Linguagem pi32v2 para Ghidra"

## Strings de display/touch observadas no app.bin

A busca literal no `app.bin` encontrou `sh8601` e `gc9b71` consecutivos numa região de strings que também contém nomes como `uart` e `sfc1`; encontrou ainda `lcd_init` e `bcs_touch`. O Ghidra, com base de carregamento provisória 0, não resolveu xrefs para essas três strings. Portanto, são nomes incorporados ao binário, possivelmente drivers compilados, e não comprovam qual controlador está ativo na placa.

O PDF preliminar SH8601A descreve um driver AMOLED LTPS de 480×480, com MIPI DSI de uma lane, DBI e Quad-SPI [13]. O PDF GC9B71 descreve um driver a-TFT LCD de 360×360 e lista variantes de resolução, inclusive 320×360 e 320×390 [14]. Esses documentos descrevem famílias/modelos dos controladores, mas não demonstram que algum deles equipa este relógio. Não foi localizada documentação pública confiável para a string `bcs_touch`.

[13]: https://admin.osptek.com/uploads/SH_8601_A0_Data_Sheet_Preliminary_UCS_V0_0_191226_1_143481d321.pdf "PDF preliminar SH8601A — marcado SHENGHETECH Confidential"
[14]: https://admin.osptek.com/uploads/GC_9_B71_Data_Sheet_V1_1_622df4ec27.pdf "PDF GC9B71, versão 1.1"
