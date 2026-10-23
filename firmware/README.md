# Firmware scaffold (não-flashável)

Este diretório contém somente a interface inicial da aplicação. Não é um firmware completo para o Microwear S11 Pro e não contém startup, linker script, drivers, bootloader, tabela de vetores, configuração de memória ou pacote UFW.

`include/board_port.h` define o limite que deve ser implementado pelo BSP verificado. `src/main.c` oferece apenas um loop principal com funções da placa ainda não implementadas. A pinagem, o painel LCD, o touch, a memória e o método de recuperação permanecem sem confirmação no exemplar.

## Teste de compilação cruzada

Com a toolchain JieLi `pi32v2` extraída em `../work/toolchain/jieli-linux-toolchains-20260730.1/pi32v2`, rode `make -C firmware compile-check`. O alvo compila apenas `src/main.c` em um objeto ELF32 relocatable, little-endian, usando `clang -target pi32v2 -mcpu=r3`. A máquina ELF aparece como `0xf1` para o `readelf` genérico do host. O teste confirma que o compilador aceita o código e emite um objeto do alvo declarado; não demonstra linkagem, boot, operação de hardware, compatibilidade com a placa nem testes no relógio.

Para outra instalação, sobrescreva `JIELI_TOOLCHAIN` com o caminho da pasta `pi32v2`, por exemplo: `make -C firmware compile-check JIELI_TOOLCHAIN=/opt/jieli/pi32v2`.

Não há ainda startup, linker script ou bibliotecas de placa validados, portanto não existe alvo de linkagem ou imagem de firmware. Não instale, grave nem use este objeto como atualização do relógio.
