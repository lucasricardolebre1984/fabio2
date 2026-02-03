"""Extenso service - Converte valores para extenso em português."""
from decimal import Decimal
from num2words import num2words


class ExtensoService:
    """Service for converting numbers to words in Portuguese."""
    
    @staticmethod
    def valor_por_extenso(valor: Decimal | float | str) -> str:
        """
        Convert monetary value to Portuguese words.
        
        Args:
            valor: Monetary value (e.g., 1500.50)
            
        Returns:
            String with value in words (e.g., "mil quinhentos reais e cinquenta centavos")
            
        Example:
            >>> ExtensoService.valor_por_extenso(Decimal("1500.50"))
            'mil quinhentos reais e cinquenta centavos'
            >>> ExtensoService.valor_por_extenso(Decimal("1.00"))
            'um real'
            >>> ExtensoService.valor_por_extenso(Decimal("0.50"))
            'cinquenta centavos'
        """
        if isinstance(valor, str):
            valor = Decimal(valor.replace(',', '.'))
        elif not isinstance(valor, Decimal):
            valor = Decimal(str(valor))
        
        # Separate reais and centavos
        reais = int(valor)
        centavos = int((valor - reais) * 100)
        
        parts = []
        
        # Convert reais
        if reais > 0:
            reais_text = num2words(reais, lang='pt_BR')
            reais_text = reais_text.replace(' e ', ' ')
            
            # Plural/singular
            if reais == 1:
                parts.append(f"{reais_text} real")
            else:
                parts.append(f"{reais_text} reais")
        
        # Convert centavos
        if centavos > 0:
            centavos_text = num2words(centavos, lang='pt_BR')
            
            if centavos == 1:
                parts.append(f"{centavos_text} centavo")
            else:
                parts.append(f"{centavos_text} centavos")
        
        # Join with " e "
        if len(parts) == 2:
            return f"{parts[0]} e {parts[1]}"
        elif len(parts) == 1:
            return parts[0]
        else:
            return "zero reais"
    
    @staticmethod
    def numero_por_extenso(numero: int) -> str:
        """
        Convert integer to Portuguese words.
        
        Args:
            numero: Integer number
            
        Returns:
            String with number in words
            
        Example:
            >>> ExtensoService.numero_por_extenso(45)
            'quarenta e cinco'
        """
        return num2words(numero, lang='pt_BR')
    
    @staticmethod
    def calcular_valor_parcela(valor_total: Decimal, valor_entrada: Decimal, qtd_parcelas: int) -> Decimal:
        """
        Calculate installment value.
        
        Args:
            valor_total: Total contract value
            valor_entrada: Down payment
            qtd_parcelas: Number of installments
            
        Returns:
            Installment value (2 decimal places)
        """
        restante = valor_total - valor_entrada
        valor_parcela = restante / qtd_parcelas
        return valor_parcela.quantize(Decimal('0.01'))
