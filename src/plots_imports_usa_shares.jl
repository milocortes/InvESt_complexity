using Plots
using DataFrames
using CSV
using DataFramesMeta

## Cargamos los datos
data = CSV.read("paises_asia_ciiu_complete_hs_data.csv", DataFrame)

data.share_on_total_imports = data.share_on_total_imports*100

data_plot = data[data.year .== 2023 .&& data.tag.=="paises_interes",:]

x,y = data_plot.distance, data_plot.share_on_total_imports

dy = diff([extrema(y)...])[1]/20  # adjust offset if needed
scatter(x,y, ms=7, 
        legend=false, 
        ylimits = (-10.,80.0), 
        xlimits = (0.65, 1.1), 
        xlabel = "Distancia",
        ylabel = "Razón con respecto al Total de Importaciones [%]",
        xguidefontsize=10,
        yguidefontsize=9,
        titlefontsize=8,
        title = "Industrias del Sector Extensivo (2023).\nImportaciones provenientes de China, Vietnam, Camboya, Malasia, Indonesia"
        )
[annotate!(x, y+dy, Plots.text(string(i), 4)) for (i,x, y) in zip(data_plot.ciiu_nombre,x,y)];
plot!()
