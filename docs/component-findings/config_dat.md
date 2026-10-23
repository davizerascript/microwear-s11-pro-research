# Achados: `config.dat`

**Artefato:** `0024ef19_config.dat`, 384 bytes, extraído do JLFS contido no pacote OTA. Não é um dump de memória do relógio em uso. A cópia bruta está atualmente rastreada em `extracted/decoded/jlfs/0024ef19_config.dat` no branch público; esta nota não reproduz os bytes dos campos `serial_num` e `link_key`.

O arquivo começa com `JCRT`. A estrutura observada tem cabeçalho little-endian e sete descritores de 32 bytes. A validação independente confirmou o tamanho total de 384 bytes, o self-CRC `0x15C3` sobre `[0x06,0x20)`, o CRC dos descritores `0x6491` sobre `[0x20,0x100)` e os CRCs dos sete payloads. O cálculo usou CRC-16/CCITT, polinômio `0x1021` e init `0`. A cópia pública do arquivo corresponde byte a byte ao arquivo analisado localmente. CRCs válidos demonstram consistência dos intervalos verificados, não autenticidade, confidencialidade ou função dos dados.

| Índice | Tipo | Offset/tamanho | Nome | Observação do payload |
|---:|---:|---:|---|---|
| 0 | 1 | `0x100` / 6 | `ver_info` | `00 02 00 82 00 00` |
| 1 | 2 | `0x110` / 22 | `ver_info_ext` | 16 bytes opacos; sufixo ASCII `,jl_v8` |
| 2 | 2 | `0x130` / 16 | `serial_num` | O padrão observado parece `jl_AC701N_` seguido de seis dígitos; valor omitido nesta nota |
| 3 | 2 | `0x140` / 1 | `reset_io` | ASCII `1` |
| 4 | 2 | `0x150` / 4 | `pilot_lamp_io` | ASCII `PB03` |
| 5 | 1 | `0x160` / 16 | `link_key` | Campo binário de 16 bytes; valor omitido nesta nota |
| 6 | 2 | `0x170` / 6 | `power_io` | ASCII `PC03_1` |

O formato de `serial_num` parece genérico ou template de teste, mas uma única amostra não prova que seja placeholder, nem que seja compartilhado entre dispositivos. O campo `link_key` contém 16 bytes não nulos, não textuais e distintos entre si. Essas propriedades não revelam sua finalidade ou entropia. O nome do campo, isoladamente, não demonstra que seja uma chave de pareamento, um segredo exclusivo do relógio ou um dado operacional.

**Conclusão de segurança:** não foi demonstrado que esse arquivo contenha uma credencial ativa, dados pessoais do usuário ou uma vulnerabilidade. Como o arquivo pertence a um pacote OTA e não a uma leitura de memória em uso, não se pode inferir que o conteúdo reflita o estado do relógio. Para resolver a função e a abrangência de `link_key`, seriam necessárias amostras independentes comparáveis, referências de código que leiam o campo ou documentação de formato do fornecedor. A análise não tentou autenticação nem interação com o relógio.

**Confiança:** alta para magic, tamanho, número de descritores, nomes, offsets e CRCs; moderada para a classificação estrutural como JCRT/configuração; não determinada para a semântica de `link_key`, o caráter de template do serial e o hardware de destino. O texto `AC701N` é uma pista de associação, não prova de compatibilidade física.

## Referências

[1]: https://github.com/kagaimiq/jl-misctools/blob/main/firmware/mkjlfs.py "Código público mkjlfs.py"
[2]: https://github.com/kagaimiq/jl-misctools "Repositório público jl-misctools, utilitários JieLi"
[3]: https://github.com/kagaimiq/jl-uboot-tool "Repositório público JieLi UBOOT tool e observações de suporte por chip"
