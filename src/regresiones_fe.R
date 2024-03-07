library(stargazer)
library(lfe)
library(IDPmisc)

library(fixest)
library(modelsummary)

#install.packages(c("stargazer", "lfe", "IDPmisc"))
#PATH <- r"(C:\Users\hermi\OneDrive\Documents\BID\articulo_complexity\articulo\output)"
PATH <- "/home/milo/Documents/egap/iniciativas/desarrollo-regional/el_salvador/datos/src"
complexity_zm = read.csv(file.path(PATH, "regresiones_crecimiento.csv"))


growth_rca_log = felm(growth_rca_log ~ arcsinh_density + arcsinh_rca  | edo + actividad, data = NaRV.omit(complexity_zm), cmethod = 'cgm2', exactDOF=TRUE)
growth_rca_arcsinh = felm(growth_rca_arcsinh ~ arcsinh_density  + arcsinh_rca | edo + actividad, data = NaRV.omit(complexity_zm), cmethod = 'cgm2', exactDOF=TRUE)
apariciones = felm(apariciones ~ arcsinh_density  + arcsinh_rca | edo + actividad, data = NaRV.omit(complexity_zm), cmethod = 'cgm2', exactDOF=TRUE)
desapariciones = felm(desapariciones ~ arcsinh_density  + arcsinh_rca | edo + actividad, data = NaRV.omit(complexity_zm), cmethod = 'cgm2', exactDOF=TRUE)


stargazer(growth_rca_log, growth_rca_arcsinh, apariciones, desapariciones, 
          type="text", 
          title = "Regresiones (2020-2015)")


### Agregamos similaridad de insumos y productos


#diff_rca_log = felm(diff_rca_log ~ arcsinh_density + arcsinh_rca  + arcsinh_output_presence+ arcsinh_input_presence | edo + actividad, data = NaRV.omit(complexity_zm[, c("diff_rca_log", "arcsinh_density", "arcsinh_rca", "arcsinh_output_presence", "arcsinh_input_presence", "edo", "actividad")]), cmethod = 'cgm2', exactDOF=TRUE)
#diff_rca_arcsinh = felm(diff_rca_arcsinh ~ arcsinh_density  + arcsinh_rca + arcsinh_output_presence+ arcsinh_input_presence| edo + actividad, data = NaRV.omit(complexity_zm[, c("diff_rca_arcsinh", "arcsinh_density", "arcsinh_rca", "arcsinh_output_presence", "arcsinh_input_presence", "edo", "actividad")]), cmethod = 'cgm2', exactDOF=TRUE)
growth_rca_log = felm(growth_rca_log ~ arcsinh_density + arcsinh_rca  + arcsinh_output_presence+ arcsinh_input_presence | edo + actividad, data = NaRV.omit(complexity_zm[, c("growth_rca_log", "arcsinh_density", "arcsinh_rca", "arcsinh_output_presence", "arcsinh_input_presence", "edo", "actividad")]), cmethod = 'cgm2', exactDOF=TRUE)
growth_rca_arcsinh = felm(growth_rca_arcsinh ~ arcsinh_density  + arcsinh_rca + arcsinh_output_presence+ arcsinh_input_presence| edo + actividad, data = NaRV.omit(complexity_zm[, c("growth_rca_arcsinh", "arcsinh_density", "arcsinh_rca", "arcsinh_output_presence", "arcsinh_input_presence", "edo", "actividad")]), cmethod = 'cgm2', exactDOF=TRUE)
apariciones = felm(apariciones ~ arcsinh_density  + arcsinh_rca + arcsinh_output_presence+ arcsinh_input_presence| edo + actividad, data = NaRV.omit(subset(complexity_zm[, c("apariciones", "arcsinh_density", "arcsinh_rca", "arcsinh_output_presence", "arcsinh_input_presence", "edo", "actividad", "rca_2015")], rca_2015 < 0.05)), cmethod = 'cgm2', exactDOF=TRUE)
desapariciones = felm(desapariciones ~ arcsinh_density  + arcsinh_rca + arcsinh_output_presence+ arcsinh_input_presence| edo + actividad, data = NaRV.omit(subset(complexity_zm[, c("desapariciones", "arcsinh_density", "arcsinh_rca", "arcsinh_output_presence", "arcsinh_input_presence", "edo", "actividad", "rca_2015")], rca_2015 > 0.2)), cmethod = 'cgm2', exactDOF=TRUE)


stargazer(growth_rca_log, growth_rca_arcsinh, apariciones, desapariciones, 
          type="text", 
          title = "Regresiones (2019-2013)")

### Agregamos similaridad de coempleo


#diff_rca_log = felm(diff_rca_log ~ arcsinh_density + arcsinh_rca  + arcsinh_output_presence+ arcsinh_input_presence | edo + actividad, data = NaRV.omit(complexity_zm[, c("diff_rca_log", "arcsinh_density", "arcsinh_rca", "arcsinh_output_presence", "arcsinh_input_presence", "edo", "actividad")]), cmethod = 'cgm2', exactDOF=TRUE)
#diff_rca_arcsinh = felm(diff_rca_arcsinh ~ arcsinh_density  + arcsinh_rca + arcsinh_output_presence+ arcsinh_input_presence| edo + actividad, data = NaRV.omit(complexity_zm[, c("diff_rca_arcsinh", "arcsinh_density", "arcsinh_rca", "arcsinh_output_presence", "arcsinh_input_presence", "edo", "actividad")]), cmethod = 'cgm2', exactDOF=TRUE)
growth_rca_log = felm(growth_rca_log ~ arcsinh_density + arcsinh_rca  + arcsinh_output_presence+ arcsinh_input_presence + log_coempleo_presence| edo + actividad, data = NaRV.omit(complexity_zm[, c("growth_rca_log", "arcsinh_density", "arcsinh_rca", "arcsinh_output_presence", "arcsinh_input_presence", "log_coempleo_presence", "edo", "actividad")]), cmethod = 'cgm2', exactDOF=TRUE)
growth_rca_arcsinh = felm(growth_rca_arcsinh ~ arcsinh_density  + arcsinh_rca + arcsinh_output_presence+ arcsinh_input_presence + log_coempleo_presence| edo + actividad, data = NaRV.omit(complexity_zm[, c("growth_rca_arcsinh", "arcsinh_density", "arcsinh_rca", "arcsinh_output_presence", "arcsinh_input_presence", "log_coempleo_presence", "edo", "actividad")]), cmethod = 'cgm2', exactDOF=TRUE)
apariciones = felm(apariciones ~ arcsinh_density  + arcsinh_rca + arcsinh_output_presence+ arcsinh_input_presence + log_coempleo_presence| edo + actividad, data = NaRV.omit(subset(complexity_zm[, c("apariciones", "arcsinh_density", "arcsinh_rca", "arcsinh_output_presence", "arcsinh_input_presence", "log_coempleo_presence", "edo", "actividad", "rca_2015")], rca_2015 < 0.05)), cmethod = 'cgm2', exactDOF=TRUE)
desapariciones = felm(desapariciones ~ arcsinh_density  + arcsinh_rca + arcsinh_output_presence+ arcsinh_input_presence + log_coempleo_presence| edo + actividad, data = NaRV.omit(subset(complexity_zm[, c("desapariciones", "arcsinh_density", "arcsinh_rca", "arcsinh_output_presence", "arcsinh_input_presence", "log_coempleo_presence", "edo", "actividad", "rca_2015")], rca_2015 > 0.2)), cmethod = 'cgm2', exactDOF=TRUE)


stargazer(growth_rca_log, growth_rca_arcsinh, apariciones, desapariciones, 
          type="text", 
          title = "Regresiones (2019-2013)")

### Agregamos similaridad de coempleo version continua

#diff_rca_log = felm(diff_rca_log ~ arcsinh_density + arcsinh_rca  + arcsinh_output_presence+ arcsinh_input_presence | edo + actividad, data = NaRV.omit(complexity_zm[, c("diff_rca_log", "arcsinh_density", "arcsinh_rca", "arcsinh_output_presence", "arcsinh_input_presence", "edo", "actividad")]), cmethod = 'cgm2', exactDOF=TRUE)
#diff_rca_arcsinh = felm(diff_rca_arcsinh ~ arcsinh_density  + arcsinh_rca + arcsinh_output_presence+ arcsinh_input_presence| edo + actividad, data = NaRV.omit(complexity_zm[, c("diff_rca_arcsinh", "arcsinh_density", "arcsinh_rca", "arcsinh_output_presence", "arcsinh_input_presence", "edo", "actividad")]), cmethod = 'cgm2', exactDOF=TRUE)
growth_rca_log = felm(growth_rca_log ~ arcsinh_density + arcsinh_rca  + arcsinh_output_presence+ arcsinh_input_presence + arcsinh_coempleo_presence_continua| edo + actividad, data = NaRV.omit(complexity_zm[, c("growth_rca_log", "arcsinh_density", "arcsinh_rca", "arcsinh_output_presence", "arcsinh_input_presence", "arcsinh_coempleo_presence_continua", "edo", "actividad")]), cmethod = 'cgm2', exactDOF=TRUE)
growth_rca_arcsinh = felm(growth_rca_arcsinh ~ arcsinh_density  + arcsinh_rca + arcsinh_output_presence+ arcsinh_input_presence + arcsinh_coempleo_presence_continua| edo + actividad, data = NaRV.omit(complexity_zm[, c("growth_rca_arcsinh", "arcsinh_density", "arcsinh_rca", "arcsinh_output_presence", "arcsinh_input_presence", "arcsinh_coempleo_presence_continua", "edo", "actividad")]), cmethod = 'cgm2', exactDOF=TRUE)
apariciones = felm(apariciones ~ arcsinh_density  + arcsinh_rca + arcsinh_output_presence+ arcsinh_input_presence + arcsinh_coempleo_presence_continua| edo + actividad, data = NaRV.omit(subset(complexity_zm[, c("apariciones", "arcsinh_density", "arcsinh_rca", "arcsinh_output_presence", "arcsinh_input_presence", "arcsinh_coempleo_presence_continua", "edo", "actividad", "rca_2015")], rca_2015 < 0.05)), cmethod = 'cgm2', exactDOF=TRUE)
desapariciones = felm(desapariciones ~ arcsinh_density  + arcsinh_rca + arcsinh_output_presence+ arcsinh_input_presence + arcsinh_coempleo_presence_continua| edo + actividad, data = NaRV.omit(subset(complexity_zm[, c("desapariciones", "arcsinh_density", "arcsinh_rca", "arcsinh_output_presence", "arcsinh_input_presence", "arcsinh_coempleo_presence_continua", "edo", "actividad", "rca_2015")], rca_2015 > 0.2)), cmethod = 'cgm2', exactDOF=TRUE)


stargazer(growth_rca_log, growth_rca_arcsinh, apariciones, desapariciones, 
          type="text", 
          title = "Regresiones (2019-2013)")

### Agregamos input-output presence similarity 

#diff_rca_log = felm(diff_rca_log ~ arcsinh_density + arcsinh_rca  + arcsinh_output_presence+ arcsinh_input_presence | edo + actividad, data = NaRV.omit(complexity_zm[, c("diff_rca_log", "arcsinh_density", "arcsinh_rca", "arcsinh_output_presence", "arcsinh_input_presence", "edo", "actividad")]), cmethod = 'cgm2', exactDOF=TRUE)
#diff_rca_arcsinh = felm(diff_rca_arcsinh ~ arcsinh_density  + arcsinh_rca + arcsinh_output_presence+ arcsinh_input_presence| edo + actividad, data = NaRV.omit(complexity_zm[, c("diff_rca_arcsinh", "arcsinh_density", "arcsinh_rca", "arcsinh_output_presence", "arcsinh_input_presence", "edo", "actividad")]), cmethod = 'cgm2', exactDOF=TRUE)
growth_rca_log = felm(growth_rca_log ~ arcsinh_density + arcsinh_rca  + arcsinh_output_presence+ arcsinh_input_presence + arcsinh_coempleo_presence_continua + arcsinh_input_presence_similarity + arcsinh_output_presence_similarity| edo + actividad, data = NaRV.omit(complexity_zm[, c("growth_rca_log", "arcsinh_density", "arcsinh_rca", "arcsinh_output_presence", "arcsinh_input_presence", "arcsinh_coempleo_presence_continua", "edo", "actividad", "arcsinh_input_presence_similarity", "arcsinh_output_presence_similarity")]), cmethod = 'cgm2', exactDOF=TRUE)
growth_rca_arcsinh = felm(growth_rca_arcsinh ~ arcsinh_density  + arcsinh_rca + arcsinh_output_presence+ arcsinh_input_presence + arcsinh_coempleo_presence_continua + arcsinh_input_presence_similarity + arcsinh_output_presence_similarity| edo + actividad, data = NaRV.omit(complexity_zm[, c("growth_rca_arcsinh", "arcsinh_density", "arcsinh_rca", "arcsinh_output_presence", "arcsinh_input_presence", "arcsinh_coempleo_presence_continua", "edo", "actividad", "arcsinh_input_presence_similarity", "arcsinh_output_presence_similarity")]), cmethod = 'cgm2', exactDOF=TRUE)
apariciones = felm(apariciones ~ arcsinh_density  + arcsinh_rca + arcsinh_output_presence+ arcsinh_input_presence + arcsinh_coempleo_presence_continua + arcsinh_input_presence_similarity + arcsinh_output_presence_similarity| edo + actividad, data = NaRV.omit(subset(complexity_zm[, c("apariciones", "arcsinh_density", "arcsinh_rca", "arcsinh_output_presence", "arcsinh_input_presence", "arcsinh_coempleo_presence_continua", "edo", "actividad", "rca_2015", "arcsinh_input_presence_similarity", "arcsinh_output_presence_similarity")], rca_2015 < 0.05)), cmethod = 'cgm2', exactDOF=TRUE)
desapariciones = felm(desapariciones ~ arcsinh_density  + arcsinh_rca + arcsinh_output_presence+ arcsinh_input_presence + arcsinh_coempleo_presence_continua + arcsinh_input_presence_similarity + arcsinh_output_presence_similarity| edo + actividad, data = NaRV.omit(subset(complexity_zm[, c("desapariciones", "arcsinh_density", "arcsinh_rca", "arcsinh_output_presence", "arcsinh_input_presence", "arcsinh_coempleo_presence_continua", "edo", "actividad", "rca_2015", "arcsinh_input_presence_similarity", "arcsinh_output_presence_similarity")], rca_2015 > 0.2)), cmethod = 'cgm2', exactDOF=TRUE)


stargazer(growth_rca_log, growth_rca_arcsinh, apariciones, desapariciones, 
          type="text", 
          title = "Regresiones (2019-2013)")

### Con fixest

growth_rca_log = feols(growth_rca_log ~ arcsinh_density + arcsinh_rca  + arcsinh_output_presence+ arcsinh_input_presence + arcsinh_coempleo_presence_continua| edo + actividad, complexity_zm)
growth_rca_arcsinh = feols(growth_rca_arcsinh ~ arcsinh_density + arcsinh_rca  + arcsinh_output_presence+ arcsinh_input_presence + arcsinh_coempleo_presence_continua| edo + actividad, complexity_zm)
apariciones = feglm(apariciones ~ arcsinh_density + arcsinh_rca  + arcsinh_output_presence+ arcsinh_input_presence + arcsinh_coempleo_presence_continua| edo + actividad, data = subset(complexity_zm, rca_2015 < 0.05), family = "logit")
desapariciones = feglm(desapariciones ~ arcsinh_density + arcsinh_rca  + arcsinh_output_presence+ arcsinh_input_presence + arcsinh_coempleo_presence_continua| edo + actividad, data = subset(complexity_zm, rca_2015 > 0.2), family = "logit")

modelsummary(growth_rca_log, growth_rca_arcsinh, apariciones, desapariciones)

stargazer(growth_rca_log, 
          type="text", 
          title = "Regresiones (2019-2013)")
