import re
from difflib import SequenceMatcher
from app.infrastructure.phi_model_client import PhiModelClient
from app.core.logging_config import logger

class PhiNeutralizer:
    def __init__(self):
        self.model_client = PhiModelClient()
        logger.info("PhiNeutralizer inicializado con cliente de modelo remoto")

    def reemplazar_modismo_manual(self, frase: str, modismo: str, significado: str) -> str:
        def mantener_caso(original, reemplazo):
            if original.isupper():
                return reemplazo.upper()
            elif original[0].isupper():
                return reemplazo.capitalize()
            else:
                return reemplazo.lower()
        
        # Estrategia 1: Buscar primero exactamente el modismo
        pattern_exacto = re.compile(re.escape(modismo), re.IGNORECASE)
        if pattern_exacto.search(frase):
            def reemplazo_func(match):
                return mantener_caso(match.group(), significado)
            frase_reemplazada = pattern_exacto.sub(reemplazo_func, frase)
            return frase_reemplazada
        
        # Estrategia 2: Buscar variaciones con conjugaciones comunes
        sufijos_verbales = ['ar', 'er', 'ir', 'ando', 'iendo', 'ado', 'ido', 'ará', 'erá', 'irá']
        raiz = modismo
        for sufijo in sufijos_verbales:
            if modismo.endswith(sufijo):
                raiz = modismo[:-len(sufijo)]
                break
        
        # Buscar cualquier palabra que comience con la raíz
        if len(raiz) >= 3: 
            pattern_raiz = re.compile(r'\b' + re.escape(raiz) + r'\w*\b', re.IGNORECASE)
            matches = pattern_raiz.findall(frase)
            if matches:
                variacion = matches[0]
                logger.info(f"Encontrada variación: '{variacion}' de '{modismo}'")
                pattern_var = re.compile(r'\b' + re.escape(variacion) + r'\b', re.IGNORECASE)
                def reemplazo_var(m):
                    return mantener_caso(m.group(), significado)
                frase = pattern_var.sub(reemplazo_var, frase)
                return frase
        
        # Estrategia 3: Búsqueda más flexible - palabras que contengan la mayor parte del modismo
        if len(modismo) >= 5:
            min_length = int(len(modismo) * 0.7)
            patron_flexible = re.escape(modismo[:min_length])
            pattern_flexible = re.compile(r'\b' + patron_flexible + r'\w*\b', re.IGNORECASE)
            matches = pattern_flexible.findall(frase)
            if matches:
                variacion = matches[0]
                logger.info(f"Encontrada (búsqueda flexible): '{variacion}' de '{modismo}'")
                pattern_var = re.compile(r'\b' + re.escape(variacion) + r'\b', re.IGNORECASE)
                def reemplazo_var(m):
                    return mantener_caso(m.group(), significado)
                frase = pattern_var.sub(reemplazo_var, frase)
                return frase
        
        # Si no se encontró nada, devolver la frase sin cambios
        logger.warning(f"✗ No se encontró '{modismo}' ni variaciones en la frase")
        return frase

    def detectar_cambios(self, original: str, neutralizada: str) -> list:
        """
        Compara palabra por palabra y retorna las palabras cambiadas con sus
        posiciones exactas (índices de caracteres) en la frase neutralizada.
        """
        # Tokenizar manteniendo las posiciones
        def tokenizar_con_posiciones(texto):
            tokens = []
            for match in re.finditer(r'\w+|[^\w\s]', texto, re.UNICODE):
                tokens.append({
                    'palabra': match.group(),
                    'inicio': match.start(),
                    'fin': match.end()
                })
            return tokens
        
        tokens_original = [t['palabra'] for t in tokenizar_con_posiciones(original)]
        tokens_neutralizada_con_pos = tokenizar_con_posiciones(neutralizada)
        tokens_neutralizada = [t['palabra'] for t in tokens_neutralizada_con_pos]
        
        # Usar SequenceMatcher para alinear las diferencias
        matcher = SequenceMatcher(None, tokens_original, tokens_neutralizada)
        cambios = []
        indices_ya_agregados = set()
        
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'replace':
                # Agregar todas las palabras nuevas del reemplazo con sus posiciones
                for idx in range(j1, j2):
                    if idx not in indices_ya_agregados:
                        token_info = tokens_neutralizada_con_pos[idx]
                        cambios.append({
                            'palabra': token_info['palabra'],
                            'indice_inicio': token_info['inicio'],
                            'indice_fin': token_info['fin']
                        })
                        indices_ya_agregados.add(idx)
                        logger.info(f"Cambio: '{token_info['palabra']}' en [{token_info['inicio']}:{token_info['fin']}]")
            
            elif tag == 'insert':
                # Agregar palabras insertadas con sus posiciones
                for idx in range(j1, j2):
                    if idx not in indices_ya_agregados:
                        token_info = tokens_neutralizada_con_pos[idx]
                        cambios.append({
                            'palabra': token_info['palabra'],
                            'indice_inicio': token_info['inicio'],
                            'indice_fin': token_info['fin']
                        })
                        indices_ya_agregados.add(idx)
                        logger.info(f"Inserción: '{token_info['palabra']}' en [{token_info['inicio']}:{token_info['fin']}]")
        
        return cambios

    async def neutralizar(self, frase: str, significado: dict) -> tuple[str, list]:
        """
        Retorna (frase_neutralizada, lista_de_cambios_con_posiciones)
        """
        if not significado or not isinstance(significado, dict):
            logger.warning("Sin significados proporcionados, retornando frase original")
            return frase, []
        
        # Paso 1: Reemplazar TODOS los modismos manualmente
        frase_modificada = frase
        reemplazos_realizados = []
        
        for modismo, significado_str in significado.items():
            frase_antes = frase_modificada
            frase_modificada = self.reemplazar_modismo_manual(
                frase_modificada, modismo, significado_str
            )
            
            # Verificar si realmente se hizo un cambio
            if frase_antes != frase_modificada:
                reemplazos_realizados.append(f"{modismo}→{significado_str}")
                logger.info(f"✓ Reemplazado: {modismo} → {significado_str}")
            else:
                logger.warning(f"✗ No encontrado: {modismo}")
        
        # Si no se hizo ningún reemplazo, devolver original
        if not reemplazos_realizados:
            logger.warning("Ningún modismo pudo ser reemplazado")
            return frase, []
        
        logger.info(f"Frase con reemplazos: {frase_modificada}")
        
        # Paso 2: Ajustar gramática usando el modelo remoto
        frase_final = await self.model_client.corregir_gramatica(frase_modificada)
        logger.info(f"Frase final corregida: {frase_final}")
        
        # Paso 3: Detectar palabras que cambiaron con sus posiciones exactas
        cambios = self.detectar_cambios(frase, frase_final)
        
        logger.info(f"Total de palabras modificadas: {len(cambios)}")
        
        return frase_final, cambios