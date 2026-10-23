# Análise do binário companion `175905457427793.bin`

## Integridade e identificação

O arquivo anexado foi preservado sem alteração em `original/175905457427793.bin`. Tamanho: 805.240 bytes. SHA-256: `65d5464dca61d051ded8092faa83318f1761dbc6016a711f037a97bc10aaafd3`.

Os primeiros 21 bytes formam a assinatura textual `BCSDIAL20250928164504`. Um uint32 little-endian em offset `0x40` é `805236`, igual ao tamanho do arquivo menos 4. Os significados completos do cabeçalho e do texto de data não foram documentados publicamente nem estabelecidos experimentalmente; portanto, a data não foi interpretada como instante de criação com fuso.

## Recursos extraídos

O utilitário local `tools/extract_bcsdial.py` procurou assinaturas JPEG e validou cada resultado com Pillow. Foram extraídos **50 JPEGs completos**, todos com 320×384 pixels, cada qual com manifesto de offset, tamanho e SHA-256 em `work/decoded/bcsdial/manifest.json`. O conteúdo visual de amostras é gráfico abstrato rosa/laranja; há variação entre imagens. O GIF diagnóstico concatena os 50 JPEGs na ordem dos offsets, a 10 quadros/s. Essa visualização é uma hipótese de sequência e **não** demonstra a semântica de animação do formato.

Assinaturas adicionais `BM` e `1f 8b` encontradas por varredura não passaram na validação estrutural de BMP ou na validação CRC/trailer de gzip; não foram tratadas como recursos. Não foi reconhecido um índice/tabela de arquivos BCS DIAL, nem determinado como as imagens se relacionam a sensores, time, UI ou recursos de firmware. A busca pública pelo magic específico não encontrou uma especificação confiável.

## Artefatos produzidos

- Binário original preservado: `original/175905457427793.bin`.
- Extrator reproduzível: `tools/extract_bcsdial.py`.
- Manifesto: `work/decoded/bcsdial/manifest.json`.
- Prévia diagnóstica e arquivo ZIP com os 50 JPEGs/manifesto existem como artefatos locais, mas são excluídos por `.gitignore`; não os publique sem verificar os direitos de redistribuição.

A assinatura `BCSDIAL` e os gráficos sugerem uma relação com recursos de mostrador, mas a relação deste arquivo com o UFW do S11 Pro ainda é uma hipótese. Não foi instalado nem enviado ao relógio.
