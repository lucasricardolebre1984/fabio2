import asyncio
from app.services.glm_image_service import glm_image_service
from app.schemas.imagem import FormatoImagem

async def test():
    try:
        print("Testando GLM-Image API...")
        image_bytes, custo = await glm_image_service.gerar_imagem(
            'campanha ano novo',
            FormatoImagem.QUADRADO
        )
        print(f'SUCESSO! {len(image_bytes)} bytes')
        print(f'Custo: R$ {custo.custo_brl}')
        print(f'Status: {custo.status}')
    except Exception as e:
        print(f'ERRO: {e}')
        import traceback
        traceback.print_exc()

asyncio.run(test())
