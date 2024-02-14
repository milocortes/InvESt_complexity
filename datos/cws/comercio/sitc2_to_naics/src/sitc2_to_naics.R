library(concordance)
library(tidyverse)


# Definimos las rutas donde se encuentran los datos
DATA_PATH <- "/home/milo/Documents/egap/iniciativas/desarrollo-regional/el_salvador/datos/datos/cws/empleo/ciiu-recodificacion-dario-diodato/output"
DATA_FILE_PATH <- file.path(DATA_PATH, "ciiu_recodificado_naics_2017.csv")

OUTPUT_PATH <- "/home/milo/Documents/egap/iniciativas/desarrollo-regional/el_salvador/datos/datos/cws/comercio/sitc2_to_naics/output"
OUTPUT_FILE_PATH <- file.path(OUTPUT_PATH, "sitc-2_to_naics-2017.csv")

# Cargamos los datos
ciiu_naics <- read.csv(DATA_FILE_PATH)

# Ejecutamos la función para cada par de correspondencias ciiu-naics
# Guardamos la información en un dataframe

df_corr_completo <- data.frame()

for (i in 1:nrow(ciiu_naics)){
    ciiu <- as.character(ciiu_naics[i,"ciiu"])
    naics <- as.character(ciiu_naics[i,"naics_2017"])
    print(paste("Registro ", i, " de ", nrow(ciiu_naics)))
    for (code_len in 2:5){

        try({
        correspondencia <- concord_sitc_naics(sourcevar = naics,
                   origin = "NAICS", destination = "SITC2",
                   dest.digit = code_len, all = TRUE)

        n_rep = length(correspondencia[[naics]]$match)

        df_corr <- data.frame(ciiu = rep(ciiu, times = n_rep), 
                              naics_2017 = rep(naics, times = n_rep), 
                              dest_digit = rep(code_len, times = n_rep), 
                              sitc2 = correspondencia[[naics]]$match, 
                              sitc2_weights= correspondencia[[naics]]$weight)
        df_corr_completo <- rbind.data.frame(df_corr_completo, df_corr)
        })

    }

}

# Eliminamos los datos faltantes (NAN)
df_corr_completo <- df_corr_completo %>% drop_na()

write.csv(df_corr_completo, OUTPUT_FILE_PATH, row.names = FALSE)

