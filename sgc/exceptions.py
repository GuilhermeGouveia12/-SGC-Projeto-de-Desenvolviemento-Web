from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)


class SGCException(Exception):
    """Exceção base do SGC."""
    status_code = status.HTTP_400_BAD_REQUEST
    default_message = 'Erro interno do sistema.'

    def __init__(self, message=None):
        self.message = message or self.default_message
        super().__init__(self.message)


class EstoqueInsuficienteException(SGCException):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    default_message = 'Estoque insuficiente para realizar a venda.'


class ClienteComVendasException(SGCException):
    status_code = status.HTTP_409_CONFLICT
    default_message = 'Cliente possui vendas registradas e não pode ser removido.'


class VendaSemItensException(SGCException):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    default_message = 'A venda deve conter ao menos um item.'


class CPFDuplicadoException(SGCException):
    status_code = status.HTTP_409_CONFLICT
    default_message = 'Já existe um cliente cadastrado com este CPF.'


def handler_global(exc, context):
    """Handler global: trata exceções SGC e delega o restante ao DRF."""
    if isinstance(exc, SGCException):
        logger.warning('SGCException: %s', exc.message)
        return Response(
            {'erro': exc.message},
            status=exc.status_code,
        )

    response = exception_handler(exc, context)

    if response is not None:
        payload = {'erro': response.data}
        response.data = payload
        return response

    logger.error('Exceção não tratada: %s', exc, exc_info=True)
    return Response(
        {'erro': 'Erro interno do servidor. Tente novamente mais tarde.'},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
