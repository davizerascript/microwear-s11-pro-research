MANIFESTO DO PACOTE DE ESTUDO (nome histórico deste arquivo: README-PRIVADO.txt)

Este arquivo está no repositório público. O título histórico não significa que o conteúdo descrito permaneça privado, nem constitui avaliação de direitos de redistribuição.

Conteúdo rastreado no branch público:
- `original/`: arquivos recebidos (`176103986767848.ufw`, `175905457427793.bin`) e hashes.
- `extracted/ufw/`: entradas extraídas do contêiner UFW.
- `extracted/decoded/`: arquivos JLFS, recursos e 50 JPEGs obtidos por carving do companion.
- `analysis/`: logs, regiões brutas, strings, auditorias intermediárias, scripts e projetos Ghidra, além de objetos de teste pi32v2. Os objetos ELF são relocatable e não são firmware executável/instalável.
- `media/`: ZIP das imagens companion e prévia GIF.
- `quarantine-unreviewed/`: inventários exploratórios antigos com prefixos de payload e classificação de `blimit` não validada. Não os use como especificação nem como conclusão.
- `SHA256SUMS-PACOTE.txt`: hashes dos membros do pacote indicado pelo manifesto.

Limites técnicos: `upgrade.res/.str/.sty` foram extraídos, mas não decodificados semanticamente em imagens legíveis. A análise Ghidra usa base provisória 0 e contém conflitos/P-code errors; as contagens não representam funções/instruções verdadeiras. O binário `blimit` e sua interpretação não são uma especificação confirmada. O protótipo pi32v2 não foi ligado, executado nem instalado.

Nota sobre segurança: o `config.dat` do pacote OTA contém um campo binário de 16 bytes denominado `link_key`. Sua finalidade, unicidade e uso não foram determinados. Não há evidência suficiente para chamá-lo de credencial ativa, dado pessoal ou vulnerabilidade; veja `docs/component-findings/config_dat.md`. Outros campos opacos também não devem ser rotulados como segredos sem evidência, mas continuam sem caracterização completa.

A licença MIT do projeto não concede direitos sobre firmware, imagens ou outros materiais de terceiros. Verifique os direitos aplicáveis antes de redistribuir os artefatos fora deste repositório. Instalações/cache do Ghidra, JDK, toolchain, instaladores e checkouts de código-fonte externos não estão incluídos; consulte `docs/research-sources.md` e `docs/tool-audit.md`.
