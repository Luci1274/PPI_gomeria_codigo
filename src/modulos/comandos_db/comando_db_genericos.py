import re


class GenericosDB:
    """Utilidades compartidas para consultas y normalización de datos."""

    _IDENTIFICADOR_SQL = re.compile(
        r"^[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)?$"
    )

    @staticmethod
    def normalizar_texto(valor, estilo=None, predeterminado=""):
        if valor is None:
            return predeterminado
        if not isinstance(valor, str):
            raise TypeError("El valor a normalizar debe ser texto o None.")

        texto = valor.strip()
        if not texto:
            return predeterminado
        if estilo == "titulo":
            return texto.title()
        if estilo == "minusculas":
            return texto.lower()
        if estilo is not None:
            raise ValueError(f"Estilo de normalización no soportado: {estilo}")
        return texto

    @classmethod
    def agregar_filtro_busqueda(cls, condiciones, parametros, columnas, termino):
        termino = cls.normalizar_texto(termino)
        if not termino:
            return
        if not columnas:
            raise ValueError("La búsqueda requiere al menos una columna.")

        columnas_sql = [cls._identificador_sql(columna) for columna in columnas]
        condiciones.append(
            "(" + " OR ".join(f"{columna} LIKE %s" for columna in columnas_sql) + ")"
        )
        parametros.extend([f"%{termino}%"] * len(columnas_sql))

    @staticmethod
    def construir_where(condiciones):
        return " WHERE " + " AND ".join(condiciones) if condiciones else ""

    @classmethod
    def existe_registro(
        cls, cursor, tabla, criterios, columnas_normalizadas=()
    ):
        if not criterios:
            raise ValueError("La comprobación de duplicados requiere criterios.")

        tabla_sql = cls._identificador_sql(tabla)
        normalizadas = set(columnas_normalizadas)
        if not normalizadas.issubset(criterios):
            raise ValueError("Las columnas normalizadas deben estar entre los criterios.")

        condiciones = []
        parametros = []
        for columna, valor in criterios.items():
            columna_sql = cls._identificador_sql(columna)
            if columna in normalizadas:
                condiciones.append(
                    f"LOWER(TRIM(COALESCE({columna_sql}, ''))) = LOWER(%s)"
                )
                parametros.append(valor or "")
            elif valor is None:
                condiciones.append(f"{columna_sql} IS NULL")
            else:
                condiciones.append(f"{columna_sql} = %s")
                parametros.append(valor)

        cursor.execute(
            f"SELECT 1 FROM {tabla_sql} WHERE "
            + " AND ".join(condiciones)
            + " LIMIT 1",
            parametros,
        )
        return cursor.fetchone() is not None

    @classmethod
    def _identificador_sql(cls, identificador):
        if not isinstance(identificador, str) or not cls._IDENTIFICADOR_SQL.fullmatch(
            identificador
        ):
            raise ValueError(f"Identificador SQL no válido: {identificador!r}")
        return ".".join(f"`{parte}`" for parte in identificador.split("."))