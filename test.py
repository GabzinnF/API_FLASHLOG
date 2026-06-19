from sqlalchemy import select

from models import Cliente, Emcomenda, db_session, Movimentacao, Centro_distribuicao

# comparar_cidade = (
#     select(Cliente, Emcomenda).where(Emcomenda.id == 20)
#     .join(Emcomenda, Cliente.id == Emcomenda.cliente_id)
# )
# result = db_session.execute(comparar_cidade).scalars().one_or_none()
# print(result.serialize())

sql_movimentacao = (select(Movimentacao, Centro_distribuicao).where(Movimentacao.encomenda_id == 20)
                    .join(Centro_distribuicao, Centro_distribuicao.id == Movimentacao.centro_id)
                    .order_by(Movimentacao.criado_em.desc()).limit(1))
ultima_movimentacao = db_session.execute(sql_movimentacao).tuples().one_or_none()

movs = []
for item in ultima_movimentacao:
    movs.append(item.serialize())

print(movs)

