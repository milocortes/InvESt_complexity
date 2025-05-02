using Plots
using DataFrames
using CSV
using DataFramesMeta
using StatsPlots
using Statistics

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
        title = "Industrias del Sector Extensivo.\nImportaciones provenientes de China, Vietnam, Camboya, Malasia, Indonesia (2023)",
        dpi=1000
        )
[annotate!(x, y+dy, Plots.text(string(i), 4)) for (i,x, y) in zip(data_plot.ciiu_nombre,x,y)];
plot!()
#savefig("importaciones_usa_sectores_slv.png") 


#### Colores Grupos
#https://discourse.julialang.org/t/alternate-color-for-each-point-in-scatter-plot-and-add-legend/56856/11
# https://blog.djnavarro.net/posts/2024-03-03_julia-plots/

@df data_plot plot(
  :distance,
  :share_on_total_imports,
  seriestype=:scatter,
  group=:division,
  title="Industrias del Sector Extensivo.\nImportaciones de China, Vietnam, Camboya, Malasia, Indonesia (2023)",
  xlabel="Distancia",
  ylabel="Razón con respecto al Total de Importaciones [%]",
  size=(1000,1000),
  legend=:outerbottom,
  markersize=13,
  xguidefontsize=15,
  yguidefontsize=15,
  titlefontsize=15,
  tickfontsize=15,
  ylimits = (-10.,80.0), 
  xlimits = (0.7, 1.1), 
  legendfontsize=14
)

[annotate!(x, y+dy, Plots.text(string(i), 9)) for (i,x, y) in zip(data_plot.division,x,y)];
plot!()

combine(groupby(data_plot, :division), :share_on_total_imports => mean)
sort(combine(groupby(data_plot, :division), :share_on_total_imports => mean), :share_on_total_imports_mean, rev=true)


share_imports_mean = data_plot |> 
  d -> subset(d, :share_on_total_imports => b -> .!ismissing.(b)) |>
  d -> select(d, [:division, :share_on_total_imports])

@df share_imports_mean plot(
        string.(:division),
        :share_on_total_imports,
        seriestype=:violin,
        legend=false,
        xlabel="Species",
        ylabel="Bill Length (mm)",
        size=(500,500)
)
