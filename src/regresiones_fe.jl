using DataFrames, CSV, FixedEffectModels, GLM, RegressionTables

complexity_zm = DataFrame(CSV.File("/home/milo/Documents/egap/iniciativas/desarrollo-regional/el_salvador/datos/src/regresiones_crecimiento.csv"))

todo = 
norte = reg(df[isless.(df.rca_2014, 0.5) .& (df.region .=="norte"),:], @formula(apariciones ~ density_2014 + ied_2010 + rca_eigenvector + fe(edo) + fe(actividad)), Vcov.cluster(:edo, :actividad))
centro_norte = reg(df[isless.(df.rca_2014, 0.5) .& (df.region .=="centro_norte"),:], @formula(apariciones ~ density_2014 + ied_2010 + rca_eigenvector + fe(edo) + fe(actividad)), Vcov.cluster(:edo, :actividad))
centro = reg(df[isless.(df.rca_2014, 0.5) .& (df.region .=="centro"),:], @formula(apariciones ~ density_2014 + ied_2010 + rca_eigenvector + fe(edo) + fe(actividad)), Vcov.cluster(:edo, :actividad))
sur = reg(df[isless.(df.rca_2014, 0.5) .& (df.region .=="sur"),:], @formula(apariciones ~ density_2014 + ied_2010 + rca_eigenvector + fe(edo) + fe(actividad)), Vcov.cluster(:edo, :actividad))

growth_rca_log = reg(complexity_zm, @formula(growth_rca_log ~ arcsinh_density + arcsinh_rca  + arcsinh_output_presence+ arcsinh_input_presence + arcsinh_coempleo_presence_continua + fe(edo) + fe(actividad)), Vcov.cluster(:edo, :actividad))

felm(, data = NaRV.omit(complexity_zm[, c("growth_rca_log", "arcsinh_density", "arcsinh_rca", "arcsinh_output_presence", "arcsinh_input_presence", "arcsinh_coempleo_presence_continua", "edo", "actividad")]), cmethod = 'cgm2', exactDOF=TRUE)
growth_rca_arcsinh = felm(growth_rca_arcsinh ~ arcsinh_density  + arcsinh_rca + arcsinh_output_presence+ arcsinh_input_presence + arcsinh_coempleo_presence_continua| edo + actividad, data = NaRV.omit(complexity_zm[, c("growth_rca_arcsinh", "arcsinh_density", "arcsinh_rca", "arcsinh_output_presence", "arcsinh_input_presence", "arcsinh_coempleo_presence_continua", "edo", "actividad")]), cmethod = 'cgm2', exactDOF=TRUE)
apariciones = felm(apariciones ~ arcsinh_density  + arcsinh_rca + arcsinh_output_presence+ arcsinh_input_presence + arcsinh_coempleo_presence_continua| edo + actividad, data = NaRV.omit(subset(complexity_zm[, c("apariciones", "arcsinh_density", "arcsinh_rca", "arcsinh_output_presence", "arcsinh_input_presence", "arcsinh_coempleo_presence_continua", "edo", "actividad", "rca_2015")], rca_2015 < 0.05)), cmethod = 'cgm2', exactDOF=TRUE)
desapariciones = felm(desapariciones ~ arcsinh_density  + arcsinh_rca + arcsinh_output_presence+ arcsinh_input_presence + arcsinh_coempleo_presence_continua| edo + actividad, data = NaRV.omit(subset(complexity_zm[, c("desapariciones", "arcsinh_density", "arcsinh_rca", "arcsinh_output_presence", "arcsinh_input_presence", "arcsinh_coempleo_presence_continua", "edo", "actividad", "rca_2015")], rca_2015 > 0.2)), cmethod = 'cgm2', exactDOF=TRUE)


stargazer(growth_rca_log, growth_rca_arcsinh, apariciones, desapariciones, 
          type="text", 
          title = "Regresiones (2019-2013)")



regtable(
    todo,todo_bin, norte, norte_bin, centro_norte, centro_norte_bin, centro, centro_bin, sur, sur_bin;
    groups = ["Región:", "Todo" => 2:3, "Norte" => 4:5, "Centro-Norte" => 6:7, "Centro" => 8:9, "Sur" => 10:11],
    render = AsciiTable(),
    labels = Dict(
        "versicolor" => "Versicolor",
        "virginica" => "Virginica",
        "PetalLength" => "Petal Length",
    ),
    regression_statistics = [
        Nobs => "Obs.",
        R2,
        R2Within,
        PseudoR2 => "Pseudo-R2",
    ]
)