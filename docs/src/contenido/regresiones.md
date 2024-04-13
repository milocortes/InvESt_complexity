# Regresiones para Crecimiento del RCA, Apariciones y Desapariciones

Con el objetivo de ofrecer evidencia empírica sobre la trayectoria de dependencia de la evolución industrial para el conjunto de Zonas Metropolitanas y El Salvador, se estimaron regresiones para tres variables explicaticas:

* **Crecimiento del RCA** : variable continua igual a la inversa hiperbólica de la tasa de crecimiento del RCA entre 2015 y 2020. 
* **Aparición de industrias**:  variable dicotómica que toma la etiqueta 1 si la industria tenía un RCA < 0.05 en 2015 y un RCA > 0.2 en 2020. En caso contrario, se asigna la etiqueta 0. La variable indica si la actividad se especializó en el periodo.
* **Desaparición de industrias** : variable dicotómica que toma la etiqueta 1 si la industria tenía un RCA < 0.2 en 2015 y un RCA > 0.05 en 2020. En caso contrario, se asigna la etiqueta 0. La variable indica si la actividad perdió especialización en el periodo.

Las regresiones toman la siguiente forma funcional:

\\[
\begin{equation}
    y_{j,k,t_1} = \alpha_0 + \alpha_1 Densidad_{j,k,t_0} + \alpha_2RCA_{j,k,t_0} + \delta_1 ZM + \delta_2 CIIU+\varepsilon_{j,k,t_1}
\end{equation}
\\]

Donde el subíndice \\(j\\) corresponde a la actividad CIIU, \\(k\\) corresponde a la zona metropolitana, \\(t_0\\) corresponde al año de inicio del periodo de estudio(2015), \\(t_1\\) corresponde al año final del periodo de estudio (2020). La estimación controla por efectos fijos para zonas metropolitanas (ZM) y actividades CIIU (CIIU). 

Para examinar el efecto de las métricas de viabilidad en la trayectoria de evolución industrial, a la forma funcional anterior agregamos como regresores las metricas de viabilidad:

* **Input Presence** : mide la presencia de actividades que producen insumos necesarios para las actividades.
* **Output Presence** : mide la presencia de actividades que compran productos de las actividades.
* **Input Presence Similarity** : mide la presencia de actividades que son similares respecto a la demanda de mismos insumos.
* **Output Presence Similarity** : mide la presencia de actividades similares respecto a si le venden sus producción a las mismas industrias. 
* **Co-empleo** :  mide la presencia de actividades que demandan los mismos tipos de ocupaciones.

## Crecimiento del RCA
La siguiente tabla muestra lo resultados para las regresiones de crecimiento del RCA. En todos los casos, el RCA fue estadísticamente significativo y negativo. El signo del coeficiento es el esperado, pues industrias con un alto RCA se espera que crezcan menos. Sólo para una especificación resultaron significativos los regresores de densidad y presencia de actividades similares respecto a si le venden sus producción a las mismas industrias. Para las regresiones donde se incorporó la medida de co-empleo, resultó significativa y negativa, lo cual da evidencia que existe una competencia por recursos humanos entre las industrias que demandan los mismos tipos de ocupaciones. 


{{#include regresiones/rca_reg.html}}


## Aparición de industrias
La siguiente tabla muestra lo resultados para las regresiones de Apariciones de industrias. En todos los casos, la Densidad resultó significativa y positiva, como es lo esperado en la literatura. Sin embargo, la densidad no es el único determinante de la evolución industrial regional. Las regresiones calculadas muestran que Output Presence Similarity y Co-empleo tienen un efecto positivo y significativo sobre las apariciones. Es decir, el incremento de actividades que son clientes de la producción de las actividades, la cual podemos pensarla como un efecto positivo del lado de la demanda local, incrementa la aparición de industrias. Por otro lado, el incremento de actividades que demandan los mismos tipos de ocupaciones influyen de forma positiva en la aparición de industrias. 


{{#include regresiones/apariciones_reg.html}}

## Desaparición de industrias
La siguiente tabla muestra lo resultados para las regresiones de Desapariciones de industrias. En todos los casos, la Densidad resultó significativa y negativa, como es lo esperado en la literatura. En este caso, sólo Input Presence Similarity resultó significativa y con signo negativo. Esta medida puede pensarse como indicadora de restricciones a la oferta local de insumos. Si se incrementan las actividades que demandan los mismos insumos que otras actividades,  la especialización se reduce. Esto puede pensarse que hay un efecto negativo de la competencia por insumos lo cual deja a algunas industrias fuera del acceso a la oferta local de insumos. Si no hay acceso a mercados internacionales, se traduce en una pérdida de especialización.

{{#include regresiones/desapariciones_reg.html}}
