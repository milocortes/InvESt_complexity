################# Cargamos las biblioecas necesarias ####################3
library(questionr)
library(survey)
library(ggplot2)

###############################################
### Definimos una ruta temporal para guardar los microdatos
temporal <- tempfile()
download.file("https://www.inegi.org.mx/contenidos/programas/enoe/15ymas/microdatos/enoe_n_2021_trim4_csv.zip",temporal)
files = unzip(temporal, list=TRUE)$Name
files_lower <- tolower(files)
sdemt_file_name <- files[grepl("sdemt", tolower(files_lower))]
coe1_file_name <- files[grepl("coe1", tolower(files_lower))]
unzip(temporal, files=files[grepl("csv",files)])

sdemt <- read.csv(sdemt_file_name)
coe1 <- read.csv(coe1_file_name)

sdemt$folio <- paste(sdemt$cd_a, sdemt$ent, sdemt$con, sdemt$v_sel, sdemt$n_hog, sdemt$h_mud, sdemt$n_ren)
coe1$folio<- paste(coe1$cd_a, coe1$ent, coe1$con, coe1$v_sel, coe1$n_hog,coe1$h_mud, coe1$n_ren)

enoetotal <- merge(sdemt[,c("folio", "clase2", "eda", "r_def", "c_res", "upm", "est_d_tri", "fac_tri")], coe1[,c("folio", "p4a", "p3")], by="folio")

# Se selecciona la población de referencia que es: población ocupada mayor de 15 años con entrevista completa y condición de residencia válida.
enoetotal <- subset(enoetotal, enoetotal$clase2 == 1 & enoetotal$eda>=15 & enoetotal$eda<=98 & enoetotal$r_def==0 & (enoetotal$c_res==1 | enoetotal$c_res==3))
rm(c("sdemt", "coe1"))

# Definimos el esquema de muestreo
sdemtdesign<-svydesign(id=~upm, strata=~est_d_tri, weight=~fac_tri, data=enoetotal, nest=TRUE)
options(survey.lonely.psu="adjust")

## Empleo por tipo de ocupación
contingencia <- svytable(~p4a+p3, sdemtdesign)

### RECURSO
### https://stats.oarc.ucla.edu/r/seminars/survey-data-analysis-with-r/