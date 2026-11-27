class ErroDeDominio(Exception):
    pass


class ProducaoNaoEncontrada(ErroDeDominio):
    def __init__(self, sigla: str, ano: int) -> None:
        super().__init__(sigla, ano)
        self.sigla = sigla
        self.ano = ano


class DadosIndisponiveis(ErroDeDominio):
    pass


class MercadoIndisponivel(ErroDeDominio):
    pass


class ParametroMercadoInvalido(ErroDeDominio):
    def __init__(self, parametro: str, valor: str) -> None:
        super().__init__(parametro, valor)
        self.parametro = parametro
        self.valor = valor
