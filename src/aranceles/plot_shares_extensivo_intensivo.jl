using Plots
using DataFrames
using CSV
using DataFramesMeta
using StatsPlots
using Statistics
using Plots.PlotMeasures

## Cargamos los datos
data = CSV.read("output/asia_shares_extensivo_intensivo.csv", DataFrame)

data.share_on_total_imports = data.share_on_total_imports*100

data_intensivo = data[data.year .== 2023 .&& data.tag.=="paises_interes" .&& data.export_rca .>= 1.0,:]
data_extensivo = data[data.year .== 2023 .&& data.tag.=="paises_interes" .&& data.export_rca .< 1.0,:]

#### Colores Grupos
#https://discourse.julialang.org/t/alternate-color-for-each-point-in-scatter-plot-and-add-legend/56856/11
# https://blog.djnavarro.net/posts/2024-03-03_julia-plots/

### EXTENSIVO
@df data_extensivo plot(
  :distance,
  :share_on_total_imports,
  seriestype=:scatter,
  group=:product_hs92_name_1d,
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
  #ylimits = (-10.,110.0), 
  #xlimits = (0.7, 1.0), 
  legendfontsize=14
)

@df data_extensivo scatter3d(
    :distance,
    :pci,
    :share_on_total_imports,
    group=:product_hs92_name_1d,
    title="Industrias del Sector Extensivo.\nImportaciones de China, Vietnam, Camboya, Malasia, Indonesia (2023)",
    xlabel="Distancia",
    zlabel="Razón con respecto al Total de Importaciones [%]",
    ylabel="PCI",
    size=(1000,1000),
    legend=:outerright,
    markersize=8,
    xguidefontsize=15,
    yguidefontsize=15,
    titlefontsize=15,
    tickfontsize=15,
    #ylimits = (-10.,110.0), 
    #xlimits = (0.7, 1.0), 
    legendfontsize=14
)

### Hacemos un loop para ver las tablas por nombre en un layout
extensivo_layout = []

for i in unique(data_extensivo.product_hs92_name_1d)
    extensivo_sector = @df data_extensivo[data_extensivo.product_hs92_name_1d.==i, :] plot(
        :distance,
        :share_on_total_imports,
        seriestype=:scatter,
        group=:product_hs92_name_1d,
        #title="Industrias del Sector Extensivo.\nImportaciones de China, Vietnam, Camboya, Malasia, Indonesia (2023)",
        xlabel="Distancia",
        ylabel="Porcentaje [%]",
        size=(1500,1500),
        #legend=:outerbottom,
        markersize=13,
        xguidefontsize=15,
        yguidefontsize=15,
        titlefontsize=15,
        tickfontsize=15,
        ylimits = (-10.,105.0), 
        xlimits = (0.7, 0.95), 
        legendfontsize=14
        )
    hspan!(extensivo_sector, [49.5,50.5], label= "50%", c=:red)
    vspan!(extensivo_sector, [0.798,0.802], label = "0.8", c=:black)

    push!(extensivo_layout,   
        extensivo_sector
        )
end

plot(extensivo_layout..., layout = (3,3), plot_title="Industrias del Sector Extensivo.\nImportaciones de China, Vietnam, Camboya, Malasia, Indonesia (2023)", left_margin = [20mm 0mm])

## Extensivo 3D
extensivo_3d_layout = []

for i in unique(data_extensivo.product_hs92_name_1d)
    extensivo_sector = @df data_extensivo[data_extensivo.product_hs92_name_1d.==i, :] scatter3d(
        :distance,
        :pci,
        :share_on_total_imports,
        group=:product_hs92_name_1d,
        #title="Industrias del Sector Extensivo.\nImportaciones de China, Vietnam, Camboya, Malasia, Indonesia (2023)",
        xlabel="Distancia",
        zlabel="Porcentaje [%]",
        ylabel="PCI",
        size=(1200,1200),
        markersize=6,
        xguidefontsize=10,
        yguidefontsize=10,
        titlefontsize=10,
        tickfontsize=10,
        zlimits = (-10.,110.0), 
        xlimits = (0.7, 1.0),
        ylimits = (-2,2),
        legendfontsize=14
    )
    push!(extensivo_3d_layout,   
        extensivo_sector
        )
end

plot(extensivo_3d_layout..., layout = (3,3), plot_title="Industrias del Sector Extensivo.\nImportaciones de China, Vietnam, Camboya, Malasia, Indonesia (2023)", left_margin = [20mm 0mm])

### INTENSIVO
@df data_intensivo plot(
  :pci,
  :share_on_total_imports,
  seriestype=:scatter,
  group=:product_hs92_name_1d,
  title="Industrias del Sector Intensivo.\nImportaciones de China, Vietnam, Camboya, Malasia, Indonesia (2023)",
  xlabel="PCI",
  ylabel="Razón con respecto al Total de Importaciones [%]",
  size=(1000,1000),
  legend=:outerbottom,
  markersize=13,
  xguidefontsize=15,
  yguidefontsize=15,
  titlefontsize=15,
  tickfontsize=15,
  #ylimits = (-10.,110.0), 
  #xlimits = (0.7, 1.0), 
  legendfontsize=14
)
#hspan!([49.5,50.5], label= "50%", c=:red)
#vspan!([-0.02,0.02], label = "PCI=0", c=:black)
vspan!([-0.092, -0.072 ]; alpha = 0.5, label = "ECI SLV", c = :red)


### Hacemos un loop para ver las tablas por nombre en un layout
intensivo_layout = []

for i in unique(data_intensivo.product_hs92_name_1d)
    intensivo_sector = @df data_intensivo[data_intensivo.product_hs92_name_1d.==i, :] plot(
        :pci,
        :share_on_total_imports,
        seriestype=:scatter,
        group=:product_hs92_name_1d,
        xlabel="PCI",
        ylabel="Porcentaje [%]",
        size=(1300,1300),
        markersize=13,
        xguidefontsize=15,
        yguidefontsize=15,
        titlefontsize=15,
        tickfontsize=15,
        ylimits = (-10.,110.0), 
        xlimits = (-2.0, 2.0), 
        legendfontsize=14
        )
    #hline!(intensivo_sector, [50], legend =false)
    #vline!(intensivo_sector, [0], label = "PCI = 0.0")
    hspan!(intensivo_sector, [49.5,50.5], label= "50%", c=:red)
    vspan!(intensivo_sector, [-0.02,0.02], label = "PCI=0", c=:black)
    push!(intensivo_layout,
        intensivo_sector
    )
end

plot(intensivo_layout..., layout = (3,3), plot_title="Industrias del Sector Intensivo.\nImportaciones de China, Vietnam, Camboya, Malasia, Indonesia (2023)", left_margin = [20mm 0mm])
