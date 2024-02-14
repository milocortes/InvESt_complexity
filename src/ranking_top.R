# install.packages("tidyverse")
# install.packages("ggbump")
library(tidyverse)
library(ggbump)


year <- rep(2019:2021, 4)
position <- c(4, 2, 2, 3, 1, 4, 2, 3, 1, 1, 4, 3)
player <- c("A", "A", "A",
            "B", "B", "B", 
            "C", "C", "C",
            "D", "D", "D")

df <- data.frame(x = year,
                 y = position,
                 group = player)

ggplot(df, aes(x = x, y = y, color = group)) +
  geom_bump(size = 1.5) +
  geom_point(size = 6) +
  geom_text(data = df %>% filter(x == min(x)),
            aes(x = x - 0.1, label = group),
            size = 5, hjust = 1) +
  geom_text(data = df %>% filter(x == max(x)),
            aes(x = x + 0.1, label = group),
            size = 5, hjust = 0) +
  scale_color_brewer(palette = "RdBu") +
  theme_void() +
  theme(legend.position = "none") 


setwd("/home/milo/Documents/egap/iniciativas/desarrollo-regional/el_salvador/datos/src")

ranking <- read.csv("zm_complexity_ranking.csv")

ggplot(ranking, aes(x = anio, y = ranking, color = unidad)) +
  geom_bump(size = 1.5) +
  geom_point(size = 6) +
  geom_text(data = ranking %>% filter(anio == max(anio)),
            aes(x = anio - 0.1, label = unidad),
            size = 5, hjust = 1) +
  geom_text(data = ranking %>% filter(anio == min(anio)),
            aes(x = anio + 0.1, label = unidad),
            size = 5, hjust = 0) +
  scale_color_brewer(palette = "RdBu") +
  theme_void() +
  theme(legend.position = "none") 


todo_complexity <- read.csv("complexity_todo_metricas.csv")
todo_complexity_2021 <- subset(todo_complexity, anio==2021 & zm=='SLV' & (cog>0 & distance>0.5))

library(ggplot2)
p <- ggplot(todo_complexity_2021, aes(x=distance, y=cog, color=pci)) +
  geom_point() + 
  geom_text(aes(label=ciiu_nombre), size=3.4, vjust = 1.5)+
  xlim(0.35, 1.0)+
  labs(
  title = "Opportunity Gain vs Distance. El Salvador. 2021",
  size = 4
  )+
  xlab("Distance")+
  ylab("Opportunity Gain")+
  theme_classic()


#######################################
library(ggplot2)

ranking_extensivo <- read.csv("/home/milo/Documents/egap/iniciativas/desarrollo-regional/el_salvador/datos/src/extensivo_multicriterio_ranking_sectores.csv")

ggplot(ranking_extensivo, aes(x=distance, y=cog, color=ciiu_seccion, size=rca )) + 
    geom_point()+ scale_color_brewer(palette="Set3")