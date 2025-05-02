using Plots
using DataFrames
using CSV
using DataFramesMeta
using StatsPlots
using Statistics

## Cargamos los datos
data = CSV.read("INTENSIVO_paises_asia_hs_data.csv", DataFrame)


data.share_on_total_imports = data.share_on_total_imports*100

data_plot = data[data.year .== 2023 .&& data.tag.=="paises_interes",:]

x,y = data_plot[:,"2023"], data_plot.share_on_total_imports

dy = diff([extrema(y)...])[1]/20  # adjust offset if needed

scatter(x,y, ms=7, 
        legend=false, 
        ylimits = (-1.5,70.0), 
        xlimits = (-0.05, 1.7), 
        xlabel = "PCI",
        ylabel = "Razón con respecto al Total de Importaciones [%]",
        xguidefontsize=10,
        yguidefontsize=9,
        titlefontsize=8,
        title = "Industrias del Sector Intensivo.\nImportaciones provenientes de China, Vietnam, Camboya, Malasia, Indonesia (2023)",
        dpi=1000
        )

[annotate!(x, y+dy, Plots.text(string(i), 4)) for (i,x, y) in zip(data_plot.HS4,x,y)];
plot!()