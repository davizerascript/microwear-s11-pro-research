# Pesquisa de firmware — Microwear S11 Pro

Projeto de engenharia reversa estática para documentar o firmware fornecido e investigar se existe uma base para desenvolvimento alternativo. **Ainda não é um sistema operacional alternativo, SDK/BSP completo nem método de instalação.**

**Dispositivo:** Microwear S11 Pro (modelo informado pelo usuário; a identidade comercial/revisão não foi confirmada só pelos bytes). **Versão explícita do pacote:** o arquivo aninhado `ui_upgrade/upgrade.json` declara `version_id: "W002"`. `W002` é preservado como identificador literal; não foi convertido em versão semântica. O campo JCRT separado `ver_info` apresenta `VER=0x0000` pela interpretação local e não é considerado a versão do pacote. Veja [o achado de versão](docs/component-findings/upgrade_json.md).

## Estado atual

O firmware original foi preservado e analisado em cópias. Cabeçalhos e lista UFW conferem; o `flash.bin` foi percorrido estruturalmente como JLFS. Foram corrigidos relatórios de CRC do cabeçalho flash e do `uboot.boot`, e a sinalização JLFS `0x40` foi associada a LZ4 conforme documentação pública. O payload ainda não foi descomprimido com LZ4.

Foi possível compilar um objeto relocatable ELF32 para `pi32v2-r3` a partir de um scaffold mínimo. Não foi feita linkagem de firmware, teste no relógio, escrita de flash, OTA ou instalação. O projeto Ghidra usa base `0x0` escolhida pelo analista e tem conflitos/P-code errors; suas contagens não são contagens verdadeiras de código do dispositivo. Controladores de display/touch não foram confirmados fisicamente.

Leia primeiro [PROGRESSO.md](PROGRESSO.md), o [mapa JLFS das 17 entradas](docs/partition-map.md), o [inventário JSON sanitizado](docs/jlfs-inventory.json), [a auditoria CRC](docs/integrity-audit.md), [os achados de hardware/Ghidra](docs/hardware-findings.md) e [a auditoria das ferramentas](docs/tool-audit.md).

Os relatórios mascaram identificadores e omitem bytes de `link_key`, material de chave e campos opacos potencialmente sensíveis. Os mapas e hashes permitem comparar estruturas sem publicar o firmware ou esses valores.

## Diretórios

- `docs/`: resultados, fontes, limitações, hashes e relatórios.
- `firmware/`: scaffold pi32v2 não flashável, usado apenas para validar compilação de objeto.
- `tools/`: scripts locais para inventário, CRC e extração limitada.
- `original/` e `work/`: dados originais, extrações, projetos e dependências locais; devem permanecer fora de uma publicação pública.

## Segurança

**Não instale, transmita nem grave nenhum artefato experimental no relógio.** Ainda não existe método de recuperação confirmado para este exemplar. Antes de qualquer escrita seriam necessários, no mínimo, dump restaurável da memória, identificação física da revisão/ICs, pinout comprovado e um procedimento de recuperação de bootloader/ISP demonstrado.

Não publique firmware original, dumps extraídos, watchfaces/imagens, bancos Ghidra ou pacotes de toolchain/SDK sem confirmar os direitos de redistribuição. Hashes e análises textuais podem documentar a amostra sem redistribuir seus bytes. O `.gitignore` evita alguns desses arquivos por padrão, mas não remove arquivos já rastreados.

## Licença

A licença MIT deste repositório cobre o código, a documentação e o scaffold originais disponibilizados aqui. Ela não concede direitos sobre firmware, imagens, marcas ou outros materiais de terceiros; esses binários e recursos não fazem parte do repositório.

## Reprodução local

Os scripts que operam sobre arquivos exigem cópias locais em `original/` e alguns ainda dependem do checkout de referência JieLi em `work/jieli-research/`. O checkout de referência, seus executáveis e o SDK não são incorporados a uma instalação limpa. Consulte [tool-audit.md](docs/tool-audit.md) antes de executar qualquer script; não use caminhos de saída já existentes.

A ferramenta [audit_integrity.py](tools/audit_integrity.py) é a mais independente: lê o UFW e imprime relatório CRC; use `--out` somente para um destino novo. `extract_jlfs.py` ainda está amarrada ao layout local do workspace e não deve ser apresentada como ferramenta genérica pronta para publicação.

## Próximas lacunas

1. Fotografias macro da placa e identificação física de flash/RAM/display/touch.
2. Dump read-only de memória física e mapeamento verificável de boot/endereço de carga.
3. SDK/BSP e linker script compatíveis com a revisão da PCB.
4. Decodificador confiável para RU30/`.sty` e parser semântico BCSDIAL.
5. Caminho de recuperação original comprovado antes de qualquer teste que escreva no dispositivo.
