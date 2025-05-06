using Plots
using DataFrames
using CSV
using DataFramesMeta
using StatsPlots
using Statistics
using Plots.PlotMeasures

## Cargamos los datos
data = CSV.read("output/hs2_asia_shares_extensivo_intensivo.csv", DataFrame)

data.share_on_total_imports = data.share_on_total_imports*100

data_intensivo = data[data.year .== 2023  .&& data.export_rca .>= 1.0,:]
data_extensivo = data[data.year .== 2023 .&& data.export_rca .< 1.0,:]



### INTENSIVO
#### Export values
@df data_intensivo Plots.plot(
  :pci,
  :share_on_total_imports,
  seriestype=:scatter,
  group=:product_hs92_name_1d,
  title="Industrias del Sector Intensivo.\nImportaciones de China, Vietnam, Camboya, Malasia, Indonesia (2023)",
  xlabel="PCI",
  ylabel="Razón con respecto al Total de Importaciones [%]",
  size=(1000,1000),
  legend=:outerbottom,
  markersize=:export_value/10_000_000,
  xguidefontsize=15,
  yguidefontsize=15,
  titlefontsize=15,
  tickfontsize=15,
  ylimits = (-10.,110.0), 
  xlimits = (-2, 2), 
  legendfontsize=20
)
hspan!([49.5,50.5], label= "50%", c=:red)
#vspan!([-0.02,0.02], label = "PCI=0", c=:black)
vspan!([-0.092, -0.072 ]; alpha = 0.5, label = "ECI SLV", c = :black)

z = data_intensivo.product_hs92_name_2d
x = data_intensivo.pci
y = data_intensivo.share_on_total_imports
dy = diff([extrema(y)...])[1]/20  # adjust offset if needed

[annotate!(x, y+dy, Plots.text(string(i), 8)) for (i,x, y) in zip(z,x,y)];
plot!()

#### Export share to USA
@df data_intensivo Plots.plot(
  :pci,
  :share_on_total_imports,
  seriestype=:scatter,
  group=:product_hs92_name_1d,
  title="Industrias del Sector Intensivo.\nImportaciones de China, Vietnam, Camboya, Malasia, Indonesia (2023)",
  xlabel="PCI",
  ylabel="Razón con respecto al Total de Importaciones [%]",
  size=(1000,1000),
  legend=:outerbottom,
  markersize=:export_share_to_usa*100,
  xguidefontsize=15,
  yguidefontsize=15,
  titlefontsize=15,
  tickfontsize=15,
  ylimits = (-10.,110.0), 
  xlimits = (-2, 2), 
  legendfontsize=20
)
hspan!([49.5,50.5], label= "50%", c=:red)
#vspan!([-0.02,0.02], label = "PCI=0", c=:black)
vspan!([-0.092, -0.072 ]; alpha = 0.5, label = "ECI SLV", c = :black)

z = data_intensivo.product_hs92_name_2d
x = data_intensivo.pci
y = data_intensivo.share_on_total_imports
dy = diff([extrema(y)...])[1]/20  # adjust offset if needed

[annotate!(x, y+dy, Plots.text(string(i), 8)) for (i,x, y) in zip(z,x,y)];
plot!()


#### Probemos 3D

@df data_intensivo scatter3d(
    :export_share_to_usa*100,
    :pci,
    :share_on_total_imports,
    group=:product_hs92_name_1d,
    title="Industrias del Sector Extensivo.\nImportaciones de China, Vietnam, Camboya, Malasia, Indonesia (2023)",
    xlabel="Exportaciones a USA [%]",
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

nombres = data_intensivo.product_hs92_name_2d
pci = data_intensivo.pci
shares_asia = data_intensivo.share_on_total_imports
shares_usa = data_intensivo.export_share_to_usa*100

dz = diff([extrema(shares_asia)...])[1]/20  # adjust offset if needed


[annotate!(x, y,  z+dz, Plots.text(string(i), 8)) for (i,x, y,z) in zip(nombres, shares_usa, pci, shares_asia)];
plot!()

points = Point2f.(data_intensivo.pci, data_intensivo.share_on_total_imports)

CairoMakie.scatter(points, color = 1:30, markersize = data_intensivo.export_value/10_000_000)