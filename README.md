# Análisis de complejidad del Proyecto InvESt-Tec Monterrey

Este repositorio contiene los programas utilizados para:
 
* Identificación de industrias estratégicas en el margen extensivo:
    - Armonización de Sistemas de Clasificación Industrial.
        + [CIIU-SCIAN 2018-NAICS 2017](datos/cws/empleo/ciiu-recodificacion-dario-diodato/src/build_recodificacion_ciiu-rev-4_scian.py)
        + [Construcción de nueva clasificación agrupando sectores (CIIU Recodificado)](datos/cws/empleo/ciiu-recodificacion-dario-diodato/src/nueva_clasificacion_ciiu.py)
    - Construcción de datos de empleo en distintas clasificaciones:
        + [USA (NAICS 2017-CIIU Recod)](datos/empleo/USA/src/procesa_empleo_usa_cbp.py)
        + [México (IMSS-SCIAN2018-CIIU Recod)](datos/empleo/MEX/src/procesa_empleo_mx_imss.py)
        + [El Salvador (CIIU-CIIU Recod)](datos/empleo/SLV/src/procesa_empleo_slv_seguridad_social.py)
    - [Catálogo de industrias transables](datos/diccionarios/traded_clusters_appendix/src/get_tradables_activities.py)
* Proceso de identificación de industrias clave en el margen extensivo:
    - [Cálculo de Medidas de Complejidad](src/build_complexity_measures.py)
    - [Preparación de datos para utilizar el método de toma de selección multicriterio TOPSI](src/prepara_multicriterio.py)
    - [Cálculo del ranking de priorización con el método de toma de selección multicriterio TOPSI](src/multicriterio_sectores.jl)
* Cálculo de Factores de Viabilidad:
    - [Recodificación de Matriz Insumo Producto de México 2018 en clasificación CIIU Recodificado](datos/mip/MEX/src/mip_desagrega_ciiu.py)
    - [Relación Directa de Insumos](src/build_complexity_measures.py)
    - [Relación Directa de Productos](src/build_complexity_measures.py)
    - [Similitud de Industrias Proveedoras](src/build_complexity_measures.py)
    - [Similitud de Industrias Compradoras](src/build_complexity_measures.py)
    - [Relación Directa de Ocupaciones](src/build_complexity_measures.py)
    - [Medida de requerimientos de trabajo calificado por industria](datos/tipo_empleo/USA/src/onet.py)
    - [Rankeo de industrias por Skills](datos/tipo_empleo/USA/src/rankea_skills_agregado.py)
    - [Rankeo de industrias por Abilities](datos/tipo_empleo/USA/src/rankea_abilities_agregado.py)
    - [Rankeo de industrias por Knowledge](datos/tipo_empleo/USA/src/rankea_knowledge_agregado.py)
* [Regresiones para Crecimiento del RCA, Apariciones y Desapariciones](src/regresiones_fe.jl)