# Achado: `upgrade.json` e versão declarada

**Origem:** arquivo aninhado no diretório JLFS `ui_upgrade` da imagem `flash.bin`; header da entrada filha em `flash+0x242a7b`, dados em `flash+0x242afb`. O pai `ui_upgrade` começa no header `flash+0x242a5b`.

- Tamanho: 53 bytes.
- SHA-256: `ae106c7058a9247c56bcead61ab62582e86da59f9b1582d0eb5421c7a8de432e`.
- CRC-16 do header JLFS: armazenado/calculado `0x3FB1` (confere).
- CRC-16 dos dados: armazenado/calculado `0x792D` (confere sobre os 53 bytes extraídos).
- Conteúdo JSON observado: `prj_uuid` vazio e `version_id` igual a `W002`.

## Interpretação segura

`W002` é o **identificador de versão explicitamente declarado por este `upgrade.json`**. Esse é o melhor valor para informar no catálogo do arquivo, com o rótulo `version_id`. Os bytes não fornecem uma versão semântica como `1.2.3`, uma data de firmware ou o nome comercial do produto; portanto, não se deve converter `W002` em uma versão pública mais específica.

O arquivo `config.dat`/JCRT contém, separadamente, o item `ver_info`, interpretado pelo patcher local como campos VID/PID/VER. Os bytes do payload são `00 02 00 82 00 00`, isto é, campo final `VER=0x0000` segundo essa interpretação. Não há evidência suficiente para tratar esse valor de configuração como a versão de release do firmware ou para substituir o `version_id=W002`.

O nome de entrada `176103986767848.ufw` também não é uma versão semântica decodificada; a sequência numérica do filename não foi interpretada como timestamp. O modelo “Microwear S11 Pro” é o fornecido pelo usuário. O firmware contém identificadores JieLi/JL701N, mas a identidade comercial do relógio não foi confirmada por texto interno ou inspeção física.

**Classificação:** alta confiança na leitura literal `version_id=W002` e nos CRCs da entrada filha; significado além de “identificador de versão do pacote de atualização” não documentado.
