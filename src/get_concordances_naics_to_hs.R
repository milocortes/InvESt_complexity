library(concordance)

setwd("/home/milo/Documents/egtp/iniciativas/InvESt_complexity/src")

ciiu_naics <- read.csv("ciiu_naics_slv_cw.csv")


acumula_df <- data.frame()

test_concordance <- function(naics) { 
  
  consulta <- concord(sourcevar = c(naics ),origin = "NAICS", destination = "HS", dest.digit = 6, all = TRUE)
  
  prueba <- data.frame(consulta)[,1]

  if (all(is.na(prueba))){
    return(NA)
  }else {
    return(consulta)     
  }
} 


for (naics_original in ciiu_naics$naics_2017){
    
    valor <- 0
    naics_original <- as.character(naics_original)
    naics <- naics_original

    print(paste("Intentando", naics_original))

    while(valor ==0){
        data <- test_concordance(naics)
        
        if(is.na(data)){
            naics <<- substr(naics, 1, nchar(naics)-2)

            if(length(naics == 0)){
                data <- data.frame(hs = NA, weigth = NA)
                valor <<- 1
            }else{
                print(paste("Reintentemos con", naics))
                valor <<- 0
            }

        }else{
            print("Exito!!")
            valor <<- 1
        }
    }

    consulta <- data.frame(data)
    colnames(consulta) <- c("hs", "weight")
    consulta$naics <- naics
    consulta$naics_original <- naics_original

    acumula_df <- rbind.data.frame(acumula_df, consulta)
}

write.csv(acumula_df, file = "naics_2017_to_hs.csv", row.names = FALSE)


