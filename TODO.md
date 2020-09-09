# TODO

## 2020-08-07

- [ ] Odenar os contornos do dreno e selecionar o maior deles
- [ ] Colocar o texto com proporção a janela selecionada
- [ ] Adicionar propriedades de configuração da camera
- [x] Criar modulo para desenhar na tela

## 2020-08-06

- [ ] Arrumar o esquema de multiplos monitores
- [x] Comparar as propriedades da etiqueta na classe do Tanque
- [x] Carregar o modelo das etiquetas fora do escopo da etiqueta
- [x] Filtrar a etiqueta na imagem apenas uma vez

## 2020-08-02

- [ ] Tracker deve conter a troca de um filtro para o outro
- [ ] Tracker deve conter o ajuste fino do hardware da WebCam
- [x] Tracker deve conter o ajuste dos filtros HSV e LAB
- [x] Adicionar trackers que se inicializam com um comando no teclado
- [x] Verificar se o sistema operacional é linux ou windows

## 2020-07-21

- [ ] Criar filtro de exclusao de area e cores nao desejadas / berço
- [x] Definir parametros de configuração do hardware da camera
- [x] Adicionar filtros adicionais para identificar o dreno

## 2020-06-29

- [x] IMPORTANTE MUDAR O FILTRO PARA LAB!!

## 2020-06-22

- [ ] Adicionar botao para printar valores do PLC
- [x] Ajustar os valores de posição do dreno
- [x] Limitar ainda mais o filtro do dreno
- [x] Corrigir o position enviado para o PLC e colocar no valor do angulo
- [x] Adicionar thread separada para o PLC

## 2020-06-08

- [ ] Adicionar noise images na hora do treinamento
- [x] Selecionar todas as etiquetas prováveis, caso a contagem de contornos de maior que um, não computar os valores de posição

## 2020-06-05

- [ ] Criar botão para recarregar o PLC
- [x] Alterar programa para interpretar medidas percentuais
- [x] Verificar se performance aumenta utilizando resolução menor - SIM

## 2020-06-03

- [ ] Alterar porcentagem de tolerancia para tanques menores
- [ ] Treinar modelo para verificar se há tanque ou não
- [x] Criar comandos para mostrar imagem com diferentes filtros
- [x] Coletar a informação do dreno relativa ao X/Y do tanque
- [x] Adicionar comando para gravar video
- [x] Implementar logs
- [x] Criar filtro para identificar a posição do dreno
- [x] Corrigir os valores exibidos para o angulos (mostrar apenas positivos e menores que 45°)
- [x] Criar mensagem indicando a conexão com o PLC
- [x] Fazer linhas para identificar os limites da mesa / Deixar os parametros no config
- [x] Adicionar lista de comandos em tela separada
- [x] Alterar o comando Save para salvar apenas a imagem sem os marcadores / Adicionar opção nas configurações
- [x] Fazer PLC sempre escrever mesmo que sem identificar tanque na posição
- [x] Criar comando para recarregar parametros de configuração
