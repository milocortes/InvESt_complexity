# Medidas de Complejidad

## Proximidad
Formally, the proximity \\( \phi\\) between products \\(i\\) and \\(j\\) is the minimum of the pairwise conditional probabilities of a country exporting a good given that it exports another.


\\[ 
    \begin{equation}
        \phi_{i,j} = \min \big\lbrace P(RCAx_i|RCAx_j),P(RCAx_j|RCAx_i) \big\rbrace 
    \end{equation}    
\\]

Where RCA stands for revealed comparative advantage:

\\[ 
    \begin{equation}
        RCA_{c,i} =\dfrac{x(c,i)}{\sum_i x(c,i)} \Bigg/  \dfrac{\sum_c x(c,i)}{\sum_{c,i} x(c,i)}
    \end{equation}
\\]

which measures whether a country \\( c\\) exports more of a good \\( i\\), as a share of its total exports, than the "average" country (\\( RCA>1\\) not \\(RCA<1\\)).

## Distancia
\\[
\begin{equation}
    d_{cp} = \dfrac{\sum_{p'}(1-M_{cp'}) \phi_{pp'}}{\sum_{p'} \phi_{pp'}}
\end{equation}
\\]

## Similaridad de insumos y productos
Siendo \\(Z\\) la matriz de flujo entre sectores y \\(X\\) es el vector de producto total, la matriz de coeficientes técnicos se calcularía como:

\\[
A= Z \cdot (X \cdot I)^{-1}
\\]

Las entradas de la matriz \\(A\\) definen los coeficientes técnicos como la proporción de insumo ofrecido por el sector \\(i\\) y comprado por el sector \\(j\\) con respecto al producto total del sector \\(j\\), \\(a_{ij}= \dfrac{z_{ij}}{x_j}\\).

La similaridad entre insumos utilizados por las industrias se calcularía como:
\\[
\begin{equation}
    \text{presencia de insumos}_{us} = \dfrac{\sum_{s'}M_{us'} A^{T}_{ss'}}{\sum_{s'} A^{T}_{ss'}}
\end{equation}
\\]


\\[
\frac{\sum_{s'}M_{us'} A^{T}_{ss'}} {\sum_2}
\\]
La similaridad entre productos utilizados por otras industrias se calcularía como:

\\[
\begin{equation}
    \text{presencia de productos}_{us} = \dfrac{\sum_{s'}M_{us'} A_{ss'}}{\sum_{s'} A_{ss'}}
\end{equation}
\\]