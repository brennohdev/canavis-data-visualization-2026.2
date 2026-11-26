class ErroDeDominio(Exception):
    pass


class ProducaoNaoEncontrada(ErroDeDominio):
    def __init__(self, sigla: str, ano: int) -> None:
        super().__init__(sigla, ano)
        self.sigla = sigla
        self.ano = ano


class DadosIndisponiveis(ErroDeDominio):
    pass
