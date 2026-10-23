# Pesquisa de firmware — Microwear S11 Pro

Engenharia reversa estática do firmware fornecido para documentar seus formatos e avaliar caminhos de desenvolvimento alternativo. **Este repositório ainda não contém uma OS alternativa, um SDK/BSP completo nem um método seguro de instalação.**

**Modelo:** Microwear S11 Pro, conforme informado pelo proprietário; marca comercial e revisão física não foram confirmadas apenas pelos bytes. **Versão declarada no pacote:** `ui_upgrade/upgrade.json` contém `version_id: "W002"`. Isso é preservado como identificador literal, não como versão semântica. O campo separado JCRT `ver_info` não foi usado como versão do pacote. Veja [upgrade_json.md](docs/component-findings/upgrade_json.md).

## O que os arquivos permitem fazer agora

O corpus público permite reproduzir e ampliar a análise offline: verificar a estrutura externa UFW, percorrer o JLFS extraído, conferir CRCs e comparar componentes pelo inventário e pelos hashes. O inventário documenta 9 entradas UFW e 17 entradas/âncoras JLFS. As ferramentas estão em `tools/`; consulte [tool-audit.md](docs/tool-audit.md), pois algumas dependem do layout de trabalho e de referências externas, e ainda não são um pacote genérico pronto para qualquer firmware.

O `app.bin` e os projetos Ghidra disponíveis permitem procurar candidatos a rotinas de inicialização, chamadas e referências a periféricos. Esse trabalho precisa ser validado: a base `0x0` é provisória, há conflitos de decodificação e erros de P-code, e as contagens do Ghidra não representam funções ou instruções confirmadas do aparelho.

Os recursos brutos `upgrade.res`, `upgrade.str` e `upgrade.sty` podem servir de base para desenvolver parsers e visualizadores. Ainda não foi demonstrado um decodificador semântico RU30/`.sty`. O companion BCSDIAL permite estudar o formato; foram extraídos 50 JPEGs válidos por carving, mas isso não é um parser do contêiner nem confirma a resolução do display.

O arquivo `config.dat` pode ser usado para estudar a estrutura JCRT: os CRCs de cabeçalho, descritores e sete payloads foram validados. Ele contém um campo de 16 bytes chamado `link_key`, mas sua função, unicidade e uso pelo relógio não foram estabelecidos. O arquivo pertence ao pacote OTA, não a um dump da memória em uso; o campo `serial_num` tem formato parecido com um template. **Não há evidência suficiente para classificar esse campo como credencial ativa, segredo exclusivo ou vulnerabilidade.** Veja [config_dat.md](docs/component-findings/config_dat.md).

A toolchain JieLi disponível foi capaz de compilar um objeto relocatable ELF32 para `pi32v2-r3` a partir de um scaffold mínimo. Isso permite experimentar com compilação de código isolado, mas não produz um executável para o relógio.

## O que ainda não é possível afirmar ou fazer com segurança

Ainda não há evidência suficiente para identificar fisicamente display, touchscreen, RAM, flash ou revisão da placa. Strings como `sh8601`, `gc9b71` e `bcs_touch` são pistas no binário, não confirmação dos componentes montados.

Não há startup, linker script, mapa de memória, BSP/drivers identificados para esta PCB nem imagem alternativa inicializável. O objeto de teste não foi linkado, executado no hardware ou instalado. Não foi estabelecido um procedimento de recuperação comprovado para este exemplar. Portanto, **não grave, transmita nem instale artefatos experimentais no relógio**.

Próximas pesquisas úteis são: (1) decodificar e visualizar RU30/`.sty` sem modificar o original; (2) refinar o ponto de entrada e o mapa de memória do `app.bin` usando evidências do bootloader/SDK; (3) localizar e validar BSP, linker script e drivers compatíveis; (4) identificar a PCB e seus componentes por fotos/dump somente de leitura; e (5) comprovar uma recuperação restaurável antes de qualquer teste que escreva no dispositivo.

## Conteúdo e segurança do branch público

O branch `main` contém atualmente 296 arquivos rastreados, incluindo os dois binários recebidos, arquivos UFW/JLFS extraídos, recursos, imagens do companion, projetos/logs Ghidra e artefatos exploratórios. Assim, avisos antigos que descreviam esses itens como “apenas locais” não refletem o conteúdo atual do branch. A publicação dos bytes não demonstra, por si só, que contenham dados pessoais ou uma vulnerabilidade; campos opacos ainda não foram totalmente caracterizados. A avaliação específica de `config.dat` está em [config_dat.md](docs/component-findings/config_dat.md).

A licença MIT cobre somente código, documentação e scaffold originais deste projeto. Ela não concede direitos sobre firmware, imagens, marcas ou outros materiais de terceiros. Confirme os direitos aplicáveis antes de redistribuir esses materiais fora deste repositório.

## Navegação

- [Progresso técnico detalhado](PROGRESSO.md)
- [Mapa JLFS](docs/partition-map.md) e [inventário JSON](docs/jlfs-inventory.json)
- [Auditoria de integridade/CRC](docs/integrity-audit.md)
- [Achados de hardware e limitações do Ghidra](docs/hardware-findings.md)
- [Achados por componente](docs/componentes-detalhados.md)
- [Auditoria das ferramentas](docs/tool-audit.md)
