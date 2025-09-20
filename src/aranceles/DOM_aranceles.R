# Libraries
library(ggplot2)
library(dplyr)
#library(hrbrthemes)
library(viridis)
library(ggrepel)

setwd("/home/milo/Documents/egtp/iniciativas/InvESt_complexity/src/aranceles/output")

## Cargamos datos HS2
df_hs_2d = read.csv("hs2_asia_shares_extensivo_intensivo.csv")
df_hs_4d = read.csv("asia_shares_extensivo_intensivo.csv")

df_hs_2d$export_share_to_usa <- df_hs_2d$export_share_to_usa*100
df_hs_2d$share_on_total_imports <- df_hs_2d$share_on_total_imports*100
df_hs_2d$export_value <- df_hs_2d$export_value/1000000
df_hs_2d$export_value_to_usa <- df_hs_2d$export_value_to_usa/1000000

df_hs_4d$export_share_to_usa <- df_hs_4d$export_share_to_usa*100
df_hs_4d$share_on_total_imports <- df_hs_4d$share_on_total_imports*100
df_hs_4d$export_value <- df_hs_4d$export_value/1000000
df_hs_4d$export_value_to_usa <- df_hs_4d$export_value_to_usa/1000000

data_intensivo = subset(df_hs_2d, year == 2023 & export_rca >=1.0)
data_extensivo = subset(df_hs_2d, year == 2023 & export_rca <1.0)

data_intensivo_4d = subset(df_hs_4d, year == 2023 & export_rca >=1.0)
data_extensivo_4d = subset(df_hs_4d, year == 2023 & export_rca <1.0)

ECI_pais = -0.292
umbral_importaciones = 50

### INTENSIVO
## Export value to USA
ggplot(data_intensivo, 
       aes(x = pci, y = share_on_total_imports, size = export_value_to_usa, fill = product_hs92_name_1d, label = product_hs92_name_2d)) +
  geom_point(alpha = .5, 
             shape = 21) +
  geom_text(nudge_x = 0.1, nudge_y = 0.1, size = 4, color = "black")  +
  scale_size_continuous(range = c(1, 16)) +
  labs(title = "Industrias del Sector Intensivo (HS2)",
       subtitle = "Importaciones de China, Vietnam, Camboya, Malasia, Indonesia (2023)",
       x = "PCI",
       y = "Razón con respecto al Total de Importaciones [%]",
       size = "Export value to USA (Million USD)",
       fill = "Cluster") +
  theme_minimal()  +
  guides(fill=guide_legend(override.aes=list(size=6))) + 
  geom_hline(yintercept=50,  color = "red", size = 1.5) + 
  geom_vline(xintercept = ECI_pais, color = "black", size=1.5)

ggsave("../GTM/hs2_export_value_to_usa_intensivo.png",dpi = 300,  width = 1167/90, height = 575/90,  bg = 'white')

## Total export value
ggplot(data_intensivo, 
       aes(x = pci, y = share_on_total_imports, size = export_value, fill = product_hs92_name_1d, label = product_hs92_name_2d)) +
  geom_point(alpha = .5, 
             shape = 21) +
  geom_text(nudge_x = 0.1, nudge_y = 0.1, size = 4, color = "black")  +
  scale_size_continuous(range = c(1, 16)) +
  labs(title = "Industrias del Sector Intensivo (HS2)",
       subtitle = "Importaciones de China, Vietnam, Camboya, Malasia, Indonesia (2023)",
       x = "PCI",
       y = "Razón con respecto al Total de Importaciones [%]",
       size = "Total export value (Million USD)",
       fill = "Cluster") +
  theme_minimal()  +
  guides(fill=guide_legend(override.aes=list(size=6))) + 
  geom_hline(yintercept=50,  color = "red", size = 1.5) + 
  geom_vline(xintercept = ECI_pais, color = "black", size=1.5)

ggsave("../GTM/hs2_export_value_total_intensivo.png",dpi = 300,  width = 1167/90, height = 575/90,  bg = 'white')


### EXTENSIVO

### PCI VS SHARE ON TOTAL IMPORTS
## Export value to USA
ggplot(data_extensivo, 
       aes(x = pci, y = share_on_total_imports, size = export_value_to_usa, fill = product_hs92_name_1d, label = product_hs92_name_2d)) +
  geom_point(alpha = .5, 
             shape = 21) +
  geom_text(nudge_x = 0.1, nudge_y = 0.1, size = 4, color = "black")  +
  scale_size_continuous(range = c(1, 16)) +
  labs(title = "Industrias del Sector Extensivo (HS2)",
       subtitle = "Importaciones de China, Vietnam, Camboya, Malasia, Indonesia (2023)",
       x = "PCI",
       y = "Razón con respecto al Total de Importaciones [%]",
       size = "Export value to USA (Million USD)",
       fill = "Cluster") +
  theme_minimal()  +
  guides(fill=guide_legend(override.aes=list(size=6))) + 
  geom_hline(yintercept=50,  color = "red", size = 1.5) + 
  geom_vline(xintercept = -0.19, color = "black", size=1.5)

ggsave("../GTM/hs2_export_value_to_usa_extensivo.png",dpi = 300,  width = 1167/90, height = 575/90,  bg = 'white')

## Total export value
ggplot(data_extensivo, 
       aes(x = pci, y = share_on_total_imports, size = export_value, fill = product_hs92_name_1d, label = product_hs92_name_2d)) +
  geom_point(alpha = .5, 
             shape = 21) +
  geom_text(nudge_x = 0.1, nudge_y = 0.1, size = 4, color = "black")  +
  scale_size_continuous(range = c(1, 16)) +
  labs(title = "Industrias del Sector Extensivo (HS2)",
       subtitle = "Importaciones de China, Vietnam, Camboya, Malasia, Indonesia (2023)",
       x = "PCI",
       y = "Razón con respecto al Total de Importaciones [%]",
       size = "Total export value (Million USD)",
       fill = "Cluster") +
  theme_minimal()  +
  guides(fill=guide_legend(override.aes=list(size=6))) + 
  geom_hline(yintercept=50,  color = "red", size = 1.5) + 
  geom_vline(xintercept = ECI_pais, color = "black", size=1.5)

ggsave("../GTM/hs2_export_value_total_extensivo.png",dpi = 300,  width = 1167/90, height = 575/90,  bg = 'white')

### Distance VS SHARE ON TOTAL IMPORTS

## Export value to USA
ggplot(data_extensivo, 
       aes(x = distance, y = share_on_total_imports, size = export_value_to_usa, fill = product_hs92_name_1d, label = product_hs92_name_2d)) +
  geom_point(alpha = .5, 
             shape = 21) +
  geom_text(nudge_x = 0.001, nudge_y = 0.1, size = 3, color = "black")  +
  scale_size_continuous(range = c(1, 16)) +
  labs(title = "Industrias del Sector Extensivo (HS2)",
       subtitle = "Importaciones de China, Vietnam, Camboya, Malasia, Indonesia (2023)",
       x = "Distance",
       y = "Razón con respecto al Total de Importaciones [%]",
       size = "Export value to USA (Million USD)",
       fill = "Cluster") +
  theme_minimal()  +
  guides(fill=guide_legend(override.aes=list(size=6))) + 
  geom_hline(yintercept=30,  color = "red", size = 1.5, alpha = 0.3) + 
  geom_vline(xintercept = 0.8, color = "black", size=1.5, alpha = 0.3)

ggsave("../GTM/hs2_export_value_to_usa_extensivo_distance.png",dpi = 300,  width = 1167/90, height = 575/90,  bg = 'white')

## Total export value
ggplot(data_extensivo, 
       aes(x = distance, y = share_on_total_imports, size = export_value, fill = product_hs92_name_1d, label = product_hs92_name_2d)) +
  geom_point(alpha = .5, 
             shape = 21) +
  geom_text(nudge_x = 0.001, nudge_y = 0.1, size = 3, color = "black")  +
  scale_size_continuous(range = c(1, 16)) +
  labs(title = "Industrias del Sector Extensivo (HS2)",
       subtitle = "Importaciones de China, Vietnam, Camboya, Malasia, Indonesia (2023)",
       x = "Distance",
       y = "Razón con respecto al Total de Importaciones [%]",
       size = "Total export value (Million USD)",
       fill = "Cluster") +
  theme_minimal()  +
  guides(fill=guide_legend(override.aes=list(size=6))) + 
  geom_hline(yintercept=30,  color = "red", size = 1.5, alpha = 0.3) + 
  geom_vline(xintercept = 0.8, color = "black", size=1.5, alpha = 0.3)

ggsave("../GTM/hs2_export_value_total_extensivo_distance.png",dpi = 300,  width = 1167/90, height = 575/90,  bg = 'white')

### INTENSIVO HS4
## Export value to USA
ggplot(data_intensivo_4d, 
       aes(x = pci, y = share_on_total_imports, size = export_value_to_usa, fill = product_hs92_name_1d)) +
  geom_point(alpha = .5, 
             shape = 21) +
  scale_size_continuous(range = c(1, 16)) +
  labs(title = "Industrias del Sector Intensivo (HS4)",
       subtitle = "Importaciones de China, Vietnam, Camboya, Malasia, Indonesia (2023)",
       x = "PCI",
       y = "Razón con respecto al Total de Importaciones [%]",
       size = "Export value to USA (Million USD)",
       fill = "Cluster") +
  theme_minimal()  +
  guides(fill=guide_legend(override.aes=list(size=6))) + 
  geom_hline(yintercept=40,  color = "red", size = 1.5) + 
  geom_vline(xintercept = ECI_pais, color = "black", size=1.5)

## Total export value
ggplot(data_intensivo_4d, 
       aes(x = pci, y = share_on_total_imports, size = export_value, fill = product_hs92_name_1d)) +
  geom_point(alpha = .5, 
             shape = 21) +
  scale_size_continuous(range = c(1, 16)) +
  labs(title = "Industrias del Sector Intensivo (HS4)",
       subtitle = "Importaciones de China, Vietnam, Camboya, Malasia, Indonesia (2023)",
       x = "PCI",
       y = "Razón con respecto al Total de Importaciones [%]",
       size = "Total export value (Million USD)",
       fill = "Cluster") +
  theme_minimal()  +
  guides(fill=guide_legend(override.aes=list(size=6))) + 
  geom_hline(yintercept=40,  color = "red", size = 1.5) + 
  geom_vline(xintercept = ECI_pais, color = "black", size=1.5)

### Etiquetamos puntos en el cuadrante de interés
labeled_df = subset(data_intensivo_4d, share_on_total_imports>=30 & pci > -0.19)

## Export value to USA
ggplot(data_intensivo_4d, 
       aes(x = pci, y = share_on_total_imports, size = export_value_to_usa, fill = product_hs92_name_1d)) +
  geom_point(alpha = .5, 
             shape = 21) +
  scale_size_continuous(range = c(1, 16)) +
  labs(title = "Industrias del Sector Intensivo (HS4)",
       subtitle = "Importaciones de China, Vietnam, Camboya, Malasia, Indonesia (2023)",
       x = "PCI",
       y = "Razón con respecto al Total de Importaciones [%]",
       size = "Export value to USA (Million USD)",
       fill = "Cluster") +
  theme_minimal()  +
  guides(fill=guide_legend(override.aes=list(size=6))) + 
  geom_hline(yintercept=30,  color = "red", size = 1.5, alpha = 0.3) + 
  geom_vline(xintercept = ECI_pais, color = "black", size=1.5, alpha = 0.3)+ 
  geom_text_repel(data = labeled_df, aes(label = product_hs92_name_4d), size = 4) 

ggsave("../GTM/hs4_intensivo_export_value_to_usa.png",dpi = 300,  width = 1167/90, height = 575/90,  bg = 'white')


## Total export value
ggplot(data_intensivo_4d, 
       aes(x = pci, y = share_on_total_imports, size = export_value, fill = product_hs92_name_1d)) +
  geom_point(alpha = .5, 
             shape = 21) +
  scale_size_continuous(range = c(1, 16)) +
  labs(title = "Industrias del Sector Intensivo (HS4)",
       subtitle = "Importaciones de China, Vietnam, Camboya, Malasia, Indonesia (2023)",
       x = "PCI",
       y = "Razón con respecto al Total de Importaciones [%]",
       size = "Total export value (Million USD)",
       fill = "Cluster") +
  theme_minimal()  +
  guides(fill=guide_legend(override.aes=list(size=6))) + 
  geom_hline(yintercept=30,  color = "red", size = 1.5, alpha = 0.3) + 
  geom_vline(xintercept = ECI_pais, color = "black", size=1.5, alpha = 0.3)+ 
  geom_text_repel(data = labeled_df, aes(label = product_hs92_name_4d), size = 4) 

ggsave("../GTM/hs4_intensivo_export_value_total.png",dpi = 300,  width = 1167/90, height = 575/90,  bg = 'white')
