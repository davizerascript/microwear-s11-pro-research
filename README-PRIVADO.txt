PACOTE PRIVADO — ARTEFATOS DE ESTUDO NÃO PUBLICADOS

Este arquivo é uma entrega privada ao proprietário do exemplar, não um release público. NÃO envie este ZIP ao GitHub, a fóruns ou a terceiros sem revisar e remover segredos e verificar direitos de redistribuição.

Conteúdo incluído:
- `original/`: arquivos fonte recebidos (`176103986767848.ufw`, `175905457427793.bin`) e hashes originais.
- `extracted/ufw/`: cópias das entradas externas UFW.
- `extracted/decoded/`: arquivos e recursos extraídos/decodificados, inclusive configurações, candidatos de autenticação e mídias. Alguns arquivos podem conter `link_key`, serial, blobs de chave ou outros dados exclusivos do dispositivo. Trate tudo como segredo.
- `analysis/`: logs, regiões brutas, strings, auditorias intermediárias, scripts Ghidra, projeto Ghidra (diretório e ZIP) e objetos de teste pi32v2. Os objetos são relocatable; não são firmware executável/instalável.
- `media/`: pacote das imagens companion extraídas e GIF diagnóstico.
- `quarantine-unreviewed/`: `INVENTARIO_COMPLETO.csv/json`, inventários exploratórios antigos que contêm prefixos de payload e classificação de `blimit` não validada. Não os use como especificação nem como conclusão.
- `SHA256SUMS-PACOTE.txt`: SHA-256 de cada membro do ZIP, exceto o próprio manifesto.

Limites técnicos: `upgrade.res/.str/.sty` foram extraídos, mas não decodificados semanticamente em imagens legíveis. A análise Ghidra usa base provisória 0 e contém conflitos/P-code errors; as contagens não representam funções/instruções verdadeiras. O binário `blimit` e sua interpretação não são uma especificação confirmada. O protótipo pi32v2 não foi ligado, executado nem instalado.

Não incluídos: instalações/cache do Ghidra, JDK, toolchain e instaladores baixados (grandes e de terceiros), nem os checkouts de código-fonte externos. As fontes, versões e referências para obtê-los estão no repositório público: https://github.com/davizerascript/microwear-s11-pro-research (docs/research-sources.md e docs/tool-audit.md).

Para conferir os originais após extrair: entre em `original/` e execute `sha256sum -c SHA256SUMS`.
